import sys
sys.path.append('./test_deploy')

import axiom.read2 as reader
import axiom.plot_func as pl_f
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
#import kmeans1d as km1d
import numpy as np
from flask import Flask, render_template, request
import json
import plotly
import plotly.express as px
import plotly.graph_objects as go

list_df = []
df0 = pd.read_csv('df0.csv')
df0 = df0.iloc[: , 1:]
df1 = pd.read_csv('df1.csv')
df1 = df1.iloc[: , 1:]
df2 = pd.read_csv('df2.csv')
df2 = df2.iloc[: , 1:]
df3 = pd.read_csv('df3.csv')
df3 = df3.iloc[: , 1:]
df4 = pd.read_csv('df4.csv')
df4 = df4.iloc[: , 1:]
df5 = pd.read_csv('df5.csv')
df5 = df5.iloc[: , 1:]

list_df.append(df0)
list_df.append(df1)
list_df.append(df2)
list_df.append(df3)
list_df.append(df4)
list_df.append(df5)

file_list = list_df[0]["filepath"]
new_file_list = [i.replace('./test_data2/','') for i in file_list]
new_file_list2 = [i.replace('.xls','') for i in new_file_list]
new_file_list2 = list(set(new_file_list2))
new_file_list2.sort()
new_file_list2.insert(0,'none')
new_file_list2

date_list = list_df[0]["datetime"]
date_list = list(set(date_list))
date_list.sort()
date_list.insert(0,'none')
date_list


unwanted_names = {'machine_id', 'order', 'datetime', 'filepath', 'group_id', 'Shot rate'}
group_id = 1
#s1 = str(len(list_df))
s1 = 6
#s2 = str(file_count)
s2 = 1186
#s3 = str(rows)
s3 = 41616
#todo: print list
s4 = str(list_df[0].shape)

#colours = list_df[0].columns
num_list= []
for i in range(len(list_df)):
    num_list.append(i+1)
group_list = num_list

col_1 = list_df[0].columns
col_2 = new_file_list2
col_3 = date_list

app = Flask(__name__)

@app.route('/callback', methods=['POST', 'GET'])
def cb():
    return gm(request.args.get('data'), request.args.get('dataa'), request.args.get('datab'))

@app.route('/callback2', methods=['POST', 'GET'])
def cb2():
    return gm2(request.args.get('data2'), request.args.get('data3'), request.args.get('data11'))

@app.route('/callback3', methods=['POST', 'GET'])
def cb3():
    return gm3(request.args.get('data4'))
#return gm3(request.args.get('data4'))

@app.route('/callback4', methods=['POST', 'GET'])
def cb4():
    return gm4(request.args.get('data5'), request.args.get('data6'), request.args.get('data7'), request.args.get('data12'))

@app.route('/callback5', methods=['POST', 'GET'])
def cb5():
    return gm5(request.args.get('data8'), request.args.get('data10'), request.args.get('data13'))

@app.route('/callback6', methods=['POST', 'GET'])
def cb6():
    return gm6(request.args.get('data9'), request.args.get('data14'))

@app.route('/')
def index():
    return render_template('test2e11d5.html', str1 = s1, str2 = s2, str3 = s3, str4 = s4,  graphJSON=gm(), graphJSON2=gm2(), graphJSON3=gm3(), graphJSON4=gm4(), graphJSON5=gm5(), graphJSON6=gm6(), group_list=group_list, col_1=col_1, col_2=col_2, col_3=col_3)

# summary table
def gm(g_id='1', g_date='2021-08-18 21:41:33', g_date2='2022-02-25 02:25:33'):
    
    group_id = int(g_id)
    
    if g_date == 'none':
        df = pl_f.print_table(list_df[group_id-1], unwanted_names).round(2)
    else:
        df3 = list_df[group_id-1]
        sorted_df3 = df3.sort_values(by="datetime", ignore_index=True)
        list_x = sorted_df3.index[sorted_df3['datetime']==g_date].tolist()
        list_y = sorted_df3.index[sorted_df3['datetime']==g_date2].tolist()
        new_df = sorted_df3.iloc[list_x[0]:list_y[0], 0:18]
        
        df = pl_f.print_table(new_df, unwanted_names).round(2)

    
    df = df.T
    df['Statistics'] = df.index
    cols = list(df.columns)
    cols = [cols[-1]] + cols[:-1]
    df = df[cols]
    fig = go.Figure(data=[go.Table(
        header=dict(values=list(df.columns),
                    fill_color='paleturquoise',
                    align='left'), 
        cells=dict(values=df.transpose().values.tolist(), 
                   fill_color='lavender',
                   align='left'))])
    
    
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

# 2 stream visualization
def gm2(data_x='008.Filling  time [s]', data_y='009. Plasticizing  time [s]', g_id3='1'):
    
    group_id = int(g_id3)
    df2 = list_df[group_id-1]
    
    fig2 = px.scatter(df2, x=data_x, y=data_y)

    graphJSON2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON2

# Correlation Heatmap
def gm3(g_id2='1'):
    group_id = int(g_id2)
    unwanted_names = {'machine_id', 'order', 'datetime', 'filepath', 'group_id', 'Shot rate'}
    df = pl_f.drop_col(list_df[group_id-1], unwanted_names)
    
    fig3 = px.imshow(df.corr(), aspect = "auto")

    graphJSON3 = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON3

# 3 stream visualization
def gm4(data_x2='008.Filling  time [s]', data_y2='009. Plasticizing  time [s]', data_z2= '000.Total  cycle time  [s]', g_id4='1'):
    
    group_id = int(g_id4)
    df2 = list_df[group_id-1]
    
    fig4 = px.scatter(df2, x=data_x2, y=data_y2, color =data_z2 )

    graphJSON4 = json.dumps(fig4, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON4

# Filtering
def gm5(file='imm1_100_5', date='2021-08-18 21:41:33', g_id5='1'):
    
    group_id = int(g_id5)
    
    if file == 'none':
        df = pl_f.print_rows_date(list_df[group_id-1], date)
    elif date == 'none':
        df = pl_f.print_rows_file(list_df[group_id-1], file)
    else:
        df = pl_f.print_rows_file_date(list_df[group_id-1], date, file)
    
    
    #df = pl_f.print_rows_file(list_df[0], file)
    fig5 = go.Figure(data=[go.Table(
        header=dict(values=list(df.columns),
                    fill_color='red',
                    align='left'), 
        cells=dict(values=df.transpose().values.tolist(), 
                   fill_color='lavender',
                   align='left'))])
    
    graphJSON5 = json.dumps(fig5, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON5

# single stream visualization (sorted by datetime)
def gm6(data_x3='008.Filling  time [s]', g_id6='1'):
    
    group_id = int(g_id6)
    df3 = list_df[group_id-1]
    sorted_df3 = df3.sort_values(by="datetime")
    fig6 = px.scatter(sorted_df3[data_x3])
    #fig6 = px.line(sorted_df3[data_x3])
    
    graphJSON6 = json.dumps(fig6, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON6


if __name__ == '__main__':
    app.run(host='0.0.0.0')
