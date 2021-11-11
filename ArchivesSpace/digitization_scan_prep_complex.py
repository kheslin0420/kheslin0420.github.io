##This script containes two functions used to collect metadata from archival objects stored in an ArchivesSpace resource record. nested_archivalObjects() can be used to collect the metadata for archival objects stored in levels of heirarchy (i.e. with series/subseries/recordgroups).
## unNested_aos() can be used to collect metadata for archival objects stored in a resource record without these same levels of heirarchy. 
##The spreadsheet produced is used in our scanning process and ingesting the digital surrogates into our digital repository
##It is also used to create DO representatons of the AO in archivesSpace.

import requests
import json
import os
import csv
import pandas as pd
import glob
import xmltodict
from lxml import etree as ET
import traceback


path = '/Users/usersname/Dir'
baseURL = 'institutions.aspace.url.com'
user_name = 'username'
password = 'password'
repo = 'NUM'
record_type = 'resources'
auth = requests.post('https://pittapi.as.atlas-sys.com/users/{}/login?password={}'.format(user_name, password)).json()
session = auth['session']
headers = {'X-ArchivesSpace-Session': session, 'Content_Type': 'application/json'}


def nested_archivalObjects(seriesORsubseries_num, csv_name,
                               **kwarg):  # provide the series or subseries number directly above children you want to create DAO for OR if you want to get all subseries provide all_subseries = 'true'
    with open(path + '/{}.csv'.format(csv_name), mode='w') as csv_file:
        fieldnames = ['ref_id', 'title', 'identifier', 'normalized_date', 'abstract', 'type_of_resource', 'genre', 'creator',
                      'source_collection_title', 'source_collection_id', 'source_series', 'source_subseries',
                      'source_otherlevel', 'source_container', 'source_citation']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        seriesORsuberies_level_endpoint = '/repositories/{}'.format(repo) + '/archival_objects/' + str(seriesORsubseries_num)
        a = requests.get(baseURL + seriesORsuberies_level_endpoint, headers=headers).json()
        # collection level metadata

        for ancestor in a['ancestors']:
            if ancestor['level'] == 'collection':
                collection = requests.get(baseURL + ancestor['ref'], headers=headers).json()
                # print(json.dumps(collection, indent=2))
                source_collection_title = collection['title']
                source_collection_ID_list = []
                for item in collection:
                    x = re.search('^id.\d$', item)
                    if x != None:
                        source_collection_ID_list.append(x.group())
                source_collection_ID = '.'.join([collection.get(item) for item in source_collection_ID_list])
                source_citation = collection['title'] + ', ' + collection['dates'][0][
                    'expression'] + ', ' + source_collection_ID + ', ' + 'Archives & Special Collections, University of Pittsburgh'

        # object metadata

        if kwarg.get('all_subseriesORfiles') == 'true':
            children_endpoint = seriesORsuberies_level_endpoint + '/children'
            ao = requests.get(baseURL + children_endpoint,
                              headers=headers).json()  # request the json for each item (subseries or children) under the series
            for item in ao:  # looking at the items within the subseries or series
                # print(item['uri'])
                child_list = requests.get(baseURL + item['uri'] + '/children',
                                          headers=headers).json()  # request the json for each item under the subseries
                for i in child_list:
                    instance_type_list = []
                    for instance in i['instances']:
                        instance_type_list.append(instance['instance_type'])
                    if "digital_object" in instance_type_list:
                        do = requests.get( baseURL + i['instances'][instance_type_list.index('digital_object')]['digital_object']['ref'], headers=headers).json()
                        identifier = do['digital_object_id']
                        title = i['title']
                        ref_id = i['ref_id']
                        abstract = ''
                        type_of_resource = ''
                        genre = ''
                        creator = ''
                        source_series = ''
                        source_subseries = ''
                        source_otherlevel_list = []
                        for ancestor in i.get('ancestors'):
                            level = ancestor.get('level')
                            if level == 'series':
                                series_r = requests.get(baseURL + ancestor.get('ref'), headers=headers).json()
                                source_series = series_r.get('display_string')
                            elif level == 'subseries':
                                subseries_r = requests.get(baseURL + ancestor.get('ref'), headers=headers).json()
                                source_subseries = subseries_r.get('display_string')
                            else:
                                otherlevel_r = requests.get(baseURL + ancestor.get('ref'), headers=headers).json()
                                if otherlevel_r.get('display_string') != None:
                                    source_otherlevel_list.append(otherlevel_r.get('display_string'))
                        source_otherlevel = ';'.join(source_otherlevel_list)
                        if i['instances'] != []:
                            try:
                                folder = i['instances'][0]['sub_container']['type_2'] + ' ' + \
                                         i['instances'][0]['sub_container'][
                                             'indicator_2']
                                top_container = requests.get(
                                    baseURL + i['instances'][0]['sub_container']['top_container']['ref'],
                                    headers=headers).json()
                                source_container = top_container['display_string'] + ', ' + folder
                            except KeyError:
                                folder = i['instances'][1]['sub_container']['type_2'] + ' ' + \
                                         i['instances'][1]['sub_container'][
                                             'indicator_2']
                                top_container = requests.get(
                                    baseURL + i['instances'][1]['sub_container']['top_container']['ref'],
                                    headers=headers).json()
                                source_container = top_container['display_string'] + ', ' + folder
                        else:
                            source_container = ''
                        if i['dates'] != []:
                            date = i['dates'][0]['expression'].replace('-', '/').lower()
                            if re.search('^[a-z]', date.lower()) and date != 'undated' and '/' not in date:
                                try:
                                    d = parser.parse(date)
                                    date = d.strftime("%Y-%m-%d")
                                except:
                                    date = date
                        else:
                            date = ''

                        writer.writerow(
                            {'ref_id': ref_id, 'title': title, 'identifier': identifier, 'normalized_date': date, 'abstract': abstract,
                             'genre': genre, 'type_of_resource': type_of_resource, 'creator': creator,
                             'source_series': source_series, 'source_subseries': source_subseries,
                             'source_otherlevel': source_otherlevel, 'source_container': source_container,
                             'source_collection_title': source_collection_title,
                             'source_collection_id': source_collection_ID, 'source_citation': source_citation})
                    else:
                        title = i['title']
                        identifier = ''
                        ref_id = i['ref_id']
                        abstract = ''
                        type_of_resource = ''
                        genre = ''
                        creator = ''
                        source_series = ''
                        source_subseries = ''
                        source_otherlevel_list = []
                        for ancestor in i.get('ancestors'):
                            level = ancestor.get('level')
                            if level == 'series':
                                series_r = requests.get(baseURL + ancestor.get('ref'), headers=headers).json()
                                source_series = series_r.get('display_string')
                            elif level == 'subseries':
                                subseries_r = requests.get(baseURL + ancestor.get('ref'), headers=headers).json()
                                source_subseries = subseries_r.get('display_string')
                            else:
                                otherlevel_r = requests.get(baseURL + ancestor.get('ref'), headers=headers).json()
                                if otherlevel_r.get('display_string') != None:
                                    source_otherlevel_list.append(otherlevel_r.get('display_string'))
                        source_otherlevel = ';'.join(source_otherlevel_list)
                        if i['instances'] != []:
                            try:
                                folder = i['instances'][0]['sub_container']['type_2'] + ' ' + \
                                         i['instances'][0]['sub_container'][
                                             'indicator_2']
                                top_container = requests.get(
                                    baseURL + i['instances'][0]['sub_container']['top_container']['ref'],
                                    headers=headers).json()
                                source_container = top_container['display_string'] + ', ' + folder
                            except KeyError:
                                folder = i['instances'][1]['sub_container']['type_2'] + ' ' + \
                                         i['instances'][1]['sub_container'][
                                             'indicator_2']
                                top_container = requests.get(
                                    baseURL + i['instances'][1]['sub_container']['top_container']['ref'],
                                    headers=headers).json()
                                source_container = top_container['display_string'] + ', ' + folder
                        else:
                            source_container = ''
                        if i['dates'] != []:
                            date = i['dates'][0]['expression'].replace('-', '/').lower()
                            if re.search('^[a-z]', date.lower()) and date != 'undated' and '/' not in date:
                                try:
                                    d = parser.parse(date)
                                    date = d.strftime("%Y-%m-%d")
                                except:
                                    date = date
                        else:
                            date = ''

                        writer.writerow(
                            {'ref_id': ref_id, 'title': title, 'identifier': identifier, 'normalized_date': date,
                             'abstract': abstract,
                             'genre': genre, 'type_of_resource': type_of_resource, 'creator': creator,
                             'source_series': source_series, 'source_subseries': source_subseries,
                             'source_otherlevel': source_otherlevel, 'source_container': source_container,
                             'source_collection_title': source_collection_title,
                             'source_collection_id': source_collection_ID, 'source_citation': source_citation})

        else:
            children_endpoint = '/repositories/{}'.format(repo) + '/archival_objects/' + str(seriesORsubseries_num) + '/children'
            ao = requests.get(baseURL + children_endpoint,
                              headers=headers).json()  # request the json for each item (subseries or children) under the series
            for item in ao:  # looking at the items within the subseries
                instance_type_list = []
                for i in item['instances']:
                    instance_type_list.append(i['instance_type'])
                if "digital_object" in instance_type_list:
                    do = requests.get(baseURL + item['instances'][instance_type_list.index('digital_object')]['digital_object']['ref'], headers=headers).json()
                    identifier = do['digital_object_id']
                    title = item['title']
                    ref_id = item['ref_id']
                    abstract = ''
                    type_of_resource = ''
                    creator = ''
                    genre = ''
                    source_series = ''
                    source_subseries = ''
                    source_otherlevel_list = []
                    for ancestor in item.get('ancestors'):
                        level = ancestor.get('level')
                        if level == 'series':
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
                    if item['instances'] != []:
                        try:
                            folder = item['instances'][0]['sub_container']['type_2'] + ' ' + \
                                     item['instances'][0]['sub_container'][
                                         'indicator_2']
                            top_container = requests.get(
                                baseURL + item['instances'][0]['sub_container']['top_container']['ref'],
                                headers=headers).json()
                            source_container = top_container['display_string'] + ', ' + folder
                        except KeyError:
                            folder = item['instances'][1]['sub_container']['type_2'] + ' ' + \
                                     item['instances'][1]['sub_container'][
                                         'indicator_2']
                            top_container = requests.get(
                                baseURL + item['instances'][1]['sub_container']['top_container']['ref'],
                                headers=headers).json()
                            source_container = top_container['display_string'] + ', ' + folder
                        else:
                            source_container = ''
                        if item['dates'] != []:
                            date = item['dates'][0]['expression'].replace('-', '/').lower()
                            if re.search('^[a-z]', date.lower()) and date != 'undated':
                                try:
                                    d = parser.parse(date)
                                    date = d.strftime("%Y-%m-%d")
                                except:
                                    date = date
                        else:
                            date = ''
                        writer.writerow(
                            {'ref_id': ref_id, 'title': title, 'identifier': identifier, 'normalized_date': date, 'abstract': abstract,
                             'genre': genre,
                             'type_of_resource': type_of_resource, 'creator': creator, 'source_series': source_series,
                             'source_subseries': source_subseries, 'source_otherlevel': source_otherlevel,
                             'source_container': source_container, 'source_collection_title': source_collection_title,
                             'source_collection_id': source_collection_ID, 'source_citation': source_citation})
                else:
                    title = item['title']
                    identifier = ''
                    ref_id = item['ref_id']
                    abstract = ''
                    type_of_resource = ''
                    creator = ''
                    genre = ''
                    source_series = ''
                    source_subseries = ''
                    source_otherlevel_list = []
                    for ancestor in item.get('ancestors'):
                        level = ancestor.get('level')
                        if level == 'series':
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
                    if item['instances'] != []:
                        try:
                            folder = item['instances'][0]['sub_container']['type_2'] + ' ' + \
                                     item['instances'][0]['sub_container'][
                                         'indicator_2']
                            top_container = requests.get(
                                baseURL + item['instances'][0]['sub_container']['top_container']['ref'],
                                headers=headers).json()
                            source_container = top_container['display_string'] + ', ' + folder
                        except KeyError:
                            folder = item['instances'][1]['sub_container']['type_2'] + ' ' + \
                                     item['instances'][1]['sub_container'][
                                         'indicator_2']
                            top_container = requests.get(
                                baseURL + item['instances'][1]['sub_container']['top_container']['ref'],
                                headers=headers).json()
                            source_container = top_container['display_string'] + ', ' + folder
                    else:
                        source_container = ''
                    if item['dates'] != []:
                        date = item['dates'][0]['expression'].replace('-', '/').lower()
                        if re.search('^[a-z]', date.lower()) and date != 'undated':
                            try:
                                d = parser.parse(date)
                                date = d.strftime("%Y-%m-%d")
                            except:
                                date = date
                    else:
                        date = ''
                    writer.writerow(
                        {'ref_id': ref_id, 'title': title, 'identifier': identifier, 'normalized_date': date, 'abstract': abstract,
                         'genre': genre,
                         'type_of_resource': type_of_resource, 'creator': creator, 'source_series': source_series,
                         'source_subseries': source_subseries, 'source_otherlevel': source_otherlevel,
                         'source_container': source_container, 'source_collection_title': source_collection_title,
                         'source_collection_id': source_collection_ID, 'source_citation': source_citation})
                    

def unNested_aos(collection_endpoint, csv_name):
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
