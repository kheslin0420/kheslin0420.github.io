import requests
import json
import os
import csv
import pandas as pd
import glob
import xmltodict
from lxml import etree as ET
import traceback
from datetime import datetime
import re
from dateutil import parser
from collections import Counter


path = ''
baseURL = ''
user_name = ''
password = ''
repo = 
record_type = ''
auth = requests.post('https://pittapi.as.atlas-sys.com/users/{}/login?password={}'.format(user_name, password)).json()
session = auth['session']
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36', 'X-ArchivesSpace-Session': session, 'Content_Type': 'application/json'}
export_options = '?include_daos=true&numbered_cs=true&include_unpublished=false'

aspaceURL = 'https://pittstaff.as.atlas-sys.com/'


with open('.csv', mode='w') as csv_file:
    fieldnames = ['fa_url', 'accessrestrict_text']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    ead_export_param = {'include_daos' : 'true', 'numbered_cs' : 'true', 'include_unpublished': 'false'}
    ids = requests.get(baseURL + '/repositories/10/resources' + '?all_ids=true', headers=headers).json()
    for id in ids:
        a = requests.get(baseURL + '/repositories/10/resources/{}'.format(str(id)), headers=headers).json()
        for item in a['notes']:
            if item.get('type') == 'accessrestrict':
                if item['subnotes'][0]['content'].lower().strip() != 'no restrictions.': #or whatever string your institution uses to denote no access restrictions
                    fa_url = aspaceURL + 'resources/' + a['uri'].split('/')[-1]
                    writer.writerow({'fa_url': fa_url, 'accessrestrict_text': item['subnotes'][0]['content']})
                else:
                    pass
