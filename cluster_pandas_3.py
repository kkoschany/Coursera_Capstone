# -*- coding: utf-8 -*-
"""
Created on Wed May 22 06:28:19 2019

@author: kkosc
"""

import pandas as pd
import wikipedia as wp
import numpy as np
import matplotlib.cm as cm
import matplotlib.colors as colours
from sklearn.cluster import KMeans
import folium
from geopy.geocoders import Nominatim


## create our dataframe of Postal Codes, Boroughs, Neighbourhoods, and Coordinates

# read and scrape the table from Wikipedia
html = wp.page("List of postal codes of Canada: M").html().encode("UTF-8")
df = pd.read_html(html)[0]

# adjust the data in the dataframe to our specifications
df = df[df.Borough != 'Not assigned']
df = df.groupby(['Postcode','Borough'])['Neighbourhood'].apply(', '.join).reset_index()
df = df.replace(to_replace='Not assigned', value='Queen\'s Park')

# add latitude and longitude to the dataframe
latlng = pd.read_csv('Geospatial_Coordinates.csv').reset_index()
del latlng['index']
del latlng['Postal Code']
df = df.join(latlng, sort=False)


## cluster the neighbourhoods of Toronto proper and map them

# slice the original dataframe and create a new dataframe of the Toronto proper data
toronto_data = df.replace(to_replace='East Toronto', value='Toronto')
toronto_data = toronto_data.replace(to_replace='Central Toronto', value='Toronto')
toronto_data = toronto_data.replace(to_replace='Downtown Toronto', value='Toronto')
toronto_data = toronto_data.replace(to_replace='West Toronto', value='Toronto')
toronto_data = toronto_data.replace(to_replace='Queen\'s Park', value='Toronto')
toronto_data = toronto_data[toronto_data.Borough != 'Scarborough']
toronto_data = toronto_data[toronto_data.Borough != 'North York']
toronto_data = toronto_data[toronto_data.Borough != 'East York']
toronto_data = toronto_data[toronto_data.Borough != 'York']
toronto_data = toronto_data[toronto_data.Borough != 'Etobicoke']
toronto_data = toronto_data[toronto_data.Borough != 'Mississauga'].reset_index()
del toronto_data['index']

#set number of clusters
kclusters = 4

toronto_grouped_clust = toronto_data.drop('Neighbourhood', 1)
del toronto_grouped_clust['Postcode']
del toronto_grouped_clust['Borough']

# run k-means clustering
kmeans = KMeans(n_clusters=kclusters, random_state=0).fit(toronto_grouped_clust)

# check cluster labels generated for each row in the dataframe
kmeans.labels_[0:10]

# add clustering labels
toronto_data.insert(0, 'Cluster Labels', kmeans.labels_)

# create the map
address = 'Toronto, ON'
geolocator = Nominatim(user_agent="to_explorer")
location = geolocator.geocode(address)
latitude = location.latitude
longitude = location.longitude
map_clusters = folium.Map(location=[latitude, longitude], zoom_start=11)

# set coluor scheme for the clusters
x = np.arange(kclusters)
ys = [i + x + (i*x)**2 for i in range(kclusters)]
colours_array = cm.rainbow(np.linspace(0, 1, len(ys)))
rainbow = [colours.rgb2hex(i) for i in colours_array]

# add markers to the map
markers_colours = []
for lat, lon, poi, cluster in zip(toronto_data['Latitude'], toronto_data['Longitude'], toronto_data['Neighbourhood'], toronto_data['Cluster Labels']):
    label = folium.Popup(str(poi) + ' Cluster ' + str(cluster), parse_html=True)
    folium.CircleMarker(
        [lat, lon],
        radius=5,
        popup=label,
        color=rainbow[cluster-1],
        fill=True,
        fill_color=rainbow[cluster-1],
        fill_opacity=0.7).add_to(map_clusters)
       
map_clusters