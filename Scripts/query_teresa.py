#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Looks at the data and puts on the map the query of finance and insurance employment in three states in private sector only

@author: shinypaul
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
import plotly.io as pio
import plotly.express as px
import plotly as plt

os.chdir("/Users/shinypaul/Documents/UVA/CS-5010/CS-5010-Group-Project-main/")
# read csv of scraped data
df = pd.read_csv('Data/LEHD_Tract.csv')
# read shapefile
dc_shapes = gpd.read_file('/Users/shinypaul/Documents/UVA/CS-5010/CS-5010-Group-Project-main/Shapefile/DC_MD_VA_Tracts.shp')
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