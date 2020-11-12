# -*- coding: utf-8 -*-
"""
Created on Sat Oct  3 15:33:21 2020

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
import plotly

# =============================================================================
# Gather US Census LEHD Data from HTTS links
# =============================================================================
states = ['dc','md','va']
types = ['JT00','JT03','JT04']
years = ['2011','2012','2013','2014','2015']

os.chdir(os.path.dirname(__file__))
os.chdir('..')
os.chdir('Data')

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
# Queries
# =============================================================================
df = pd.read_csv('LEHD_Tract.csv')
os.chdir('..')
# read shapefile
dc_shapes = gpd.read_file('Shapefile/DC_MD_VA_Tracts.shp')
# convert GEOID column to int64 for joining
dc_shapes['GEOID'] = dc_shapes['GEOID'].astype('int64')
# join with shapefile on GEOID
dat = df.merge(dc_shapes, how = 'left', on = "GEOID")
# remove Delaware
dat = dat[dat["STATEFP"] != 10]
# remove Pennsylvania
dat = dat[dat["STATEFP"] != 42]
# don't use federal or private
dat = dat[dat['Emp_Type'] == "All"]
# log transform column of interest
dat['log_Tot_Emp'] = np.log10(dat['Tot_Emp'] + .000000001)

# read json
with open('geojson/DC_Metro_Area.geojson') as f:
  dc_tracts = json.load(f)
  
# total employment
max_value = dat['log_Tot_Emp'].max()
fig = px.choropleth_mapbox(dat, geojson=dc_tracts, locations='GEOID',       
                           color='log_Tot_Emp',
                           color_continuous_scale="Inferno",
                           range_color=(0, max_value),
                           featureidkey="properties.GEOID",
                           animation_frame="Year",
                           #projection="mercator"
                           mapbox_style="carto-positron",
                           center = {"lat": 38, "lon": -77},
                           zoom = 5
                          )
fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show(renderer="browser")
plotly.offline.plot(fig,filename ='Data/log_tot-emp.html')

# fig.show()

# =============================================================================
# How does DC compare to Baltimore in terms of Government Employment for the past
# 5 years?
# =============================================================================

# First 5 digits of GEOID is county ID #

df['COUNTYID'] = df['GEOID'].astype(str).str.slice(0, 5)
df['STATEID'] = df['GEOID'].astype(str).str.slice(0, 2)
df['COUNTYID'] = df['COUNTYID'].astype('int64')
df['STATEID'] = df['STATEID'].astype('int64')

# Baltimore City FIPS = 24510
dc_bc = df.query(('COUNTYID == 24510 or STATEID == 11 and Emp_Type =="All"'))

dc_bc = dc_bc[['GEOID','COUNTYID','STATEID','Tot_Emp']]


# =============================================================================
# Compare highest employment and lowest employment dc_bc in the DMV area
# =============================================================================

dc_bc_agg = dc_bc[['COUNTYID','Tot_Emp']].groupby(['COUNTYID']).agg('mean')
dc_bc_agg
max_min = dc_bc[(dc_bc['Tot_Emp'] == max(dc_bc['Tot_Emp'])) | (dc_bc['Tot_Emp'] == min(dc_bc['Tot_Emp']))]

# =============================================================================
# Income Queries
# =============================================================================

df = df_tract
newdf = df[['GEOID','Year','Emp_Type','NAICS_1250','NAICS_1251_3333','NAICS_3333']]
#Queries for fun 
print(newdf)

print(newdf[0:2].sum())
print('--------------------------')
max_value = newdf.max()
print(max_value)
#Visualizations
# read shapefile
dc_shapes = gpd.read_file('Shapefile/DC_MD_VA_Tracts.shp')
# convert GEOID column to int64 for joining
dc_shapes['GEOID'] = dc_shapes['GEOID'].astype('int64')
# join with shapefile on GEOID
dat = newdf.merge(dc_shapes, how = 'left', on = "GEOID")
# remove Delaware
dat = dat[dat["STATEFP"] != 10]
# remove Pennsylvania
dat = dat[dat["STATEFP"] != 42]
# don't use federal or private
dat = dat[dat['Emp_Type'] == "All"]
# log transform column of interest
#dat['NAICS_3333'] = np.log10(dat['NAICS_62'] + .000000001)
import plotly.express as px
# read json
with open('geojson/DC_Metro_Area.geojson') as f:
  dc_tracts = json.load(f)
import plotly.io as pio
pio.renderers
# total employment

max_value = 1000

fig = px.choropleth_mapbox(dat, geojson=dc_tracts, locations='GEOID',
                           color = 'NAICS_3333',
                           color_continuous_scale="Inferno",
                           range_color=(0, max_value),
                           featureidkey="properties.GEOID",
                           animation_frame="Year",
                           #projection="mercator"
                           mapbox_style="carto-positron",
                           center = {"lat": 38, "lon": -77},
                           zoom = 5
                          )
fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show(renderer="browser")
plotly.offline.plot(fig,filename ='Data/income.html')

# =============================================================================
# Private Employment
# =============================================================================

df = df_tract
# read shapefile
dc_shapes = gpd.read_file('Shapefile/DC_MD_VA_Tracts.shp')
# convert GEOID column to int64 for joining
dc_shapes['GEOID'] = dc_shapes['GEOID'].astype('int64')
# join with shapefile on GEOID
dat = df.merge(dc_shapes, how = 'left', on = "GEOID")

# remove Delaware
dat = dat[dat["STATEFP"] != 10]
# remove Pennsylvania
dat = dat[dat["STATEFP"] != 42]


#PRIVATE ONLY
# don't use federal or all
dat = dat[dat['Emp_Type'] == "Private"]

# log transform column of interest - Finance and Insurance
dat['log_NAICS_52'] = np.log10(dat['NAICS_52'] + .000000001)

# read json
with open('geojson/DC_Metro_Area.geojson') as f:
  dc_tracts = json.load(f)

# private employment
max_value = dat['log_NAICS_52'].max()
fig = px.choropleth_mapbox(dat, geojson=dc_tracts, locations='GEOID',       
                           color='log_NAICS_52',
                           color_continuous_scale="Inferno",
                           range_color=(0, max_value),
                           featureidkey="properties.GEOID",
                           animation_frame="Year",
                           #projection="mercator"
                           mapbox_style="carto-positron",
                           center = {"lat": 38, "lon": -77},
                           zoom = 5
                          )
fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show(renderer="browser")
plotly.offline.plot(fig,filename ='Data/naics_52.html')

























