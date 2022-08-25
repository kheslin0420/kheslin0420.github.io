import requests
import json
import os
import csv
import xmltodict
import traceback

path = '/Users/username/Desktop'
baseURL = 'institution's.baseURL.for.aspace'
user_name = 'username'
password = 'password'
repo = 'NUM'
auth = requests.post(baseURL + '/users/{}/login?password={}'.format(user_name, password)).json()
session = auth['session']
headers = {'X-ArchivesSpace-Session': session, 'Content_Type': 'application/json'}

with open('/Users/username/Dir/EAD_BulkErrorReport.csv', mode='w') as csv_file:
    fieldnames = ['resource_record#', 'traceback_error']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    ead_export_param = {'include_daos' : 'true', 'numbered_cs' : 'true'}
    ids = requests.get(baseURL + '/repositories/' + repo + '/' + 'resources' + '?all_ids=true', headers=headers).json()
    for id in ids:
        ead = requests.get(baseURL + '/repositories/' + repo + '/' + 'resource_descriptions/' + '{}.xml'.format(str(id)), params=ead_export_param, headers=headers)
        try:
            obj = xmltodict.parse(ead.content)
            with open('/Users/username/Dir/BULK_Aspace_EAD_Export/{}.xml'.format(obj['ead']['eadheader']['eadid']['#text']), 'wb') as f:
                f.write(ead.content)
        except KeyError:
            obj = xmltodict.parse(ead.content)
            with open('/Users/username/Dir/BULK_Aspace_EAD_Export/{}.xml'.format(obj['ead']['eadheader']['filedesc']['titlestmt']['titleproper']['num']), 'wb') as f:
                f.write(ead.content)
        except:
            resource_record = 'resources/{}#tree::resource_{}'.format(str(id), str(id))
            error_message = traceback.format_exc()

        writer.writerow({'resource_record#': resource_record, 'traceback_error': error_message})
