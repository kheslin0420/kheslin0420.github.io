##delete digital objects using a reference to the ArchivalID

import requests
import json
import os
import csv
import pandas as pd
import glob
import xmltodict
from lxml import etree as ET
import traceback


path = '/Users/username/Dir'
baseURL = 'institutions.aspace.url.com'
user_name = 'username'
password = 'password'
repo = 'NUM'
record_type = 'resources'
auth = requests.post(baseURL + '/users/{}/login?password={}'.format(user_name, password)).json()
session = auth['session']
headers = {'X-ArchivesSpace-Session': session, 'Content_Type': 'application/json'}
ead_export_param = {'include_daos' : 'true', 'numbered_cs' : 'true'}

archival_objects_refIDs = {'ref_id[]': ['ref1595_4a0', 'ref1599_k6j']}

archival_objects_list = requests.get(baseURL + '/repositories/' + repo + '/' + 'find_by_id/archival_objects', params=archival_objects_refIDs, headers=headers).json()

for i in archival_objects_list['archival_objects']:
    ao_json = requests.get(baseURL + i["ref"], headers=headers).json()
    digital_object = ao_json['instances'][1]['digital_object']['ref']
    deletion_confirmation = requests.delete(baseUrl + digital_object, headers=headers).json()
    print(json.dumps(deletion_confirmation))
