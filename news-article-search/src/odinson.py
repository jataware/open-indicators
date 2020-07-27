from nltk.stem import PorterStemmer
from copy import deepcopy
import oyaml as yaml
import requests
import logging
import docker
import json
import re
import os


yaml.SafeDumper.org_represent_str = yaml.SafeDumper.represent_str

def repr_str(dumper, data):
    if '\n' in data:
        return dumper.represent_scalar(u'tag:yaml.org,2002:str', data, style='|')
    return dumper.org_represent_str(data)

yaml.add_representer(str, repr_str, Dumper=yaml.SafeDumper)

ps = PorterStemmer()

class Odinson:
    def __init__(self, targets):       
        self.targets = targets.get('target_variables',{})
        self.rules_shell = self.load_rule_shell()
        self.rules = []
        self.process_targets()
        self.write_tmp_rules()

    def load_rule_shell(self):
        with open("src/odinson-rules/rules.yaml") as f:
            return yaml.safe_load(f)
    
    def process_targets(self):
        for kk, vv in self.targets.items():
            if vv.get('matchType', '') == 'verb-object':
                verbs = [ps.stem(verb) for verb in vv['verbs']]
                objects = vv['objects']
                self.update_rules(kk,verbs,objects)
    
    def update_rules(self, target_name, verbs, objects):
        r = deepcopy(self.rules_shell['rules'])
        for r_ in r:
            v_ = '.*|'.join(verbs) + '.*'
            o_ = '/' + '|'.join(objects) + '/'
            r_['pattern'] = r_['pattern'].replace('verb.*',v_)
            r_['pattern'] = r_['pattern'].replace('/object/',o_)
            r_['name'] = f"{target_name}_{r_['name']}"
            self.rules.append(r_)
    
    def write_tmp_rules(self):
        with open("src/odinson-rules/tmp-rules.yaml", "w") as file:
            yaml.safe_dump(dict(rules=self.rules), file)
            
    def process_text(self, text):
        evidences = {}
        for kk, vv in self.targets.items():
            if vv.get('matchType', '') == 'verb-object':
                evidences[kk] = []
        wrkDir = os.getcwd()
        headers = {'Content-Type': 'application/json'}
        data = {"rulefile":f"/root/rules/tmp-rules.yaml","text":text}
        response = requests.post('http://localhost:9000/process_text', headers=headers, data=json.dumps(data))
        results = response.json()
        if results != [[]]:
            for r in results[0]:
                ev = json.loads(r)
                for k in evidences.keys():
                    if k.lower() in ev['foundBy'].lower():
                        evidences[k].append(ev['evidence']['sentence'])
        return evidences
    
class Odinson_Docker:
    """
    Instantiates an object to start an Odinson container that connects to UofA Odinson API 
    container "hard-coded" NAME=odinson...allows for easier reset of container if/when connection fails
    """
    def __init__(self, name='odinson'):
        self.memory = '8g'
        self.name = name
        self.wrkDir = os.getcwd()
        self.ports = {"9000/tcp": 9000}
        self.client = docker.from_env()
        self.containers = self.client.containers
        self.volumes = { f"{self.wrkDir}/src/odinson-rules": {'bind': '/root/rules', 'mode': 'rw'}}

    def run(self):
        # get container and stop/remove it if necessary
        try:
            c = self.containers.get(self.name)
            # stop it
            c.stop()
            # remove it
            c.remove()
        except docker.errors.NotFound:
            pass

        logging.info(f'Starting: {self.name}') 
        c = self.containers.run("brandomr/odinsonwebapp",
                                restart_policy={"Name": "always"}, 
                                volumes=self.volumes, 
                                ports= self.ports,
                                detach=True, 
                                name = self.name,
                                tty=True,
                                stdin_open=True,
                                mem_limit=self.memory)

        return print(c.id)

    def status(self):
        # get container
        try:
            c = self.containers.get(self.name)
            return True
        except docker.errors.NotFound:
            logging.error("container not found.")
            return False