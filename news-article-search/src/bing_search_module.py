#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 14:06:16 2020

@author: travishartman
"""
import requests
import copy

def bsearch(queries, params):
    '''
    See url below for full list of available parameters:
    https://docs.microsoft.com/en-us/rest/api/cognitiveservices-bingsearch/bing-news-api-v7-reference
    '''
    
    # Use the Bing News Search API to get relevant urls to pass to Article()        
    headers = {"Ocp-Apim-Subscription-Key": params['subscription_key']}
    search_url = params[r'searchurl']
    
    #Copy dict to delete credentials and get just the parameters
    prms = copy.deepcopy(params)  
    del prms['subscription_key']
    del prms['searchurl']
    
    prms["q"] = queries
    
    response = requests.get(search_url, headers=headers, params=prms)
    response.raise_for_status()
    search_results = response.json()
    
    urls = [search_results['value'][i]['url'] for i in range(len(search_results['value']))]

    return urls

