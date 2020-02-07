import glob
import pandas as pd
import re
import os
import argparse
from shutil import copy
import plotly.graph_objects as go
import plotly
import matplotlib.pyplot as plt

ANALYZER_PATH = "analyzer/"
WORKLOAD_PATH = "workload/"
reportsDir = WORKLOAD_PATH + 'caliper-reports/*.html'
resultsDir = ANALYZER_PATH + 'aggregated-results/'
html_template = ANALYZER_PATH + 'dashboard.html'
html_result = ANALYZER_PATH + 'aggregated-results/dashboard.html'
copy(html_template, html_result)
files = glob.glob(reportsDir)

def load_args():
    parser = argparse.ArgumentParser(description="This script is for running caliper benchmark")
    parser.add_argument("--interval", help="Optimal Block interval", required=True)
    parser.add_argument("--gaslimit", help="Optimal Block gas limit", required=True)
    parser.add_argument("--throughput", help="Max thoughput", required=True)
    parser.add_argument("--executiontime", help="Execution Time", required=True)
    return parser.parse_args()

if __name__ == '__main__':
    config = load_args()
    my_tables = []
    for file in files:
        tables = pd.read_html(file)
        temp = tables[0]
        temp['fileName'] = file.split('/')[-1]
        print(temp['fileName'])
        my_tables.append(temp)
    temp = my_tables[0][['Name']].values.tolist()
    name = my_tables[0][['Name']]
    final = my_tables[0].drop(1)
    final['ExperimentNo'] = 0
    final['gasLimit'] = str(final['fileName']).split('-')[1].split('.')[0]
    final['gasLimit'] = final['gasLimit'].astype(float)
    final['blockInterval'] = str(final['fileName'][0]).split('second')[0]
    final['blockInterval'] = final['blockInterval'].astype(float)
    for j in range(1, len(my_tables)):
        temp = my_tables[j].drop(1)
        temp['ExperimentNo'] = j
        temp['gasLimit'] = str(temp['fileName']).split('-')[1].split('.')[0]
        temp['gasLimit'] = temp['gasLimit'].astype(float)
        temp['blockInterval'] = str(temp['fileName'][0]).split('second')[0]
        temp['blockInterval'] = temp['blockInterval'].astype(float)
        final = pd.concat([final, temp], ignore_index=False, sort=False)

    final = final.drop('Succ', axis=1).drop('Fail', axis=1).drop('Send Rate (TPS)', axis=1).drop(
        'Max Latency (s)', axis=1).drop(
        'Min Latency (s)', axis=1).drop('Avg Latency (s)', axis=1).drop('fileName', axis=1).drop('ExperimentNo',
                                                                                                 axis=1)
    final.rename(columns={'Throughput (TPS)': 'throughput'}, inplace=True)
    tempcheck = final.groupby(final['throughput'])

    dat = pd.DataFrame()
    for key, item in tempcheck:
        dat = pd.concat([dat, tempcheck.get_group(key)], ignore_index=True)

    # create overall report

    dat.to_csv(resultsDir + 'data.csv', index=False)
    dat=dat.sort_values(by=['throughput'],ascending=False)
    html = ''
    # create seperate fille for each function
    for name in dat['Name'].unique():
        file_name_csv = resultsDir + 'data_{0}.csv'.format(name)
        file_name_html = resultsDir + 'data_{0}.html'.format(name)
        dat[dat['Name'] == name].drop('Name', axis=1).to_csv(file_name_csv, index=False)
        df = dat[dat['Name'] == name].drop('Name', axis=1)
        html = dat[dat['Name'] == name].drop('Name', axis=1).to_html(index=False)

    html = html.split('\n', 3)[3]
    #Create plots for Throughput analysis
    data = dat
    print(data.columns)
    data = data.loc[data['Name']=='transfer']
    gaslimit = data['gasLimit'].values
    blockinterval = data['blockInterval'].values
    tps = data['throughput'].values
    fig = go.Figure(data=[go.Scatter(
        x=gaslimit,
        y=blockinterval,
        text=['TPS:'+str(s) for s in tps],
        mode='markers',
        marker=dict(
            size=tps,
            sizemode='area',
            sizeref=2.*max(tps)/(40.**2),
            sizemin=4
            )
            )])
    fig.update_layout(
    title="Throughput for varying gas limit and block interval ",
    xaxis_title="Gas Limit",
    yaxis_title="Block Interval"
    )
    plotly.offline.plot(fig, filename=resultsDir+'bubbleplot.html', auto_open=False)
    fig, ax = plt.subplots(1,1);
    data.groupby("blockInterval").plot(x="gasLimit", y="throughput", ax=ax)
    plt.xlabel('Gaslimit')
    plt.ylabel('Throughput')
    plt.legend([v[0] for v in data.groupby('blockInterval')['blockInterval']], title = 'Block interval')
    plt.savefig('line_graph.png')
# Create Interactive plots

    fig = go.Figure()
    l = len(set(data.blockInterval))
    buttons = list()
    buttons.append(dict(label="All",
                         method="update",
                         args=[{"visible": [True]*l},
                               {"title": "All Blockintervals",
                                "annotations": []}]))
    blockInterval = list(set(data.blockInterval))
    for x in blockInterval:
        temp=data.loc[data['blockInterval']==x]
        temp=temp.sort_values(by=['gasLimit'])
        print(temp)
        fig.add_trace(go.Scatter(x=list(temp.gasLimit),y=list(temp.throughput),name="Blockinterval"+str(x)))
        temp1 = [False]*l
        temp1[blockInterval.index(x)] = True
        buttons.append(dict(label=str(x),
                         method="update",
                         args=[{"visible": temp1},
                               {"title": "Blockinterval "+str(x),
                                "annotations": []}]))
    fig.update_layout(
        updatemenus=[
            go.layout.Updatemenu(
                active=0,
                buttons=buttons,
            )
        ])

    fig.update_layout(title_text="All Blockintervals",xaxis_title="Gas Limit",
    yaxis_title="Throughput")

    plotly.offline.plot(fig, filename=resultsDir+'linegraph.html',auto_open=False)


    # print(html)
    with open(html_result, "r+") as f:
        data = f.read()
        data = data.replace("{table}", html).replace("{interval}", config.interval).replace("{gaslimit}",
                config.gaslimit).replace("{throughput}", config.throughput).replace("{executiontime}", config.executiontime)
        f.seek(0)
        f.write(data)
        f.truncate()

    exit(0)
