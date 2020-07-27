from flask import Flask, render_template, request, redirect
from flask import send_from_directory
import json
import os
import urllib.request
import requests
import sys
import yaml

app = Flask(__name__)

static_file_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST', 'GET'])
def submit():
    print("Submission obtained....")
   
    #print(request.get_json())
    t = request.get_json()
    result = json.loads(t)
    
    #Set up structure and get file data to dump into
    wrkDir = os.getcwd()
    f = {}
    yaml_filename = result['header']['yaml_filename']

    if os.path.exists("/static/" + yaml_filename):
        os.remove(yaml_filename)
    else:
         print("The file does not exist")

    # YAML has two main keys, concept and target_variables
    f['concept'] = result['header']['concept'].splitlines()
    f['target_variables'] = {}

    # REGEX
    regexes = result['regex']
    for regex in regexes:
        if regex['column_label'] != "":

            # This is the column header and key for the subsetted target variables
            tgt_key = regex['column_label']
            temp_tgts ={}
            
            # ADD string/integer to yaml
            if regex['outputFormat'] == "frequency":
                tmp_matchType = "string"
            else:
                tmp_matchType = "integer"

            #Need to convert 'true' and 'false' from string to boolean
            inTitle_bool = (regex['inTitle'] == 'True')

            # Put it all together in a temp dict and add to wrapper dict    
            temp_tgts[tgt_key] ={'targets': regex['targets'].splitlines(),
                                 'outputFormat': regex['outputFormat'],
                                 'matchType': tmp_matchType, 
                                 'inTitle': inTitle_bool}

            f['target_variables'].update(temp_tgts)

    # ODIN    
    odins = result['odin']
    for odin in odins:
        if odin['odin_column_label'] != "":
            temp_tgts ={}    	
            tgt_key = odin['odin_column_label']
            
            inTitle_bool = (odin['inTitle'] == 'True')

            temp_tgts[tgt_key] ={'verbs': odin['verbs'].splitlines(), 
                                 'objects': odin['objects'].splitlines(),
                                 'outputFormat': 'extraction', 'matchType': 'verb-object', 
                                 'inTitle': inTitle_bool}

            f['target_variables'].update(temp_tgts)
  
    fname = wrkDir + '/static/' + yaml_filename
    with open(fname, 'w') as file:
        yaml.dump(f, file)

    return result

@app.route('/static/<path:path>', methods=['GET'])
def download(path):
    print('Request to download {}'.format(path))
    return send_from_directory(static_file_dir, path)    

if __name__ == '__main__':
    app.run()
