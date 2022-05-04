import pandas as pd
import os
import xlrd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import plotly.express as px 
import kmeans1d as km1d


#
def print_list_col(list_df_col, list_n):
    for i in range(len(list_df_col)):
        if list_df_col[i].name in list_n:
            gfg = list_df_col[i]
            print(list_df_col[i].name)
            print('Variance = ' + str(list_df_col[i].var()))
            print('Mean = ' + str(list_df_col[i].mean()))
            print('Std = ' + str(list_df_col[i].std()))
            gfg.plot()
            plt.show()

#
def get_ind_list(col_str, lst):
    for i in range(len(lst)):
        if (col_str == lst[i].name):
            return i

#
def get_list_names(lst):
    tmp_list = []
    for i in range(len(lst)):
        tmp_list.append(lst[i].name)
    return tmp_list

#
def get_set_col(lst_df):
    list_col=[]
    for i in range(len(lst_df)):
        for j in range(len(lst_df[i].columns)):
            list_col.append((lst_df[i].columns)[j])
    uni_list_col= set(list_col)
    return uni_list_col

#
def get_list_col(lst_df):
    list_df_col = []
    uni_list_col = get_set_col(lst_df)
    for i in uni_list_col:
        for j in range(len(lst_df)):
            if i in lst_df[j].columns:
                # add to existing col
                if i in get_list_names(list_df_col):
                    k = get_ind_list(i, list_df_col)
                    list_df_col[k]= list_df_col[k].append(lst_df[j][i], ignore_index=True)
                else:
                    #if col doesnt exit, listdfcol append(add new col)
                    list_df_col.append(lst_df[j][i])
    return list_df_col

# takes df along with list of col to drop, returns updated df
def drop_col(df, list_col):
    tmp_df = df
    for i in list_col:
        tmp_df = tmp_df.drop(i, axis = 1)
    return tmp_df

# takes list of dfs & list of columns to drop, plot all groups of df without the passed col names
def plot_list_df(lst_df, list_col):
    for i in range(len(lst_df)):
        tmp_str = "Group: " + str(lst_df[i]['group_id'][0])
        tmp_df = drop_col(lst_df[i], list_col)
        ax = tmp_df.plot.line()
        ax.set_title(tmp_str, color='black')
        ax.legend(bbox_to_anchor=(1.0, 1.0))
        ax.plot()
        
#
def plot_col_corr_all(df, col_n):
    for i in range(len(df.columns)):
        if (col_n == i):
            continue
        ax = df.plot(x =col_n, y=i, kind = 'line')
        ax.plot()

#
def plot_col_corr(df, a, b):
    ax = df.plot(x =a, y=b, kind = 'line')
    ax.plot()

#corr table for all dfs
def plot_corr_all(lst_df):
    for i in range(len(lst_df)):
        print(lst_df[i].corr())

#cov table for all dfs
def plot_cov_all(lst_df):
    for i in range(len(lst_df)):
        print(lst_df[i].cov())

#corr for specific df, set title
def plot_corr(df, n):
    unwanted_names = {'machine_id', 'order', 'datetime', 'filepath', 'group_id', 'Shot rate'}
    tmp_df = drop_col(df[n-1], unwanted_names)

    corr = tmp_df.corr()
    ax = sns.heatmap(
        corr, 
        vmin=-1, vmax=1, center=0,
        cmap=sns.diverging_palette(20, 220, n=200),
        square=True
    )
    ax.set_title('Group '+ str(n))
    ax.set_xticklabels(
        ax.get_xticklabels(),
        rotation=45,
        horizontalalignment='right'
    );
        
#corr for all dfs
def plot_corr_all(list_df):
    for i in range(len(list_df)):
        unwanted_names = {'machine_id', 'order', 'datetime', 'filepath', 'group_id', 'Shot rate'}
        tmp_df = pl_f.drop_col(list_df[i], unwanted_names)

        corr = tmp_df.corr()
        ax = sns.heatmap(
            corr, 
            vmin=-1, vmax=1, center=0,
            cmap=sns.diverging_palette(20, 220, n=200),
            square=True
        )
        ax.set_xticklabels(
            ax.get_xticklabels(),
            rotation=45,
            horizontalalignment='right'
        );
        
# add function to print and return var in certain data streams

#------------------------------------        
# plot all clustering, check for interesting data streams to cluster
def cluster_1d_all(list_df):
    for i in range(len(list_df)):
        #add cols here
        tmp_df = col
        x = tmp_df
        k = 3
        clusters, centroids = km1d.cluster(x,k)
        #print(clusters)
        print(centroids)
        
        
# plot single clustering
def cluster_1d(col):
    #tmp_df = list_df[0]["008.Filling  time [s]"]
    tmp_df = col
    x = tmp_df
    k = 3
    clusters, centroids = km1d.cluster(x,k)
    #print(clusters)
    print(centroids)

#---------------------------------------------
    
