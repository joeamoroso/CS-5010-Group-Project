# -*- coding: utf-8 -*-
"""
Created on Sat Oct  3 15:33:21 2020

@author: Joe
"""
import os
import pandas as pd
import numpy as np
import requests
import gzip
import shutil

# =============================================================================
# Gather US Census LEHD Data from HTTS links
# =============================================================================
states = ['dc','md','va']
types = ['JT00','JT03','JT04']
years = ['2011','2012','2013','2014','2015']

files = []

os.chdir('C:\\CS-5010-Group-Project\\Data\\')

# Loop through years 2011-2017 for DC, MD, VA and extract total, federal, and private employment tarfiles
for year in years:

    for state in states:
        
        for jobtype in types:
            url = 'https://lehd.ces.census.gov/data/lodes/LODES7/'+ state +'/wac/'+ state + '_wac_S000_' + jobtype + '_'+ year +'.csv.gz'
            response = requests.get(url,stream = True)
            target_path =state + '_wac_S000_' + jobtype + '_'+ year +'.csv.gz'
            with open(target_path,'wb') as f:
                f.write(response.raw.read())
           
            # with tarfile.open(url,mode ='r') as f:
            #      f.extract(r'C:/CS-5010-Group_Project/' + state)

# Loop through each tarfile and extract to CSV
for file in os.listdir():
    if file.endswith('.gz'):
        file_s = file[:-3]
        with gzip.open(file,'rt') as f_in:
            with open(file_s,'wt') as f_out:
              shutil.copyfileobj(f_in, f_out)

# Read in each created CSV to a list, add year and employment type to each df
data_list = []
for file in os.listdir():
    if file.endswith('.csv'):
       year = file[:-4]
       emp = file[:-9]
       year = file[len(year) -4:len(year)]
       emp = emp[len(emp) -4:len(emp)]
       data = pd.read_csv(file)
       data['Year'] = year
       data['Emp_Type'] = emp
       data_list.append(data)

df = pd.concat(data_list)

# =============================================================================
# Data Queries
# =============================================================================

# Renaming Employment Types # 
df['Emp_Type'] = np.where(df['Emp_Type'] == 'JT00','All',df['Emp_Type'])
df['Emp_Type'] = np.where(df['Emp_Type'] == 'JT03','Private',df['Emp_Type'])
df['Emp_Type'] = np.where(df['Emp_Type'] == 'JT04','Federal',df['Emp_Type'])

df.rename(columns = {'CNS01': 'NAICS_11',
                     'CNS02': 'NAICS_21',
                     'CNS03': 'NAICS_22',
                     'CNS04': 'NAICS_23',
                     'CNS05': 'NAICS_31_33',
                     'CNS06': 'NAICS_42',
                     'CNS07': 'NAICS_44_45',
                     'CNS08': 'NAICS_48_49',
                     'CNS09': 'NAICS_51',
                     'CNS10': 'NAICS_52',
                     'CNS11': 'NAICS_53',
                     'CNS12': 'NAICS_54',
                     'CNS13': 'NAICS_55',
                     'CNS14': 'NAICS_56',
                     'CNS15': 'NAICS_61',
                     'CNS16': 'NAICS_62',
                     'CNS17': 'NAICS_71',
                     'CNS18': 'NAICS_72',
                     'CNS19': 'NAICS_81',
                     'CNS20': 'NAICS_92'},inplace = True)

df.to_csv('all_LEHD_2011-2015.csv')

