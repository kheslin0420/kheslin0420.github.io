##This script is used to collect metadata for archival objects stored within a resource record with no heirarchy
## (i.e. they are not contained within a series/subseries/recordgroup). This metadata is collected as part of our digitization process
## and is used for ingest into our digital repository. This csv aslso serves to create DO representations of the AO 
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


collection_endpoint = ''
csv_name = ''

with open('/Users/username/Dir/{}.csv'.format(csv_name), mode='w') as csv_file:
    fieldnames = ['ref_id', 'title', 'identifier', 'normalized_date', 'normalized_date_qualifier', 'abstract', 'type_of_resource', 'genre',
                  'creator',
                  'subject','subject_name', 'copyright_status','copyright_status','publication_status','source_collection_title', 'source_collection_id', 'source_series', 'source_subseries',
                  'source_otherlevel', 'source_container', 'source_citation']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

    collection = requests.get(baseURL + collection_endpoint, headers=headers).json()
    source_collection_title = collection['title']
    source_collection_ID_list = []
    for item in collection:
        x = re.search('^id.\d$', item)
        if x != None:
            source_collection_ID_list.append(x.group())
    source_collection_ID = '.'.join([collection.get(item) for item in source_collection_ID_list])
    source_citation = collection['title'] + ', ' + collection['dates'][0][
        'expression'] + ', ' + source_collection_ID + ', ' + 'Archives & Special Collections, University of Pittsburgh'

    collection_tree = requests.get(baseURL + collection_endpoint + '/tree', headers=headers).json()

    for child in collection_tree['children']:
        ao = requests.get(baseURL + child['record_uri'], headers=headers).json()  # request the json for each item under the subseries
        title = ao['title']
        identifier = ''
        ref_id = ao['ref_id']
        abstract = ''
        type_of_resource = ''
        creator = ''
        genre = ''
        subject = ''
        subject_name = ''
        source_series = ''
        copyright_status = ''
        publication_status = ''
        source_subseries = ''
        source_otherlevel_list = []
        source_otherlevel = ''
        normalized_date_qualifier = ''
        for ancestor in ao.get('ancestors'):
            level = ancestor.get('level')
            if level == 'collection':
                continue
            elif level == 'series':
                series_r = requests.get(baseURL + ancestor.get('ref'), headers=headers).json()
                source_series = series_r.get('display_string')
            elif level == 'subseries':
                subseries_r = requests.get(baseURL + ancestor.get('ref'), headers=headers).json()
                source_subseries = subseries_r.get('display_string')
            else:
                other_level_r = requests.get(baseURL + ancestor.get('ref'), headers=headers).json()
                if other_level_r.get('display_string') != None:
                    source_otherlevel_list.append(other_level_r.get('display_string'))
            source_otherlevel = ';'.join(source_otherlevel_list)
        if ao['instances'] != []:
            try:
                folder = ao['instances'][0]['sub_container']['type_2'] + ' ' + ao['instances'][0]['sub_container']['indicator_2']
                top_container = requests.get(baseURL + ao['instances'][0]['sub_container']['top_container']['ref'],headers=headers).json()
                source_container = top_container['display_string'] + ', ' + folder
            except KeyError:
                folder = ao['instances'][1]['sub_container']['type_2'] + ' ' + ao['instances'][1]['sub_container']['indicator_2']
                top_container = requests.get(baseURL + ao['instances'][1]['sub_container']['top_container']['ref'],headers=headers).json()
                source_container = top_container['display_string'] + ', ' + folder
        else:
            source_container = ''
        if ao['dates'] != []:
            date = ao['dates'][0]['expression'].replace('-', '/').lower()
            if re.search('^[a-z]', date.lower()) and date != 'undated':
                try:
                    d = parser.parse(date)
                    date = d.strftime("%Y-%m-%d")
                except:
                    date = date
        else:
            date = ''
        writer.writerow(
                {'ref_id': ref_id, 'title': title, 'identifier': identifier, 'normalized_date': date, 'normalized_date_qualifier': normalized_date_qualifier, 'abstract': abstract,
                 'genre': genre,
                 'type_of_resource': type_of_resource, 'creator': creator, 'subject': subject,'subject_name': subject_name,'copyright_status': copyright_status,'publication_status': publication_status,'source_series': source_series,
                 'source_subseries': source_subseries, 'source_otherlevel': source_otherlevel,
                 'source_container': source_container, 'source_collection_title': source_collection_title,
                 'source_collection_id': source_collection_ID, 'source_citation': source_citation})
print("Process complete!")
