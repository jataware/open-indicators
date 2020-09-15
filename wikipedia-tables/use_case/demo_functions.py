#!/usr/bin/env python
# coding: utf-8

from qwikidata.sparql import (get_subclasses_of_item, return_sparql_query_results)
import pandas as pd
import import_ipynb

import requests
import urllib.request
import time
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from urllib.request import urlopen
import re
import random
import json
import csv

import itertools
from itertools import chain
import json

# Plotting
import contextily as ctx
import shapely
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import matplotlib.pyplot as plt
import geopandas as gpd


# twist the number of plants/combos to see which groupings meet power threshold
def f(min, max, num):    
    return itertools.combinations(range(min, max), num)

def combo_it1(total_plants, num_op_plants, min_power, oromia_hydro):
    
    # iterate of the indicies to get n choose k combos for all plants
    combo_super_list = []
    num_plants = [x for x in range(total_plants+1)]
    for num in num_plants:
        combos = f(0, total_plants, num)
        for combo in combos:
            combo_super_list.append(combo)
            
    # get power production for plants in combo and see if combo meets threshold      
    good_combos = []
    for comb in combo_super_list:
        temp = 0
        for ind in comb:
            temp = temp + float(oromia_hydro['Installedcapacity (MWe)'].loc[ind])
        if temp >= min_power:
            good_news = [comb,temp]
            good_combos.append(good_news)
    
    # map indicies to plant name
    needed_plants = []
    for combo in good_combos: 
        if len(combo[0]) == num_op_plants:
            comb = combo[0]
            temp_p = []
            for ind in comb:
                temp = oromia_hydro['ICS Power plant'].loc[ind]
                temp = temp.split("[")[0]
                #temp = (temp)
                temp_p.append(temp)
                this_is_it = (temp_p, combo[1])   
            needed_plants.append(this_is_it) 

    if needed_plants == []:
        print(f'No combo meets power need of {round(min_power,2)} MWe')
    else:
        print(f'The following plant combination(s) meet the {round(min_power,2)} MWe requirement:')
        print()
        for plant in needed_plants:
            print(plant)

def no_rain(x, drought_index):
    return x*drought_index

def drought_power_production(drought_index, ethiopia_min_capacity, gdf):
    threshold = ethiopia_min_capacity
    total_d = gdf['Installedcapacity (MWe)']
    all_drought = [float(prod) for prod in total_d if "(" not in prod]
    ad = sum([no_rain(x, drought_index) for x in all_drought])
    print()
    if ad >= threshold:
        print(f'Success: Drought power production of {round(ad,2)} MWe meets {round(threshold,2)} MWe minimum by {round((ad-threshold )/threshold*100,2)}%')
    else:
        print(f'Warning: Drought power production of {round(ad,2)} MWe does not meet minimum {round(threshold,2)} MWe by {round((threshold-ad)/threshold*100,2)}%')

def by_the_numbers(gdf):
    # ALL ETHIOPIAN HYDRO POWER PRODUCTION:
    total= gdf['Installedcapacity (MWe)']
    total = [float(prod) for prod in total if "(" not in prod]
    total_power = sum(total)

    # OROMIA HYDRO POWER PRODUCTION:
    total_oromia = gdf[gdf['in_oromia']==True]['Installedcapacity (MWe)']
    total_oromia = [float(prod) for prod in total_oromia if "(" not in prod]
    total_oromia_power = sum(total_oromia)

    # Print Outs
    print()
    print(f'Ethiopia: Total hydro power production = {total_power} MWe')
    print(f'Oromia: Total hydro power production = {total_oromia_power} MWe')
    perc = round((total_oromia_power/total_power)*100,2)
    print(f'Oromia hydro supports {perc}% of Ethiopian hydro power')


def plot_plants(gdf, oromia):
    
    f, ax = plt.subplots(1, figsize=(12, 12))
    ax.set_ylabel("Latitude: North", size=20)
    ax.set_xlabel("Longitude: East",size=20)
    ax = oromia.plot(ax=ax, alpha=1, color="cyan")
    #ax = eth_river.plot(ax=ax, alpha=1, color="cyan")
    gdf[(gdf['in_oromia'] == True) & (gdf['operational'] == True)].plot(ax=ax, color = 'green', label="Inside Oromia")
    gdf[gdf['operational'] == False].plot(ax=ax, color = 'yellow', label="Not Operational")
    gdf[(gdf['in_oromia'] == False) & (gdf['operational'] == True)].plot(ax=ax, color = 'red', label="Outside Oromia")
    lims = plt.axis('equal')
    f.suptitle('Hydro Power Plants of Oromia', size=30)
    ax.grid()
    ctx.add_basemap(ax, zoom=10)
    plt.legend(prop={"size":15}, facecolor='cyan', framealpha=1)
    plt.show()


