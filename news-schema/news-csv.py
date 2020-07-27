#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 16 16:52:56 2020

@author: travishartman
"""

import pandas as pd
import yaml as yaml
import datetime as dt
import argparse
import os
import sys
import numpy as np
import math

# python3 news-csv.py --news=news/tester.json --yaml=news/search_all_covid.yaml --output=news/results.csv --typer=False

# Ignore the pandas overwrite caveats from adding columns with data to dataframe
pd.options.mode.chained_assignment = None

# set directory and read in data
wrkDir = os.getcwd()
wrkDir = wrkDir + '/'

parser = argparse.ArgumentParser('Obtain File info')
parser.add_argument('--news', dest ='news', type=str, help='The News Search .json')
parser.add_argument('--yaml', dest ='yaml', type=str, default='search_all_covid.yaml', help='YAML file used to build News Search')
parser.add_argument('--output', dest ='output', type=str, default='results.csv', help='The name of the desired output file.')
parser.add_argument('--typer', dest ='typer', type=str, default='True', help='False will reduce file size significantly')
args = parser.parse_args()

news_articles = args.news
yaml_file = args.yaml
typer = args.typer
out_file = args.output

# Work with yaml first:
with open(yaml_file) as f:
    yp = yaml.safe_load(f)

#Seperate odin/regex due to different dict structure and add search criteria as qualifiers and description key for the feature
regex = {}
odin = {}
for key in yp['target_variables']:
    if yp['target_variables'][key]['matchType'] == 'verb-object':
        new_key = key + "_value"
        new_descr = key + "_description"
        qual_verb = key + "_verb"
        qual_obj = key + "_obj"
        temp_verb = " ".join(yp['target_variables'][key]['verbs'])
        temp_obj = " ".join(yp['target_variables'][key]['objects'])
        odin[new_key] = {'name': new_descr,
                         'description': 'semantic NLP match for verb object pairings',
                         'qualifier': {qual_verb: temp_verb, qual_obj: temp_obj} 
                        }
    else:
        new_key = key + "_value"
        new_descr = key + "_description"
        new_q = key + "_regex"
        temp = " ".join(yp['target_variables'][key]['targets'])
        regex[new_key] = {'name': new_descr,
                          'description': 'regex match',
                          'qualifier': {'col_name': new_q, 'qual': temp}
                         }     

# USER NEEDS TO ADD THIS TO THE STANDARD YAML TO GET GEO-POLICAL LEVELS
meta= {'country': yp['admin']['country'], 
       'adminX': yp['admin']['adminX'], 'adminY': yp['admin']['adminY']}

# Update geo-political levels
adminX = meta['adminX']
adminY = meta['adminY']

# Work with JSON from News-Article-Search
df_raw = pd.read_json(news_articles, lines=True)

# Delete rows without Publish Date and reset index
df1 = df_raw[df_raw.publish_date.notna()]
df =  df1[df1.publish_date != '']
df.reset_index(drop=True, inplace=True)

#delete uneeded query column
del df['query']

#Update the columns for schema compliance:
keepers = ['time', 'title', 'text', 'url', 'adminX', 'adminY', 'admin_1', 'admin_2','admin_3', 'country']
df.columns = [x if x in keepers else x + '_value' for x in df.columns]
df.rename(columns = {'publish_date_value': 'time', 'adminX':adminX, 'adminY':adminY}, inplace = True)

#Add country column
df['country']=meta['country'] 

#ISO 8601 2020-07-16T22:03:45+00:00....YYYY-MM-DDT00:00:00
df['time']=df['time'].apply(lambda x: pd.to_datetime(x).strftime("%Y-%m-%dT%H:%M:%S"))

# For the odinson features AND regex Quantity: return the count of tokens, instead of the token/quantity
headers= list(df.columns)
for key in headers:
    if key not in keepers:
        df[key] = df[key].apply(lambda x: int(len(x)) if type(x)==list else x)  # replace lists with len
        df[key] = df[key].apply(lambda x: 0 if math.isnan(x) else x)  # replace NaN with 0.0 

# WARNING: creates unwieldly sized files with redundant data
if typer == str(True):
    # Add to EACH feature the qualifiers url, text, and title
    cols = list(df.columns)
    for feat in cols:
        if "_value" in feat:
    
            # title
            temp_title = feat.split('_value')[0] + '_title'
            df[temp_title] = df['title']
    
            # text
            temp_title = feat.split('_value')[0] + '_text'
            df[temp_title] = df['text']
    
            # url
            temp_title = feat.split('_value')[0] + '_url'
            df[temp_title] = df['url']   
                
    #delete old columns
    deleter = ['title', 'url', 'text']
    for dels in deleter:
        del df[dels]      

# ADD DUMMY feature to hold article metadata and avoid over-data
if typer == str(False):
    df.insert(2, 'article_value', 1)
    df.insert(3, 'article_description', "Placeholder feature for Article url and title")
    df.insert(4, 'article_url', df['url'])
    df.insert(5, 'article_title', df['title'])
    
    #delete old column headers
    deleter = ['title', 'url', 'text']
    for dels in deleter:
        del df[dels]

#Add descriptions
for key in odin.keys():
    name = odin[key]['name']
    descr = odin[key]['description']
    for qual in odin[key]['qualifier'].keys():
        qual_val = odin[key]['qualifier'][qual]

        df.loc[:, name] = descr
        df.loc[:, qual] = qual_val

for key in regex.keys():
    name = regex[key]['name']
    descr = regex[key]['description']
    qual = regex[key]['qualifier']['col_name']
    qual_val = regex[key]['qualifier']['qual']
    
    df.loc[:, name] = descr
    df.loc[:, qual] = qual_val

#Send csv file to directory
df.to_csv(wrkDir + out_file, index=False)
