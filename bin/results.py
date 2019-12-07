import glob
import time
from fpdf import FPDF
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


document = FPDF()
document.add_page() 
document.set_font("Arial", size=7) 
directory = '*.html'   
files=glob.glob(directory)
col_width = (document.w - 2*document.l_margin)/5
document.ln(12)
my_tables = []
for file in files:     
    tables = pd.read_html(file)
    temp = tables[0]
    temp['fileName'] = file
    my_tables.append(temp)
temp = my_tables[0][['Name']].values.tolist()	
name = my_tables[0][['Name']]	
final = my_tables[0]
final['ExperimentNo'] = 0
for j in range(1,len(my_tables)):
    temp = my_tables[j]
    temp['ExperimentNo'] = j
    final = pd.concat([final,temp], ignore_index=False)
     
#succ = final.groupby(['Name'])['Succ'].sum()	
#fail = final.groupby(['Name'])['Fail'].sum()	
#sendRate = final.groupby(['Name'])['Send Rate (TPS)'].mean()	
#maxLatency = final.groupby(['Name'])['Max Latency (s)'].max()	
#minLatency = final.groupby(['Name'])['Min Latency (s)'].min()	
#avgLatency = final.groupby(['Name'])['Avg Latency (s)'].mean()	
#throughput = final.groupby(['Name'])['Throughput (TPS)'].mean()
#dat = pd.concat([succ,fail,sendRate,maxLatency,minLatency,avgLatency,throughput],axis=1)
tempcheck=(final.groupby(final['Name']))		
#print(temp)
dat = pd.DataFrame()
#for j in range(1,len(tempcheck)):
#    temp = pd.concat([temp,tempcheck[j]], ignore_index=True)
for key, item in tempcheck:
    dat=pd.concat([dat,tempcheck.get_group(key)], ignore_index=True)
document.cell(col_width/4, 10, 'Ex. No', border=1)
document.cell(col_width, 10, 'File name', border=1)
document.cell(col_width/2, 10, 'Name', border=1)
document.cell(col_width/3, 10, 'Succ', border=1)
document.cell(col_width/3, 10, 'Fail', border=1)
document.cell(col_width/2, 10, 'SendRate(TPS)', border=1)
document.cell(col_width/2, 10, 'MaxLatency(s)', border=1)
document.cell(col_width/2, 10, 'MinLatency(s)', border=1)
document.cell(col_width/2, 10, 'AvgLatency(s)', border=1)
document.cell(col_width/2, 10, 'Throughput(TPS)', border=1)
document.ln(12)
for i in range(0, len(dat)):
    document.cell(col_width/4, 10, str(dat['ExperimentNo'].iloc[i]), border=1)
    document.cell(col_width, 10, str(dat['fileName'].iloc[i]), border=1)
    document.cell(col_width/2, 10, str(dat['Name'].iloc[i]), border=1)
    document.cell(col_width/3, 10, str(dat['Succ'].iloc[i]), border=1)
    document.cell(col_width/3, 10, str(dat['Fail'].iloc[i]), border=1)
    document.cell(col_width/2, 10, str(round(dat['Send Rate (TPS)'].iloc[i],5)), border=1)
    document.cell(col_width/2, 10, str(dat['Max Latency (s)'].iloc[i]), border=1)
    document.cell(col_width/2, 10, str(dat['Min Latency (s)'].iloc[i]), border=1)
    document.cell(col_width/2, 10, str(round(dat['Avg Latency (s)'].iloc[i],5)), border=1)
    document.cell(col_width/2, 10, str(round(dat['Throughput (TPS)'].iloc[i],5)), border=1)
    document.ln(12);
# Plot
for key, item in tempcheck:
    temp = tempcheck.get_group(key)
    tim = time.strftime("%Y%m%d%H%M%S")
    plt.bar(temp['ExperimentNo'], temp['Throughput (TPS)'])
    plt.title(str(temp['Name'].iloc[0]))
    plt.savefig(str(temp['Name'].iloc[0])+tim)
    document.add_page()
    document.image(str(temp['Name'].iloc[0])+tim+'.png')
    plt.clf()


document.output('result'+tim+'.pdf','F')