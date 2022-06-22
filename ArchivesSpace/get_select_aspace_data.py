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

path = input("Enter full path to Desktop or whereever you wish to store the CSV file:")
baseURL = input("Enter baseURL for institution's Aspace instance:")
user_name = input("Provide Aspace api username:")
password = input("Provide Aspace api password:")
repo = input("Enter repo number:")
record_type = 'archival_objects'
auth = requests.post(baseURL + '/users/{}/login?password={}'.format(user_name, password)).json()
session = auth['session']
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
    'X-ArchivesSpace-Session': session, 'Content_Type': 'application/json'}
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
        writer.writerow({'ref_id': self.ref_id, 'ao_uri': self.uri, 'title': title, 'identifier': identifier, 'normalized_date': normalized_date, 'description': description, 'type_of_resource': '', 'genre': '', 'creator': '','subject': '', 'subject_name': '', 'subject_geographic':'','copyright_status': '', 'publication_status': '', 'source_series': source_series, 'source_subseries': source_subseries, 'source_otherlevel': source_otherlevel, 'source_container': source_container, 'source_collection_title': source_collection_title, 'source_collection_id': source_collection_ID, 'source_citation': source_citation, 'depositor': '', 'language': '', 'format': '', 'source_identifier': '', 'contributor': ''})

    def get_description(self):
        if self.notes != []:
            try:
                description = self.notes[0].get('subnotes')[0].get('content')
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

    def get_series(self):
        for ancestor in self.ancestor:
            level = ancestor.get('level')
            if level == 'series':
                series_r = requests.get(baseURL + ancestor.get('ref'), headers=headers).json()
                source_series = series_r.get('display_string')
                return source_series
            else:
                series = ''
                return series

    def get_subseries(self):
        for ancestor in self.ancestor:
            level = ancestor.get('level')
            if level == 'subseries':
                subseries_r = requests.get(baseURL + ancestor.get('ref'), headers=headers).json()
                source_subseries = subseries_r.get('display_string')
                return source_subseries
            else:
                subseries = ''
                return subseries

    def get_otherLevel(self):
        source_otherlevel_list = []
        for ancestor in self.ancestor:
            level = ancestor.get('level')
            if level != 'series' and 'subseries' and 'collection':
                otherlevel_r = requests.get(baseURL + ancestor.get('ref'), headers=headers).json()
                if otherlevel_r.get('display_string') != None:
                    source_otherlevel_list.append(otherlevel_r.get('display_string'))
                source_otherlevel = ';'.join(source_otherlevel_list)
                return source_otherlevel
            else:
                source_otherlevel = ''
                return source_otherlevel

    def get_containers(self):
        if self.instances != []:
            try:
                if self.instances[0]["sub_container"]['type_2']:
                    folder = self.instances[0]["sub_container"]['type_2'] + ' ' + \
                             self.instances[0]["sub_container"]['indicator_2']
                    top_container = requests.get(
                        baseURL + self.instances[0]["sub_container"]['top_container']['ref'],
                        headers=headers).json()
                    source_container = top_container['display_string'] + ', ' + folder
                    return source_container
                else:
                    top_container = requests.get(
                        baseURL + self.instances[0]["sub_container"]['top_container']['ref'],
                        headers=headers).json()
                    source_container = top_container['display_string']
                    return source_container
            except KeyError:
                try:
                    folder = self.instances[1]["sub_container"]['type_2'] + ' ' + \
                             self.instances[1]["sub_container"][
                                 'indicator_2']
                    top_container = requests.get(
                        baseURL + self.instances[1]["sub_container"]['top_container']['ref'],
                        headers=headers).json()
                    source_container = top_container['display_string'] + ', ' + folder
                    return source_container
                except:
                    source_container = ''
                    return source_container
            else:
                source_container = ''
                return source_container

csv_path = input("Enter name for CSV:")
csv_mode = input(
    'Are you opening and writing a new CSV or appending to an exisiting one?\nEnter w for new and a for appending:')
heirarchy = input('Is their heirarchy to this collection? y/n?:').lower()

