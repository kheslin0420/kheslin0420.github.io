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

path = '/Users/kaylaheslin/Desktop'
baseURL = 'https://pittsbapi.as.atlas-sys.com'
user_name = ''
password = ''
repo = input('Enter the Aspace repo number: ')
record_type = 'archival_objects'
auth = requests.post('https://pittsbapi.as.atlas-sys.com/users/{}/login?password={}'.format(user_name, password)).json()
if auth != {'error': 'Login failed'}:
    print('Login successful')
    session = auth['session']
    headers = {'X-ArchivesSpace-Session': session, 'Content_Type': 'application/json'}
    export_options = '?include_daos=true&numbered_cs=true&include_unpublished=false'

    class archival_object:
        def __init__(self, uri, ref_id, notes, dates, ancestor, instances):
            self.uri = uri
            self.ref_id = ref_id
            self.notes = notes
            self.dates = dates
            self.ancestor = ancestor
            self.instances = instances

        def write_csv(self):
            writer.writerow({'ref_id': self.ref_id, 'ao_uri': self.uri, 'title': title, 'identifier': identifier, 'normalized_date': normalized_date, 'description': description, 'type_of_resource': '', 'genre': '', 'creator': '','subject_topic': '', 'subject_name': '', 'subject_geographic':'','copyright_status': '', 'publication_status': '', 'source_series': source_series, 'source_subseries': source_subseries, 'source_other_level': source_otherlevel, 'source_container': source_container, 'source_collection': source_collection_title, 'source_collection_id': source_collection_ID, 'source_citation': source_citation, 'depositor': '', 'language': '', 'format': '', 'source_identifier': '', 'contributor': ''})

        def get_description(self):
            if self.notes != []:
                try:
                    description = self.notes[0].get('subnotes')[0].get('content').replace('\n', ' ')
                    return description
                except:
                    description = ''
                    return description
            else:
                description = ''
                return description

        def get_date(self):
            if self.dates != []:
                date_expression = self.dates[0].get('expression').replace('-', '/').lower()
                if re.search('^[a-z]',
                             date_expression.lower()) and date_expression != 'undated' and '/' not in date_expression:
                    try:
                        d = parser.parse(date_expression)
                        date = d.strftime("%Y-%m-%d")
                        return date
                    except:
                        date = date_expression
                        return date
                else:
                    date = date_expression
                    return date

        def get_heirarchy(self):
            heirarchy_list = []
            source_otherlevel_list = []
            for ancestor in self.ancestor:
                level = ancestor.get('level')
                if level == 'series':
                    series_r = requests.get(baseURL + ancestor.get('ref'), headers=headers).json()
                    source_series = series_r.get('display_string')
                    heirarchy_list.insert(0, source_series)
                else:
                    series = ''
                    heirarchy_list.insert(0, series)
                if level == 'subseries':
                    subseries_r = requests.get(baseURL + ancestor.get('ref'), headers=headers).json()
                    source_subseries = subseries_r.get('display_string')
                    heirarchy_list.insert(1, source_subseries)
                else:
                    subseries = ''
                    heirarchy_list.insert(1, subseries)
                if level != 'series' and 'subseries' and 'collection':
                    otherlevel_r = requests.get(baseURL + ancestor.get('ref'), headers=headers).json()
                    if otherlevel_r.get('display_string') != None:
                        source_otherlevel_list.append(otherlevel_r.get('display_string'))
                    source_otherlevel = ';'.join(source_otherlevel_list)
                    heirarchy_list.insert(2, source_otherlevel)
                else:
                    source_otherlevel = ''
                    heirarchy_list.insert(2, source_otherlevel)
            return(heirarchy_list)


        def get_containers(self):
            if self.instances != []:
                try:
                    if self.instances[0]["sub_container"]['type_2']:
                        folder = self.instances[0]["sub_container"]['type_2'] + ' ' + \
                                 self.instances[0]["sub_container"]['indicator_2']
                        top_container = requests.get(
                            baseURL + self.instances[0]["sub_container"]['top_container']['ref'],
                            headers=headers).json()
                        source_container = top_container['type'] + ' ' + top_container['indicator'] + ', ' + folder
                        return source_container
                    else:
                        top_container = requests.get(
                            baseURL + self.instances[0]["sub_container"]['top_container']['ref'],
                            headers=headers).json()
                        source_container = top_container['type'] + ' ' + top_container['indicator']
                        return source_container
                except KeyError:
                    try:
                        folder = self.instances[1]["sub_container"]['type_2'] + ' ' + \
                                 self.instances[1]["sub_container"][
                                     'indicator_2']
                        top_container = requests.get(
                            baseURL + self.instances[1]["sub_container"]['top_container']['ref'],
                            headers=headers).json()
                        source_container = top_container['type'] + ' ' + top_container['indicator'] + ', ' + folder
                        return source_container
                    except:
                        source_container = ''
                        return source_container
                else:
                    source_container = ''
                    return source_container

    csv_path = input("Enter name for CSV (only the name. The '.csv' extension will be applied when saving the file to your Desktop):")
    csv_mode = input('Are you opening and writing a new CSV or appending to an exisiting one?\nEnter w for new and a for appending:')
    resource_record_id = input('Enter the resource record ID (numnber only):')

    ordered_records = requests.get(baseURL + r'/repositories/{}/resources/{}/ordered_records'.format(repo, resource_record_id), headers=headers).json()
    
    print("There are {} ordered records in this finding aid (this is not the number of digital objects). The script must parse through each orded record to find all digital objects. if the number of ordered record is greater than 100, this may take some time. You woulld receive confirmation of a completed process at the end.".format(len(ordered_records)))

    digital_objects = []
    with open(csv_path, mode=csv_mode, newline='', encoding='utf=8') as csv_file:
        fieldnames = ['ref_id', 'ao_uri', 'title', 'identifier', 'normalized_date', 'normalized_date_qualifier',
                      'subject_topic', 'subject_name', 'subject_geographic', 'description', 'type_of_resource', 'genre', 'creator', 'copyright_status',
                      'publication_status', 'source_collection', 'source_collection_id', 'source_series',
                      'source_subseries', 'source_other_level', 'source_container', 'source_citation', 'depositor',
                      'language', 'format', 'source_identifier', 'contributor']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for uri in ordered_records['uris']:
            #print(uri)
            if uri['level'] =='item' or uri['level'] == 'file':
                ref = requests.get(baseURL + uri['ref'], headers=headers).json()
                #print(ref)
                for i in ref['instances']:
                    if i.get('digital_object') is not None:
                        do = requests.get(baseURL + i.get('digital_object')['ref'], headers=headers).json()
                        #print(do)
                        identifier = do['digital_object_id']
                        title = re.sub('<(?=\w)\w+\s\w+\S\S\w+\S>|<\S\w+>', '', do['title'].strip())
                        ao = requests.get(baseURL + do['linked_instances'][0]['ref'], headers=headers).json()
                        ao_1 = archival_object(uri=ao['uri'], ref_id=ao.get('ref_id'), notes=ao.get('notes'),
                                               dates=ao.get('dates'), ancestor=ao.get('ancestors'),
                                               instances=ao.get('instances'))

                        description = re.sub('<(?=\w)\w+\s\w+\S\S\w+\S>|<\S\w+>', '', ao_1.get_description())
                        normalized_date = ao_1.get_date()
                        source_series = ao_1.get_heirarchy()[0]
                        source_subseries = ao_1.get_heirarchy()[1]
                        source_otherlevel = ao_1.get_heirarchy()[2]
                        source_container = ao_1.get_containers()

                        #print(description, normalized_date, source_series)

                        for ancestor in ao['ancestors']:
                            if ancestor['level'] == 'collection':
                                collection = requests.get(baseURL + ancestor['ref'], headers=headers).json()
                                source_collection_title = collection['title']
                                source_collection_ID_list = []
                                for item in collection:
                                    x = re.search('^id.\d$', item)
                                    if x != None:
                                        source_collection_ID_list.append(x.group())
                                        source_collection_ID = '.'.join([collection.get(item) for item in source_collection_ID_list])
                                        source_citation = collection['title'] + ', ' + collection['dates'][0]['expression'] + ', ' + source_collection_ID + ', ' + 'Archives & Special Collections, University of Pittsburgh'

                        ao_1.write_csv()

else:
    print('Authentication failed. Check username and password')