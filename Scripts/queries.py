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
import plotly.io as pio
import plotly.express as px
import plotly as plt
os.chdir("C:/CS-5010-Group-Project")
# read csv of scraped data
df = pd.read_csv('Data/LEHD_Tract.csv')

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
plt.offline.plot(fig,filename ='Data/log_tot-emp.html')

# fig.show()
