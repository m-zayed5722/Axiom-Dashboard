import pandas as pd
import os
import xlrd
import logging
import datetime
import hashlib
import pathlib
import datetime
import json
import sqlalchemy

def get_logger(name):
    l = logging.getLogger(name)
    if not l.hasHandlers():
        c = logging.StreamHandler()
        l.addHandler(c)
        l.setLevel(logging.INFO)
    return l

def read_header(sheet, loglevel=logging.INFO):
    """
    Reads header info from data file version 1.0.  The date file has the following layout.
    
    Row1: Machine ID [Col A]
    Row2: Order [Col A], Date/time [Col E]
    Row3: Values [Col A through Col M, see list below]
    
    Shot rate
    008.Filling  time [s]
    009. Plasticizing  time [s]
    000.Total  cycle time  [s]
    012.Min.melt  cushion [in]
    015.Peak  value Inj.  Pressure  [psi]
    016. Change- over Inj.  Pressure  [psi]
    003. Clamping  force [shtn]
    018. Change- over Melt  pressure  [psi]
    051.Shot  vol. before  injection [in]
    092.Peak  value  Holding  pressure  [psi]
    100.Melt  temperature  [F]
    111.Cooling  time [s]
    
    This functions returns ID, Order, and Date Time.  It also confirms that the Row3 
    matches the list above.
    """
    col_names = [
        'Shot rate',
        '008.Filling  time [s]',
        '009. Plasticizing  time [s]',
        '000.Total  cycle time  [s]',
        '012.Min.melt  cushion [in]',
        '015.Peak  value Inj.  Pressure  [psi]',
        '016. Change- over Inj.  Pressure  [psi]',
        '003. Clamping  force [shtn]',
        '018. Change- over Melt  pressure  [psi]',
        '051.Shot  vol. before  injection [in]',
        '092.Peak  value  Holding  pressure  [psi]',
        '100.Melt  temperature  [F]',
        '111.Cooling  time [s]']
    
    logger = get_logger('axiom_header_read')
    logger.setLevel(loglevel)
    
    machine_id = sheet.cell(0,0).value
    logger.debug(f'machine id = {machine_id}')
    if not machine_id:
        logger.warning(f'machine id not found')

    order = sheet.cell(1,0).value
    logger.debug(f'order = {order}')
    if not order:
        logger.warning(f'order not found')
    
    date_time_raw = sheet.cell(1,4).value
    date_time = datetime.datetime.strptime(date_time_raw, '%d.%m.%Y %H:%M:%S')
    if not date_time_raw:
        logger.warning(f'date_time_raw')
    logger.debug(f'data/time = {date_time}')
    
    for i in range(sheet.ncols):
        if sheet.cell(2,i).value != col_names[i]:
            logger.warning(f'Missing {col_names[i]}')
            
    return {
        'machine_id': machine_id,
        'order': order,
        'datetime': date_time
    }

def read_column_names(sheet, loglevel=logging.INFO):
    row_number = 2
    names = []
    for i in range(sheet.ncols):
        names.append(sheet.cell(row_number, i).value)
    
    return sorted(names)

def read_data(filepath, loglevel=logging.INFO):
    logger = get_logger('axiom_data_read')
    logger.setLevel(loglevel)
    
    logger.info(f'Reading file{filepath}')
    wb = xlrd.open_workbook(filepath)
    
    num_sheets = len(wb.sheet_names())
    if num_sheets > 1:
        logger.warning(f'Found more than 1 sheet.  Only reading first sheet. [{filepath}]')
    
    sh = wb.sheet_by_index(0)    
    header = read_header(sh, loglevel)
    column_names = read_column_names(sh, loglevel)
    
    df = pd.read_excel(wb, header=2, usecols='A:M')
    last_row = df.shape[0]
    if df.iloc[last_row-1,0] == '#':
        logger.debug(f'Bad last row found. Dropping last row. [{filepath}]')
        df = df[:-1]

    for k in header.keys():
        df[k] = header[k]
    df['filepath'] = filepath
        
    logger.info(f'Read {df.shape[0]} rows.')

    return df

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def find_data_files(dirpath):
    data_files = []
    for (dirpath, dirnames, filenames) in os.walk(dirpath):
        for filename in filenames:
            if os.path.splitext(filename)[1] in ['.xls']:
                filepath = os.path.join(dirpath, filename)
                f = pathlib.Path(filepath)
                data_files.append(
                    { 'filepath': filepath, 
                      'filename': filename,
                      'hash': md5(filepath),
                      'mtime': f.stat().st_mtime_ns,
                      'size': f.stat().st_size }
                )
    return data_files