##Nested archival objects
with open(path + '/{}.csv'.format(csv_path), mode=csv_mode) as csv_file:
    fieldnames = ['ref_id', 'ao_uri', 'title', 'identifier', 'normalized_date', 'normalized_date_qualifier',
                  'subject', 'subject_name', 'subject_geographic', 'description', 'type_of_resource', 'genre', 'creator', 'copyright_status',
                  'publication_status', 'source_collection_title', 'source_collection_id', 'source_series',
                  'source_subseries', 'source_otherlevel', 'source_container', 'source_citation', 'depositor',
                  'language', 'format', 'source_identifier', 'contributor']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

    if heirarchy == 'y':
        seriesORsubseries_num = input('Enter the series number or subseries number:')
        arg = input(
            "AllseriesORsubseries, true or false? Enter true only if you are getting all items from a subseries within a series or multiple subseries nested under a series."
            "\nIf you are attempting to get items directly under a series, select false:")
        #print(seriesORsubseries_num)
        for level in seriesORsubseries_num.split(' '):
            seriesORsuberies_level_endpoint = '/repositories/{}'.format(repo) + '/archival_objects/' + str(level)
            #print(level)

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
            if arg == 'true':
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
                        for count, value in enumerate(instance_type_list): #enumerate the instance list
                            if value == 'digital_object': # we only want to get do instances
                                do = requests.get(baseURL + i['instances'][count][value]['ref'], headers=headers).json() #then we get the DO
                                #print(json.dumps(do, indent=2))
                                ao_uri = do['linked_instances'][0]['ref'] #archival object for digital object
                                identifier = do['digital_object_id']
                                title = do['title']
                                ao_1 = archival_object(uri=ao_uri, ref_id=i.get('ref_id'), notes=i.get('notes'),
                                dates = i.get('dates'), ancestor = i.get('ancestors'), instances = i.get('instances'))

                                description = ao_1.get_description()
                                normalized_date = ao_1.get_date()
                                source_series = ao_1.get_series()
                                source_subseries = ao_1.get_subseries()
                                source_otherlevel = ao_1.get_otherLevel()
                                source_container = ao_1.get_containers()
                                ao_1.write_csv()
                            else:
                                continue
                        if "digital_object" not in instance_type_list:
                            title = i['title']
                            identifier = ''
                            ao_1 = archival_object(uri=i.get('uri'), ref_id=i.get('ref_id'), notes=i.get('notes'),
                                                   dates=i.get('dates'), ancestor=i.get('ancestors'), instances=i.get('instances'))

                            description = ao_1.get_description()
                            normalized_date = ao_1.get_date()
                            source_series = ao_1.get_series()
                            source_subseries = ao_1.get_subseries()
                            source_otherlevel = ao_1.get_otherLevel()
                            source_container = ao_1.get_containers()
                            ao_1.write_csv()
                        else:
                            continue

            else:
                children_endpoint = '/repositories/{}'.format(repo) + '/archival_objects/' + str(level) + '/children'
                ao = requests.get(baseURL + children_endpoint,
                                  headers=headers).json()  # request the json for each item (subseries or children) under the series
                for item in ao:  # looking at the items within the subseries
                    instance_type_list = []
                    for i in item['instances']:
                        instance_type_list.append(i['instance_type'])
                    for count, value in enumerate(instance_type_list): #enumerate the instance list
                        if value == 'digital_object': # we only want to get do instances
                            do = requests.get(baseURL + item['instances'][count][value]['ref'], headers=headers).json() #then we get the DO
                            #print(json.dumps(do, indent=2))
                            ao_uri = do['linked_instances'][0]['ref'] #archival object for digital object
                            identifier = do['digital_object_id']
                            title = do['title']
                            ao_1 = archival_object(uri=ao_uri, ref_id=item.get('ref_id'), notes=item.get('notes'),
                            dates = item.get('dates'), ancestor = item.get('ancestors'), instances = item.get('instances'))

                            description = ao_1.get_description()
                            normalized_date = ao_1.get_date()
                            source_series = ao_1.get_series()
                            source_subseries = ao_1.get_subseries()
                            source_otherlevel = ao_1.get_otherLevel()
                            source_container = ao_1.get_containers()
                            ao_1.write_csv()
                        else:
                            continue
                    if "digital_object" not in instance_type_list:
                        title = item['title']
                        identifier = ''
                        ao_1 = archival_object(uri=item.get('uri'), ref_id=item.get('ref_id'), notes=item.get('notes'),
                                               dates=item.get('dates'), ancestor=item.get('ancestors'), instances=item.get('instances'))

                        description = ao_1.get_description()
                        normalized_date = ao_1.get_date()
                        source_series = ao_1.get_series()
                        source_subseries = ao_1.get_subseries()
                        source_otherlevel = ao_1.get_otherLevel()
                        source_container = ao_1.get_containers()
                        ao_1.write_csv()
    else:
        collection_endpoint = input('Enter collection endpoint:')
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
            ao = requests.get(baseURL + child['record_uri'],
                              headers=headers).json()  # request the json for each item under the subseries
            instance_type_list = []
            for instance in ao['instances']:
                instance_type_list.append(instance['instance_type'])
            for count, value in enumerate(instance_type_list): #enumerate the instance list
                if value == 'digital_object': # we only want to get do instances
                    do = requests.get(baseURL + ao['instances'][count][value]['ref'], headers=headers).json() #then we get the DO
                    #print(json.dumps(do, indent=2))
                    ao_uri = do['linked_instances'][0]['ref'] #archival object for digital object
                    identifier = do['digital_object_id']
                    title = do['title']
                    ao_1 = archival_object(uri=ao_uri, ref_id=ao.get('ref_id'), notes=ao.get('notes'),
                    dates = ao.get('dates'), ancestor = ao.get('ancestors'), instances = ao.get('instances'))

                    description = ao_1.get_description()
                    normalized_date = ao_1.get_date()
                    source_series = ao_1.get_series()
                    source_subseries = ao_1.get_subseries()
                    source_otherlevel = ao_1.get_otherLevel()
                    source_container = ao_1.get_containers()
                    ao_1.write_csv()
                else:
                    continue
            if "digital_object" not in instance_type_list:
                title = ao['title']
                identifier = ''
                ao_1 = archival_object(uri=ao.get('uri'), ref_id=ao.get('ref_id'), notes=ao.get('notes'),
                                       dates=ao.get('dates'), ancestor=ao.get('ancestors'), instances=ao.get('instances'))

                description = ao_1.get_description()
                normalized_date = ao_1.get_date()
                source_series = ao_1.get_series()
                source_subseries = ao_1.get_subseries()
                source_otherlevel = ao_1.get_otherLevel()
                source_container = ao_1.get_containers()
                ao_1.write_csv()

print("Process complete!")