def filter_plants(gdf, oromia):
    gdf['in_oromia'] = gdf['geometry'].apply(lambda x: in_oromia(x, oromia))
    gdf['in_oromia_operational'] = gdf['geometry'].apply(lambda x: in_oromia(x, oromia))
    gdf['operational'] = gdf['Installedcapacity (MWe)'].apply(lambda x: op_vs_plan(x))
    in_oro = gdf['in_oromia'][gdf['in_oromia'] == True].count()
    in_op = gdf['in_oromia'][gdf['in_oromia'] == True][gdf['operational'] == True].count()

    print(f'There are {in_oro} hydro plants in Oromia, of which {in_op} are operational')

    return gdf

def op_vs_plan(x):
    if "(" in x:
        return False
    else:
        return True


# Function to check if power plant in Oromia:
def in_oromia(geo_pt, oromia):
    pt_in_bool = (oromia.contains(geo_pt))

    if True in pt_in_bool.values:
        return True
    else:
        return False

# ONE-OF for demo:
def clean_data(hydro_scrape):
    # grab first table with list of hydro power plants
    hydro_list = hydro_scrape[0]['List_of_power_stations_in_Ethiopia'][0]

    #Delete NaN Rows (Rows with Totals)
    hydro_list = hydro_list[hydro_list['ICS Power plant'] != 'Total']
    hydro_list = hydro_list[hydro_list['ICS Power plant'] != 'Total operational']

    # Rename laborious column header
    hydro_list = hydro_list.rename(columns={'Capacity factor(2016/17)[6][7][8][9][3]': 'Capacity Factor'})

    # Get series of lat/long strings
    hydro_coords_s = hydro_list['Coordinates']
    lat_= []
    lon_ = []

    #Convert Coordinates to float-type lat/long for plotting and subsetting to Oromia Region
    for str_coord in hydro_coords_s:
        #if type(str_coord) == str:
        temp = str_coord.split("/")[1]
        lat = float(temp.split(" ")[1].split("°")[0].split("\ufeff")[1])
        lon = float(temp.split(" ")[2].split("°")[0])
        lat_.append(lat)
        lon_.append(lon)

    # Add lat/long series to dataframe
    hydro_list.insert(2, "Latitude", lat_)
    hydro_list.insert(3, "Longitude", lon_)
    hydro_list.head(3)  
    gdf = hydro_list
    
    gdf1 = gpd.GeoDataFrame(gdf, geometry=gpd.points_from_xy(gdf.Longitude, gdf.Latitude))
    cols = gdf1.columns.tolist()
    cols.insert(4, cols.pop(cols.index('geometry')))
    gdf1 = gdf1.reindex(columns= cols)
    
    return gdf1



# Put wikidata results into a dataframe
def noice(results, headers):
    noice = []
    for res in results['results']['bindings']:
        temp={}
        for h in headers:
            if h in res.keys():
                if h == "item":
                    
                    item_url = res[h].get('value', "None")
                    q_code = item_url.split("/")[-1]
                    temp[h] = q_code

                else:
                    temp[h] = res[h].get('value', "None")

        noice.append(temp)
        
    return pd.DataFrame(noice)

# Delete rows without a URL
def delete_no_url(df, NaN_column='article_url'):
    
    df = df.dropna(subset=[NaN_column])
    df = df.reset_index(drop=True, inplace=False)
    
    return df

def collapser(item, df):
    joiner = ", ".join(list(df[df["item"] == item]["instanceOfLabel"]))
    return joiner

#### Wikipedia Functions

# Used in get_all_wikipedia_urls: scrapes for url 
def lister(soup):
    result = []
    uls = soup.find_all('ul', {'class': 'mw-allpages-chunk'})
    base ="https://en.wikipedia.org"
    for ul in uls:
        for li in ul.find_all('li'):
            for link in li.find_all('a'):
                end_url = link.get('href')
                url = base + end_url
                result.append(url)      
    return result

#Scrape main wikipedia category pages for all the urls on the pages
def get_all_wikipedia_urls(urls):
    res = []
    for url in urls:
        html = urlopen(url)
        soup = BeautifulSoup(html, 'html.parser')

        temp = lister(soup)
        res.append(temp)
        
    res = [i for g in res for i in g]
        
    return res

