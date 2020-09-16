#!/usr/bin/env python
# coding: utf-8

from qwikidata.sparql import (get_subclasses_of_item, return_sparql_query_results)
import pandas as pd
from IPython.display import display, HTML
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

from itertools import chain
import json

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

def clean_wikidata(results, headers):   
    # Build dataframe from wikidata results:
    df = noice(results, headers)

    # ...and delete articles without urls:
    df_urls = delete_no_url(df)

    # ...and collapse the duplicative item's rows while retaining their different instancesOf
    df_clean = df_urls[["item", "itemLabel", "article_url"]].drop_duplicates(subset='item')
    df_clean["instanceOfLabel"] = df_clean.item.apply(lambda x: collapser(x, df_urls))
    print(f'Deleted {df.shape[0]-df_urls.shape[0]} rows without urls \n\
    Collapsed {df_urls.shape[0] - df_clean.shape[0]} duplicate rows \n\
    There are now {df_clean.shape[0]} wikidata rows')
    
    return df_clean

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

# scrape the article urls on the wikipedia serach page 
def scrape_wikipedia(df_clean):

    # URLs from a manual search from link above, the three pages below have ETH-related pages
    url1 = 'https://en.wikipedia.org/w/index.php?title=Special:AllPages&from=Ethiopia'
    url2 = 'https://en.wikipedia.org/w/index.php?title=Special:AllPages&from=Ethiopian+Civil+Aviation+Agency'
    url3 = 'https://en.wikipedia.org/w/index.php?title=Special:AllPages&from=Ethiopian+farming'

    # list to churn through all of the urls on each of the three pages
    pages_urls=[url1, url2,url3]

    # Scrape URLS above for the article link URLs
    wikipedia_urls_only = get_all_wikipedia_urls(pages_urls)
    print()
    print(f'There are an additional {len(wikipedia_urls_only)} Wikipedia articles')
    print()
    
    
    # Scrape the wikipedia_urls_only to tag on the instancesOf/properties
    # This will take some time...
    wikipedia_urls = url_categories(wikipedia_urls_only)
    
    return wikipedia_urls


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
def table_scrapes(url_list_full, prob=.10, maxdelay=4):

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

# tunnel thru super_list to display each table
def view_tables(super_list):
    for dct in super_list[:100]:
        for key in dct.keys():
            for tab in dct[key]:
                if type(tab) == str:
                    pass
                else:
                    print(key)
                    print(dct['url'])
                    print(dct['properties'])
                    display(HTML(tab.to_html()))
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

