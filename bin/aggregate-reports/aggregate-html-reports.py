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
final['gasLimit'] = str(final['fileName']).split('-')[1].split('.')[0]
final['gasLimit'] = final['gasLimit'].astype(float)
final['blockSize'] = str(final['fileName'][0]).split('second')[0]
final['blockSize'] = final['blockSize'].astype(float)
for j in range(1,len(my_tables)):
    temp = my_tables[j]
    temp['ExperimentNo'] = j
    temp['gasLimit'] = str(temp['fileName']).split('-')[1].split('.')[0]
    temp['gasLimit'] = temp['gasLimit'].astype(float)
    temp['blockSize'] = str(temp['fileName'][0]).split('second')[0]
    temp['blockSize'] = temp['blockSize'].astype(float)
    final = pd.concat([final,temp], ignore_index=False, sort=False)

tempcheck=(final.groupby(final['Name']))		

dat = pd.DataFrame()
for key, item in tempcheck:
    dat=pd.concat([dat,tempcheck.get_group(key)], ignore_index=True)     

dat.to_csv('data.csv',index=False)