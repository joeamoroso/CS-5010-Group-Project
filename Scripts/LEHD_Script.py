# -*- coding: utf-8 -*-
"""
Created on Sat Oct  3 15:33:21 2020

@author: Joe
"""
import os
import pandas as pd
import numpy as np
import tarfile
import wget
import requests
import gzip
import shutil


# =============================================================================
# Gather US Census LEHD Data from HTTS links
# =============================================================================
states = ['dc','md','va']
types = ['JT00','JT03','JT04']
years = ['2011','2012','2013','2014','2015','2016','2017']

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
               data =  f_in.read()
               f_out.write(data)