#line plot for a specific data stream
def plot_line(col):
    tmp_df = col
    val = 0
    ar = tmp_df
    plt.plot(ar, np.zeros_like(ar) + val, 'x')
    plt.show()
    
#
def print_info(lst_df, file_count, rows):
    print('Number of groups = ' + str(len(lst_df)))
    print('Number of files = ' + str(file_count))
    print('Total number of rows in all files = ' + str(rows))
    for i in range(len(lst_df)):
        print('\nGroup ' + str(i+1) +' shape = ' + str(lst_df[i].shape))
        print("Newest file in group "+ str(i+1))
        print_latest_file(lst_df, i)
        
#
def print_all_files(lst_df):
    list_files = lst_df["filepath"].unique()
    return list_files

#
def print_table(list_df, unwanted_names):
    tmp_df = drop_col(list_df, unwanted_names)
    tmp_df = tmp_df.reindex(tmp_df.var().sort_values().index, axis=1)
    inf_df = tmp_df.describe()
    inf_df = inf_df.T
    inf_df['std'] = inf_df['std']**2
    inf_df['median'] = tmp_df.median()
    inf_df = inf_df.T
    inf_df = inf_df.drop('count')
    inf_df = inf_df.drop('25%')
    inf_df = inf_df.drop('50%')
    inf_df = inf_df.drop('75%')
    save_df = inf_df.rename(index={"std": "var"})
    save_df = save_df.T
    save_df = save_df[['var', 'mean', 'median', 'min', 'max']]
    #save_df.T.round(2)
    return save_df


# Print rows with a specific value for a certain column 
def print_rows_val(lst_df, col, val):
    return lst_df.loc[lst_df[col] == val]

#Scatter plot 3 streams(plotly)
def scatter3s(df, x1, y1, z1):
    fig = px.scatter(df, x=x1, y=y1, color=z1)
    fig.show()

#Scatter plot 2 streams(plotly)
def scatter2s(df, x1, y1):
    fig = px.scatter(df, x=x1, y=y1)
    fig.show()
    
# print number and names of files in a certain dataframe
def nfiles(df, n):
    x = n
    print("Number of files in group " + str(x) + " = " + str(len(df[n-1]["filepath"].unique())))
    return df[n-1]["filepath"].unique()

# print var of a single data stream for each group
def print_var(df, x):
    print(x + " variance for each group: ")
    for i in range(5):
        print("Group " + str(i+1) + " = "+ str(df[i]["008.Filling  time [s]"].var()))
        
# clusterting 1d for a certain data stream for all groups
def cluster1D_all(df, col, y):
    tmp_df = df[0][col]
    for i in range(4):
        tmp_df = tmp_df.append(df[i+1][col], ignore_index=True)
    x = tmp_df
    k = y
    clusters, centroids = km1d.cluster(x,y)
    #print(clusters)
    print("Clustering data stream: "+ col)
    print(centroids)
    val = 0
    ar = tmp_df
    plt.plot(ar, np.zeros_like(ar) + val, 'x')
    plt.plot(centroids, np.zeros_like(centroids) + val, 'o')
    plt.show()

# clustering 1D for a cetain data stream in a dataframe
def cluster1D(df, col, y):
    tmp_df = df[col]
    x = tmp_df
    k = y
    clusters, centroids = km1d.cluster(x,y)
    #print(clusters)
    print("Clustering data stream: "+ col)
    print(centroids)
    val = 0
    ar = tmp_df
    plt.plot(ar, np.zeros_like(ar) + val, 'x')
    plt.plot(centroids, np.zeros_like(centroids) + val, 'o')
    plt.show()
    

#
def print_rows_file(lst_df, y):
    x = './test_data2/'
    z = '.xls'
    file = x+y+z
    return lst_df.loc[lst_df['filepath'] == file]


# print all recent dates from every group
def print_recent_all(list_df):
    tmp_df = list_df[0].sort_values(by = "datetime")
    print(tmp_df.tail(1)['datetime'])
    tmp_df = list_df[1].sort_values(by = "datetime")
    print(tmp_df.tail(1)['datetime'])
    tmp_df = list_df[2].sort_values(by = "datetime")
    print(tmp_df.tail(1)['datetime'])
    tmp_df = list_df[3].sort_values(by = "datetime")
    print(tmp_df.tail(1)['datetime'])
    tmp_df = list_df[4].sort_values(by = "datetime")
    print(tmp_df.tail(1)['datetime'])


#    
def print_rows_date(lst_df, date):
    return lst_df.loc[lst_df['datetime'] == date]
    
    
# Print rows from a certain file with a specific datatime 
def print_rows_file_date(lst_df, date, y):
    x = './test_data2/'
    z = '.xls'
    file = x+y+z
    return lst_df.loc[(lst_df['datetime'] == date) & (lst_df['filepath'] == file)]

# Print latest file in a group
def print_latest_file(lst_df, n):
    x = lst_df[n].sort_values(by = "datetime").iloc[-1]
    print('Filepath: ' + str(x["filepath"]) + ', Datetime: ' + str(x["datetime"]))
    
    

