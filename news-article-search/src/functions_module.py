#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 16:12:59 2020

@author: travishartman
"""


from newspaper import Article
from odinson import Odinson
import pandas as pd
import configparser
import subprocess
import newspaper
import datetime
import requests
import logging
import http
import json
import os


def FormatGeo(geocsvfile):
# Format the geo data csv; returns a list of tuples

    geo = pd.read_csv(geocsvfile)
    
    geo_adminX = [i.split('[')[0] for i in geo.iloc[:,0].tolist()]
    geo_adminY = [i.split('[')[0] for i in geo.iloc[:,1].tolist()]
    
    geo_l = zip(geo_adminX, geo_adminY)
    geo_l = list(geo_l)

    return geo_l

def proc_article(url, adminX, adminY, regex, yp):
    '''
    function downloads articles from urls provided by the bing search API.
    With the article data, runs a regex search over the article for tgt variables
    where the regexes are user-selected in the yaml and defined in the yaml module.
    Returns a dict with standard article information + dynamic keys,values determined 
    from the yaml search parameters.
    '''
    od = Odinson(yp)

    run_odinson = False
    for key in regex:
        outputFormat = regex[key]['outputformat']
        if outputFormat == 'extraction':
            run_odinson = True      
    
    try:
        article = Article(url)
        article.download()
        article.parse()

    except newspaper.article.ArticleException as e:
        logging.info(f'Exception for: {url}')  

    if article.publish_date:
        pub_date = article.publish_date.strftime('%m-%d-%Y %H:%M')
    else:
        pub_date = article.publish_date
    
        
    #Read article with created regexs to search for target variables     
    resultsDict = {}

    resultsDict = proc_regex(resultsDict, article.text, article.title, adminX, adminY, regex)
    
    # run Odinson if needed
    if run_odinson:
        resultsDict = proc_odinson(od, resultsDict, article.text)

    #Standard/Static keys
    stdDict = {'title': article.title, 'publish_date': pub_date, 
              'text': article.text, 'url': url}
    
    result = {**stdDict, **resultsDict}
        
    return result

def proc_regex(resultsDict, text, title, adminX, adminY, regex):
    #Read article with created regexs to search for target variables     
    run_odinson = False
    for key in regex:
        searchArticle = []
        tempDict = {}
        
        outputFormat = regex[key]['outputformat']
        inTitle = regex[key]['inTitle']
        compRegex = regex[key]['rgx'] 

        #Build article search dict
        if outputFormat == 'quantity':
            searchArticle = list(set([i[0] for i in compRegex.findall(text)]))
        
        if outputFormat == 'frequency':
            searchArticle = compRegex.findall(text)
            searchArticle = len(searchArticle)

        if outputFormat == 'extraction':
            searchArticle = []
        
        # Dump regex results into temp dict to later be added to resultsDict    
        tempDict.__setitem__(key, searchArticle)
    
        #True if we captured something useful
        dataCheck = bool([tgt for tgt in tempDict.values() if tgt != []])
        
        if dataCheck:
            # Filter dict build based on whether or not user wants geo in title
            if inTitle == True:
                if adminX.lower() in title.lower():
                    resultsDict.__setitem__(key, searchArticle)
                else:
                    resultsDict.__setitem__(key, 0)
                    
            if inTitle == False:
                resultsDict.__setitem__(key, searchArticle)

    return resultsDict  

def proc_odinson(od, resultsDict, text):
# Run article through Odinson / NLP search
    logf = open("logs/odin.log", "a")
    try: 
        searchArticle = od.process_text(text)
        logging.debug(f'Found Odin results {searchArticle}')
        
        for kk, vv in searchArticle.items():
            if vv != []:
                resultsDict.__setitem__(kk, vv)     
        
    except Exception as e:
        logging.error('Odin processing error for %s: %s', url, e)
        tm = datetime.datetime.now()
        tm = tm.strftime("%c")
        log_obj = dict(timestamp=tm, error=e, url=url, article=text)
        logf.write(json.dumps(log_obj)+'\n')    

    return resultsDict

def csvLook(wrkDir, jsonfile, csvoutfile):
# View the JSON output file in CSV format   
    t = pd.read_json(wrkDir + jsonfile, lines=True)
    t.to_csv(wrkDir + csvoutfile, sep=',', index=False, encoding='utf-8') 
    print(f'CSV File: {csvoutfile} written to {wrkDir}')