# tag the wikipedia urls with the instancesOf tags
def url_categories(wikipedia_urls):
    count = 0
    result = []
    tot = len(wikipedia_urls)
    
    print("Starting scrape for wikipedia articles' properties")
    
    for url in wikipedia_urls:
        if count%100 == 0 and count != 0:
            print(f'Scraped {count} of {tot} urls for properties')
            
        response = requests.get(url)
        soup = BeautifulSoup(response.text,"html.parser")

        cup_o_soup = soup.find('div', {'class': 'mw-normal-catlinks'})
        temp = []
        for cup in cup_o_soup.find_all("li"):
            for link in cup.find_all('a'):
                instant_cup = link.get('title').split(":")[-1]
                temp.append(instant_cup)
        result.append((url,temp))
        count += 1

    print("Property scrape complete")
    return result

def display_all_results(super_list_dict):

    df = pd.DataFrame(columns=["number of tables", "key", "url", "properties"])
    i = 0
    
    for d_ in super_list_dict:
        key = [x for x in d_.keys()][0]
        url = d_.get('url', "None")
        num_df = len(d_[key])
        prop = d_.get('properties', "None")
        df.loc[i] = [str(num_df), key, url, prop]
        i += 1
            
    #print(f' num df: {num_df} | key: {key} | url: {url}')

    return df 

#random delay to avoid getting scrape blocked
def decision(probability, maxdelay=8):
    
    if random.random() < probability:
        delay = random.randint(1, maxdelay)
    else:
        delay = 0
    
    return delay

#List of dicts; dict values are of dataframes of the tables for that particular url
def table_scrapes(url_list_full, prob=0, maxdelay=4):

    headers= {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
    
    print("Starting your scrape...")

    #Add key to tuple in "amplified" list of urls from wikidata search
    urls_amp = [(x[0], x[0].split("/")[-1], x[1]) for x in url_list_full] 
    
    # initialize
    super_list_dict = []
    count = 0
    success = 0
    tot = len(url_list_full)
    delay = [decision(prob,maxdelay) for x in range(tot)]
    
    # Iterate over each url, pull out any wikitables and throw into super list with key=article url tag
    for url_tup in urls_amp:

        if delay[count] != 0:
            print(f'Pause scrape for {delay[count]} second(s)')
            time.sleep(delay[count])
        
        # unique keys for the url
        url = url_tup[0]
        key = url_tup[1]
        cup = url_tup[2]

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text,"html.parser")
        
        #soup it 
        tables = soup.find_all("table", {"class":["wikitable", "infobox", "infobox vevent", "infobox vcard"]})
        
        if tables != []:
            try:
                # build temp dicts to dump into temp list that dumps into overall super list 
                df_dict = {}
                temp_list = []

                for table in tables:

                    str_tab = str(table)

                    #one-off replace to fix html error
                    str_tab = str_tab.replace('6;', '6')

                    temp_df = pd.read_html(str_tab)[0]
                    temp_list.append(temp_df)

                df_dict[key] = temp_list
                df_dict["url"] = url
                df_dict["properties"] = cup
                
                # add table df to super list
                super_list_dict.append(df_dict) 
                
                #success counter
                success +=1

            except:
                pass
                #print(f"Skipping Parsing Error for: {url}")
        else:
            print(f"No wikitables found, skipping: {url}")
        
        #Display
        if count%100 == 0 and count != 0:
            print()
            print(f'**** Scraped {count} of {tot} urls ****')
            print()
        count += 1    
    
    print("!!!! Complete !!!!")       
    print(f'{success} of {tot} urls have wikitables')

    return super_list_dict  

### Search Functions

# Search across all text for keyword
def keyword_search(soup_results, keyword):
    
    search_result = []
    outer_cnt = 0 
    
    for res in soup_results:

        for k,v in res.items():
            if k != "url" and k != 'properties':
                key=k
            if k == "url":
                url=res[k]

        inner_cnt = 0
        for frame in res[key]:

            t=frame.to_dict()
            values = set(chain.from_iterable(i.values() for i in t.values()))
            values = (str(values).split())

            temp_result = []
            for elem in values:
                if keyword.lower() in elem.lower():

                    temp_result = [outer_cnt, inner_cnt, key, url]

            if temp_result != []:
                search_result.append(temp_result)

            inner_cnt += 1    
        outer_cnt += 1
        
    for line in search_result:
        print(line)
    
    if search_result == []:
        return print("No results found")
        
    return search_result

# IN PROGRESS...
def search_title1(keyword, df):
    
    print(df[df['key'].str.contains(keyword, case=False)])      

# IN PROGRESS...
def search_title2(keyword, url_list):
    
    search_words = [x.split("/")[-1].lower() for x in url_list]

    index = []
    for words in search_word:
        temp_index = []
        if keyword.lower() in words:
            ind = search_words.index(words)
            index.append(ind)
            
    return index

