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
import geopandas as gpd
import matplotlib.pyplot as plt
from descartes import PolygonPatch
from shapely.geometry import Point, LineString, Polygon, shape, GeometryCollection
import json
import plotly.express as px

# =============================================================================
# Gather US Census LEHD Data from HTTS links
# =============================================================================
states = ['dc','md','va']
types = ['JT00','JT03','JT04']
years = ['2011','2012','2013','2014','2015']

os.chdir('C:\\CS-5010-Group-Project\\Data\\')

# Loop through years 2011-2017 for DC, MD, VA and extract total, federal, and private employment tarfiles
try:

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

except Exception as e:
    print('Error downloading: ', e)
    
# =============================================================================
# Clean Data 
# =============================================================================

# Renaming Employment Types # 
df['Emp_Type'] = np.where(df['Emp_Type'] == 'JT00','All',df['Emp_Type'])
df['Emp_Type'] = np.where(df['Emp_Type'] == 'JT03','Private',df['Emp_Type'])
df['Emp_Type'] = np.where(df['Emp_Type'] == 'JT04','Federal',df['Emp_Type'])

df.rename(columns = {'C000': 'Tot_Emp',
                     'CNS01': 'NAICS_11',
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
                     'CNS20': 'NAICS_92',
                     'CE01' : 'NAICS_1250',
                     'CE02' : 'NAICS_1251_3333',
                     'CE03' : 'NAICS_3333'},inplace = True)

# Get and aggreagate data by Census Tract (11 digit) from Block Level (15 digit) #
df['GEOID'] = df['w_geocode'].astype(str).str.slice(0, 11)
df['GEOID'] = df['GEOID'].astype('int64')

# Aggregate Data by Tract, Year, and Employment Group 

df_tract = df[['GEOID','Year','Emp_Type','Tot_Emp','NAICS_11','NAICS_21','NAICS_22','NAICS_23',
               'NAICS_31_33','NAICS_42','NAICS_44_45','NAICS_48_49',
               'NAICS_51','NAICS_52','NAICS_53','NAICS_54','NAICS_55','NAICS_56',
               'NAICS_61','NAICS_62','NAICS_71','NAICS_72','NAICS_81','NAICS_92',
               'NAICS_1250','NAICS_1251_3333','NAICS_3333']].groupby(['GEOID','Year','Emp_Type']).agg('sum').reset_index()

df_tract.head()

df_tract.to_csv('LEHD_Tract.csv',index = False)

# =============================================================================
#  Import DMV Shapefile and join Data 
# =============================================================================
dmv = gpd.read_file('C:/CS-5010-Group-Project/Shapefile/DC_MD_VA_Tracts.shp')
dmv.plot(facecolor = 'none',edgecolor ='black', lw =0.4)

# =============================================================================
# Queries
# =============================================================================
# with open('geojson/DC_Metro_Area_WGS.geojson') as f:
#   dc_tracts = json.load(f)

# dat = pd.read_csv('LEHD_Tract.csv')

# max_value = dat['NAICS_62'].max()
# fig = px.choropleth(dat, geojson=dc_tracts, locations='GEOID',       
#                            color='NAICS_21',
#                            color_continuous_scale="Viridis",
#                            range_color=(0, max_value),
#                            featureidkey="properties.GEOID",
#                            projection="mercator"
#                           )
# fig.update_geos(fitbounds="locations", visible=False)
# fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})









