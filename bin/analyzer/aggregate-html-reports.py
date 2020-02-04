import glob
import pandas as pd
import re
import os
from shutil import copy

reportsDir = 'workload/caliper-reports/*.html'
resultsDir = 'analyzer/aggregated-results/'
html_template = 'analyzer/dashboard.html'
html_result = 'analyzer/aggregated-results/dashboard.html'
r_script = 'analyzer/plot_results.R'
bash_console='bash_console.txt'
python_console='python_console.txt'

copy(html_template, html_result)
files = glob.glob(reportsDir)
fin = open(bash_console, "rt")
all_data = fin.read()
fin.close()
all_data = all_data.replace('\n',"<br />")

temp = all_data.split('creationTimestamp')[0]
print(temp)
filtered_data = temp.split('---- CREATING BOOTNODE ----')[1]
filtered_data = '---- BOOTNODE Information----'+filtered_data
filtered_data = filtered_data.replace("BOOTNODE CREATED!",'')
filtered_data = filtered_data.replace("SLEEPING FOR 30 SECONDS TO MAKE SURE BOOTNODE IS UP...",'')
filtered_data = filtered_data.replace("CREATING NODES",'---- ETHEREUM NODES INFO ----')
fin1 = open(python_console, "rt")
python_data = fin1.read()
fin1.close()
python_data = python_data.replace('\n',"<br />")
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
tempcheck = (final.groupby(final['throughput']))

dat = pd.DataFrame()
for key, item in tempcheck:
    dat = pd.concat([dat, tempcheck.get_group(key)], ignore_index=True)
# create overall report
dat.to_csv(resultsDir + 'data.csv', index=False)
html = ''
# create seperate fille for each function
for name in dat['Name'].unique():
    file_name_csv = resultsDir + 'data_{0}.csv'.format(name)
    file_name_html = resultsDir + 'data_{0}.html'.format(name)
    dat[dat['Name'] == name].drop('Name', axis=1).to_csv(file_name_csv, index=False)
    html = dat[dat['Name'] == name].drop('Name', axis=1).to_html(index=False)

html = html.split('\n', 3)[3]


with open(html_result, "r") as f:
    data = f.read()
    data = data.replace("{table}", html)
    data = data.replace("{bash_console}", filtered_data)
    data = data.replace("{python_console}", python_data)

    
with open(html_result, "w") as f:
    f.write(data)
    f.truncate()

run_command = os.system("Rscript " + r_script)

exit(0)
