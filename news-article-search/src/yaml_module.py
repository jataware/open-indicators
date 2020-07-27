#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 16 14:03:31 2020

@author: travishartman
"""

import oyaml as yaml
import pandas as pd
import logging
import re

# Dict to lookup the regex pattern based on user yaml selection
regexPattern = { 'integer': [ "(\d[0-9,]+\s(" , "))" ], 
                 'string': [ r'\b(\w*(' , r')\w*)\b' ]}  

class SearchParameters(object):
    '''
    Build the query list to be sent to the news search api. Takes in loaded yaml 
    file, parses yaml concept/tgt variable data as well as data handling requests
    and returns a list of strings to be sent into the searcher.
    '''    
    def __init__(self, params):
        self.params = params

    # Pull out just the concept information, return list of formatted concepts
    def conL(self):
    # from .yaml file: read-in all CONCEPT variables and add joiners
        conceptList = [con for con in self.params['concept']]
        
        qListCon=[]
        for con in conceptList:
            con = f'"{con}"'
            qListCon.append(con)
        qListCon = " OR ".join(qListCon)
        qListCon = "({})".format(qListCon)

        return qListCon

    # Pull out just the tgt vars information, return list of all formatted tgt vars
    def tgtL(self):
    # from .yaml file: read-in all TARGET variables     
        tgtList = []
        for key in self.params['target_variables'].keys():
            tempList = []
            tempList = [tgt for tgt in self.params['target_variables'][key].get('targets', '') if tgt != '']
            if tempList != []:
                tgtList.append(tempList)

        qListTgt = []
        for tgtList in tgtList:
            temp = []
            for tgt in tgtList:
                tgt = f'"{tgt}"'
                temp.insert(0, tgt)

            temp = " OR ".join(temp)
            temp= "({})".format(temp)
            qListTgt.append(temp)

        return qListTgt   

    # merge concept and tgt lists. Churns tgt variables around static concepts
    # Does not include geo data which is added in the main.py
    def BuildQuery(self):
    
        #Build the queries
        queries = []
        qCon = self.conL()

        for qTgt in self.tgtL():
            temp= []
            temp.append(qCon)
            temp.append(qTgt)
            temp.insert(0, "")
            temp = " AND ".join(temp)

            queries.append(temp)  

        return queries    

class Regex(object):
    '''
    Build the regex dict to be sent to the proc_article function. Takes in loaded yaml 
    file, parses yaml concept/tgt variable data ands wraps the parsed data within
    a regex as decided by the user in the yaml file.
    '''
    def __init__(self, params):
        self.params = params

    def RegexList(self):
    # from .yaml file: build and compile the regexes and tack on "regexType" wanted

        tgtVars = list(self.params['target_variables'].keys())
        
        # BUILD REGEX    
        regexList =[]
        for key in tgtVars:
            matchtype = self.params['target_variables'][key]['matchType']
            tempList =[]
            if matchtype in ['integer','string']:
                regexType = regexPattern[matchtype]
                pre = regexType[0]
                post =regexType[1]

                # tempList.append(pre)
                # add on the alternate target variables (key = Primary tgt variable)
                for tgts in self.params['target_variables'][key]['targets']:
                    tempList.append(tgts)
                    
                # Put it all together
                tempList = pre + '|'.join(tempList)
                tempList = tempList + post

                regexList.append(tempList)

            else:
                regexList.append(None)

        return regexList    

   # COMPILE REGEX  
    def CompileRegex(self):
    # Compile the regexes into a dictionary
        regexList = self.RegexList()

        #Get the keys to iterate through
        tgtVars = list(self.params['target_variables'].keys())
            
        re_compiledDict={}
        i = 0
        while i < len(regexList):
            if regexList[i] != None:
                re_compiledDict[tgtVars[i]] = re.compile(regexList[i],flags = re.I) 
            i += 1

        # Build dict with compiled regex, and user-selected countType and inTitle filter
        for key in tgtVars:
            matchtype = self.params['target_variables'][key]['matchType'] 
            outputFormat = self.params['target_variables'][key]['outputFormat']
            inTitle = self.params['target_variables'][key]['inTitle']
            if matchtype in ['integer','string']:
                re_compiledDict[key]=dict(rgx=re_compiledDict[key], outputformat = outputFormat, inTitle=inTitle)
            elif matchtype == 'verb-object':
                re_compiledDict[key]=dict(rgx=None, outputformat = outputFormat, inTitle=inTitle)
        return re_compiledDict