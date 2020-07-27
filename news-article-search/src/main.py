#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JATAWARE

@author: travishartman
"""

#################### Imports ##################################################
import http.client, urllib.request, urllib.parse, urllib.error, base64
from odinson import Odinson_Docker
import bing_search_module as bsm
import functions_module as fn
from odinson import Odinson
import yaml_module as ym
from time import sleep
import spinner as sp
import oyaml as yaml
import pandas as pd
import configparser
import datetime
import requests
import argparse
import logging
import random
import http
import json
import sys
import os

################### COMMAND LINE RUN
# $ python3 src/main.py -r=results.json -geo=geo/test.csv -defs=user_search.yaml

################### COMMAND LINE ARGS
parser = argparse.ArgumentParser(description='Parse News for a given query')
parser.add_argument('-r', dest ='outfile', type=str, help='The location to store results')
parser.add_argument('-geo', dest = 'geoFile', type=str, help='Location of the geography csv')
parser.add_argument('-defs', dest = 'yamlFile', type=str, help='Location of user yaml file')

args = parser.parse_args()

outf = args.outfile
geoCsvFile  = args.geoFile 
userYaml = args.yamlFile

################### HARD CODE OUTFILE
# nice-to-have csv file that's easier than a json to inspect
outcsv = outf.split(".")[0]+ ".csv"

################### config.ini Read-in
wrkDir = os.getcwd()
wrkDir = wrkDir + '/' 
resultsDir = wrkDir + "results/"
logsDir = wrkDir + "logs/"

config = configparser.ConfigParser()
configFile = wrkDir + 'config.ini'
config.read(configFile)

################### set up logger event handling
userLevel = config['LOGGER']['logger_level']
logging.basicConfig(level= userLevel,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')

################### Get parameters and assign "searcher"
#Reference below:
# https://docs.microsoft.com/en-us/azure/cognitive-services/bing-web-search/quickstarts/python
# Set Bing parameters
params = dict(config.items('BING PARAMETERS'))

#Assign the Search API from the bing_search_module
searcher=bsm.bsearch

#Start Odinson Docker Container and delay to allow compile
odin = Odinson_Docker()
if odin.status() == False:
    odin.run()
    sleep(60)

##################### Read-in User Data 
# Pull in YAML with user-defined concept and target variables:
with open(r"" + userYaml) as f:
    yp = yaml.safe_load(f)

##################### Build inputs
# Classes from yaml_module
qc = ym.SearchParameters(yp)
rc= ym.Regex(yp)

queries = qc.BuildQuery()
regex = rc.CompileRegex()

geo_l = fn.FormatGeo(geoCsvFile)
od = Odinson(yp)

def run(q, params, outf):
#Run the regex search over the concept-target related news articles  
    
    # Verify the Odinson container is up
    if odin.status() == False:
        logging.info("Restarting Odinson")
        odin.run()
        sleep(60)

    for url in searcher(q, params):
        if url not in urls:
            urls.add(url)
            logging.debug(f'Getting {url}')
            try:
                #proc_article takes urls fom searcher and runs them thru regex
                processed = fn.proc_article(url, adminX, adminY, regex, yp)
                if processed:
                    #Add columns to the output file
                    processed['adminX'] = adminX
                    processed['adminY'] = adminY
                    processed['query'] = q
                    with open(os.path.join(resultsDir, outf), 'a') as f:
                        f.write(json.dumps(processed)+'\n')         
            except Exception as e:
                logging.error(e)
    sleep(30)
    
    return True

####################### Execute 
if __name__ == "__main__":

    urls = set()

    #Open logbook to capture all exceptions from main run	
    tm = datetime.datetime.now()
    tm = tm.strftime("%m.%d.%Y%.%H:%M")
    logFi = open(os.path.join(logsDir, tm + '_main.log'), 'a')	

    # Create set and write output to it
    queries_completed = set()
    if os.path.exists(f"results/{outf}"):
        with open(f"results/{outf}",'r') as f:
            for line in f:
                doc = json.loads(line.split('\n')[0])
                queries_completed.add(doc['query'])

    logging.debug("Queries completed: %s", queries_completed)
                
    # Add geo names to query, verify not already done, and dump into run function
    for adminX, adminY in geo_l:
        logging.debug(f"queries: {queries}")
        for q_ in queries:
            logging.debug(f"Searching {q_}")
            q = f'"{adminX}", {adminY}{q_}'
            if q not in queries_completed:
                queries_completed.add(q)
                success = False
                while success == False:
                    try:                        
                        try:
                            with sp.Spinner():
                                logging.info(f"Searching {q}")
                                success = run(q, params, outf)        

                        except urllib.error.HTTPError as e:
                            tm = datetime.datetime.now()
                            tm = tm.strftime("%c")
                            logFi.write(f"{tm}: {e} \n".format(str(tm), str(e))) 
                                    
                            if e.code == 429:
                                logging.error('Too many requests')
                       	
                            else:
                                logging.error(f'{e.code}: {e}')

                            # If error, let's not run the same query again
                            success = True
                                    
                    except Exception as e:
                        logging.error(e)
                        tm = datetime.datetime.now()
                        tm = tm.strftime("%c")
                        logFi.write(f"{tm}: {e} \n".format(str(tm), str(e)))   
            else:
                logging.debug("Skipping query: %s since it has already been processed.", q)
    logFi.close()

##################### Build Readable csv
# Create csv file in wrkDir to look at JSON file
fn.csvLook(resultsDir, outf, outcsv)


