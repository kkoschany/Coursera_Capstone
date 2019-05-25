# -*- coding: utf-8 -*-
"""
Created on Wed May 22 06:28:19 2019

@author: kkosc
"""

import pandas as pd
import wikipedia as wp

#read and scrape the table from Wikipedia
html = wp.page("List of postal codes of Canada: M").html().encode("UTF-8")
df = pd.read_html(html)[0]

#adjust the data in the dataframe to our specifications
df = df[df.Borough != 'Not assigned']
df = df.groupby(['Postcode','Borough'])['Neighbourhood'].apply(', '.join).reset_index()
df = df.replace(to_replace='Not assigned', value='Queen\'s Park')

#add latitude and longitude to the dataframe
latlng = pd.read_csv('Geospatial_Coordinates.csv').reset_index()
del latlng['index']
del latlng['Postal Code']
df = df.join(latlng, sort=False)

#print the dataframe and its size
print(df)
print(df.shape)