def read_data_files(data_files, file_db, data_folder, loglevel=logging.INFO):
    logger = get_logger('axiom_header_read')
    logger.setLevel(loglevel)

    file_count = 0
    shape_count = 0
    #df = pd.DataFrame()
    list_df = []
    for file in data_files:
        if file_db.has_consumed(file):
            logger.info(f'File {file["filepath"]} already used.')
        else:            
            df_tmp = read_data(file['filepath'], loglevel=logging.ERROR)
            if df_tmp.shape[0] > 0:
                file_count += 1
                file_db.add_file(file, data_folder)
            
                if len(list_df) == 0:
                    df_tmp['group_id'] = 1
                    list_df.append(df_tmp)
                    #df = df_tmp
                else:
                    #--------------------------------------------------------
                    flag = 0
                    df_new = df_tmp
                    for i in range(len(list_df)):
                        df_new['group_id'] = 1
                        if(len(list_df[i].columns)==len(df_new.columns)):
                            #print("checking if they have same col")
                            if((list_df[i].columns==df_new.columns).all()):
                                #print("same col, adding to existing group")
                                df_new['group_id'] = list_df[i]['group_id'][0]
                                list_df[i] = list_df[i].append(df_new, ignore_index=True)
                                flag = 1
                                break
                            else:
                                #print("diff col: checking if same sorted col")
                                if((list_df[i].columns.sort_values()==df_new.columns.sort_values()).all()):
                                    #print("same sorted col: adding to existing group")
                                    #reindex then add
                                    df_new['group_id'] = list_df[i]['group_id'][0]
                                    df_new = df_new.reindex(columns=list_df[i].columns)
                                    list_df[i] = list_df[i].append(df_new, ignore_index=True)
                                    flag = 1
                                    break
                    if (flag == 0):
                        #print("creating new group")
                        df_new['group_id'] = len(list_df)+1
                        list_df.append(df_new)
                    #----------------------------------------------------
                    #df = df.append(df_tmp, ignore_index=True)
                    shape_count = shape_count + df_tmp.shape[0]
                
    logger.info(f'{shape_count} rows read from {file_count} files.')
    return list_df, file_count, shape_count

"""
def read_data_files(data_files, file_db, data_folder, loglevel=logging.INFO):
    logger = get_logger('axiom_header_read')
    logger.setLevel(loglevel)

    file_count = 0
    df = pd.DataFrame()
    for file in data_files:
        if file_db.has_consumed(file):
            logger.info(f'File {file["filepath"]} already used.')
        else:            
            df_tmp = read_data(file['filepath'], loglevel=logging.ERROR)
            if df_tmp.shape[0] > 0:
                file_count += 1
                file_db.add_file(file, data_folder)
            
                if df.shape[0] == 0:
                    df = df_tmp
                else:
                    df = df.append(df_tmp, ignore_index=True) 
                
    logger.info(f'{df.shape[0]} rows read from {file_count} files.')
    return df, file_count, df.shape[0]
"""

def store_df(df, h5file, loglevel=logging.INFO):
    logger = get_logger('axiom_header_read')

    session_id = datetime.datetime.now().strftime("d%Y_%m_%d_%H%M%S")
    logger.info('Saving as {session_id}')
    try:
        df.to_hdf(h5file, session_id)
        return True
    except:
        logger.error(f'Cannot save dataframe with {df.shape[0]} rows to h5file')
        return False

class DataFiles:
    """
    A class to keep track of which data files have been consumed.
    """
    
    def __init__(self, dbinfo, echo=False):
        self.db_engine, self.Files, self.DataStreams, self.session = self.setup_db(dbinfo, echo)
        self.logger = get_logger('axiom_data_read')

    def setup_db(self, dbinfo, echo):
        # Create engine
        from sqlalchemy import create_engine
        db_engine = create_engine(dbinfo, echo = echo)

        # Create schema
        from sqlalchemy import Column, Integer, String
        from sqlalchemy.ext.declarative import declarative_base
        Base = declarative_base()
        
        class Files(Base):
            __tablename__ = 'files'
            
            hash = Column(String, primary_key = True)
            name = Column(String)
            mtime = Column(Integer)
            size = Column(Integer)
            path = Column(Integer)
            streams_id = Column(Integer)

        class DataStreams(Base):
            __tablename__ = 'streams'
            
            id = Column(Integer, primary_key = True, autoincrement=True)
            column_names = Column(String)
            
        Base.metadata.create_all(db_engine)

        # Create a session that will use to communicate with
        # the database.
        from sqlalchemy.orm import sessionmaker
        Session = sessionmaker(bind = db_engine)
        session = Session()

        return db_engine, Files, DataStreams, session  

    def find_similar_streams(self, column_names):
        """
        column_names = list of column names
        """
        cn = json.dumps(column_names)
        
        found = self.session.query(self.DataStreams).filter(self.DataStreams.column_names == cn)
        if found.count() > 0:
            return True, found[0].id 
        else:
            streams = self.DataStreams(column_names = cn)
            self.session.add(streams)
            self.session.commit()
            
            found = self.session.query(self.DataStreams).filter(self.DataStreams.column_names == cn)
            return False, found[0].id
        
        assert(False)
        
    def has_consumed(self, data_file):
        found = self.session.query(self.Files).filter(self.Files.hash == data_file['hash'])
        if found.count() > 0:
            return True
        return False

    def add_file(self, data_file, data_folder='.'):
        if self.has_consumed(data_file):
            self.logger.info(f'File {data_file["filename"]} already exists in database. Nothing more to do.')
            return False

        self.logger.info(f'Adding {data_file["filename"]}')
        file = self.Files(hash = data_file['hash'], 
                          name = data_file['filename'],
                          path = os.path.dirname(os.path.relpath(data_file['filepath'], data_folder)), 
                          mtime = data_file['mtime'], 
                          size = data_file['size'])
        self.session.add(file)

        try:
            self.session.commit()
            return True
        except:
            self.logger.error(f'Error adding file {data_file["filename"]}')
            self.session.rollback()
            return False

        assert(False)

    def get_files(self):
        return self.session.query(self.Files).all()