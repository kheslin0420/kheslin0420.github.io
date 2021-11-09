#production code starts here
from lxml import etree as ET
import sys
import glob
import os.path
import csv
import re

with open('/Users/username/Directory/generic_title.csv', mode='w') as csv_file:
    fieldnames =['title', 'identifier', 'abstract', 'date_display', 'sort_date', 'date_created', 'keyDate', 'encoding',  'normalized_date_qualifier', 'creator', 'depositor', 'contributor', 'gift_of', 'genre', 'address', 'type_of_resource', 'format', 'dimension', 'date_digitized', 'publisher', 'publication_status', 'copyright_status', 'source_id', 'source_citation', 'source_collection_id', 'reference_source_title', 'source_collection_date', 'pub_place', 'series', 'subseries', 'container', 'ownership', 'prefercite']

    list_of_files = glob.glob('/Users/username/Directory/subdir/*.xml')
    list_of_lcsh_subjects = []
    list_of_lcnaf_subjects = []
    list_of_aat_subjects = []
    for file in list_of_files:
        file_dictionary = {}
        barcode = file.split('_')[1]
        xmlObject = ET.parse(file)  # create an xml object that python can parse
        root = xmlObject.getroot()  # get the root of that object
        namespaces = {'mods': 'http://www.loc.gov/mods/v3'}  # define your namespace
        copyright_ns = {'copyrightMD': 'http://www.cdlib.org/inside/diglib/copyrightMD'}

        for i in root.findall('mods:subject', namespaces):
            if i.attrib['authority'] == 'lcsh':
                list_of_lcsh_subjects.append(root.findall('mods:subject', namespaces))
            if i.attrib['authority'] == 'lcnaf':
                list_of_lcnaf_subjects.append(root.findall('mods:subject', namespaces))
            if i.attrib['authority'] == 'aat':
                list_of_aat_subjects.append(root.findall('mods:subject', namespaces))

    lcsh_maxList = max(list_of_lcsh_subjects, key= lambda i: len(i))
    lcsh_maxLength = len(lcsh_maxList)
    for i in range(lcsh_maxLength):
        fieldnames.insert(-25, 'lcsh_subject.{}'.format(str(i).zfill(2)))
        fieldnames.insert(-25, 'lcsh_subject_type.{}'.format(str(i).zfill(2)))

    if list_of_lcnaf_subjects != []:
        lcnaf_maxList = max(list_of_lcnaf_subjects, key = lambda  i: len(i))
        lcnaf_maxLength = len(lcnaf_maxList)
    
        for i in range(lcnaf_maxLength):
            fieldnames.insert(-25, 'lcnaf_subject.{}'.format(str(i).zfill(2)))

    if list_of_aat_subjects != []:
        aat_maxList = max(list_of_aat_subjects, key= lambda  i: len(i))
        aat_maxLength = len(aat_maxList)

        for i in range(aat_maxLength):
            fieldnames.insert(-25, 'aat_subject.{}'.format(str(i).zfill(2)))

    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

    for file in list_of_files:
        file_dictionary = {}
        barcode = file.split('_')[1]
        xmlObject = ET.parse(file)  # create an xml object that python can parse
        root = xmlObject.getroot()  # get the root of that object
        namespaces = {'mods': 'http://www.loc.gov/mods/v3'}  # define your namespace
        copyright_ns = {'copyrightMD': 'http://www.cdlib.org/inside/diglib/copyrightMD'}


        for genre_element in root.iterfind('mods:genre', namespaces):
            genre = genre_element.text
            file_dictionary['genre'] = genre


        for description in root.iterfind('mods:abstract', namespaces):
            abstract = description.text
            file_dictionary['abstract'] = abstract


        for typeResource in root.iterfind('mods:typeOfResource', namespaces):
            type_of_resource = typeResource.text
            file_dictionary['type_of_resource'] = type_of_resource


        for b in root.iterfind('mods:note', namespaces):
            if b.attrib['type'] == 'address':
                address = b.text
                file_dictionary['address'] = address
            if b.attrib['type'] == 'donor':
                gift_of = b.text
                file_dictionary['gift_of'] = gift_of
            else:
                continue

        for roleterm in root.iterfind('mods:name/mods:namePart/mods:role/mods:roleTerm', namespaces):
            if roleterm.text == 'contributor':
                contributor = roleterm.text
                file_dictionary['contributor'] = contributor

        for roleterm in root.iterfind('mods:name/mods:namePart/mods:role/mods:roleTerm', namespaces):
            if roleterm.text == 'creator':
                creator = roleterm.text
                file_dictionary['creator'] = creator

        for roleterm in root.iterfind('mods:name/mods:namePart/mods:role/mods:roleTerm', namespaces):
            if roleterm.text == 'depositor':
                depositor = roleterm.text
                file_dictionary['depositor'] = depositor

        for itemID in root.iterfind('mods:identifier', namespaces):
            if itemID.attrib['type'] == 'pitt':
                identifier = itemID.text
                file_dictionary['identifier'] = identifier

        for item_id in root.iterfind('mods:identifier', namespaces):
            if itemID.attrib['type'] == 'source':
                source_id = itemID.attrib['type']
                file_dictionary['source_id'] = source_id

        for title in root.iterfind('mods:titleInfo/mods:title', namespaces):
            title_en = title.text
            file_dictionary['title'] = title_en

        for pub in root.iterfind('mods:originInfo/mods:publisher', namespaces):
            publisher = pub.text
            file_dictionary['publisher'] = publisher

        for date_dig in root.iterfind('mods:originInfo/mods:dateCaptured', namespaces):
            date_digitized = date_dig.text
            file_dictionary['date_digitized'] = date_digitized

        for resource_format in root.iterfind('mods:physicalDescription/mods:form', namespaces):
            format = resource_format.text
            file_dictionary['format'] = format
            
        counter1 = -1
        counter2 = -1
        for subject in root.iterfind('mods:subject', namespaces):
            if subject.attrib['authority'] == 'lcsh':
                counter1 += 1
                counter2 += 1
                file_dictionary['lcsh_subject.{}'.format(str(counter1).zfill(2))] = '|'.join([child.text for child in subject.iterchildren()])
                file_dictionary['lcsh_subject_type.{}'.format(str(counter2).zfill(2))] = '|'.join([child.tag[28:len(child.tag)] for child in subject.iterchildren()])
            if subject.attrib['authority'] == 'lcnaf':
                counter += 1
                file_dictionary['lcnaf_subject.{}'.format(str(counter).zfill(2))] = '|'.join([child.text for child in subject.iterchildren()])
            if subject.attrib['authority'] == 'aat':
                counter += 1
                file_dictionary['aat_subject.{}'.format(str(counter).zfill(2))] = '|'.join([child.text for child in subject.iterchildren()])

        for phys_desc in root.iterfind('mods:physicalDescription/mods:extent', namespaces):
            dimension = phys_desc.text
            file_dictionary = dimension

        for note in root.iterfind('mods:relatedItem/mods:note', namespaces):
            if note.attrib['type'] == 'prefercite':
                source_citation = note.text
                file_dictionary['source_citation'] = source_citation

        for relatedItem in root.iterfind('mods:relatedItem', namespaces):
            if relatedItem.attrib['type'] == 'host':
                for element in relatedItem.iterchildren():
                    if element.tag == '{http://www.loc.gov/mods/v3}identifier':
                        source_collection_id = element.text
                        file_dictionary['source_collection_id'] = source_collection_id

        for relatedItem in root.iterfind('mods:relatedItem', namespaces):
            if 'type' in relatedItem.attrib:
                if relatedItem.attrib['type'] == 'isReferencedBy':
                    for element in relatedItem.iterchildren():
                        if element.tag == '{http://www.loc.gov/mods/v3}titleInfo':
                            for child in element:
                                reference_source_title = child.text
                                file_dictionary['reference_source_title'] = reference_source_title

        for element_date in root.iterfind('mods:originInfo/mods:dateOther', namespaces):
            if element_date.attrib['type'] == 'sort':
                try:
                    sort_date = element_date.text
                    file_dictionary['sort_date'] = sort_date
                except TypeError:
                    file_dictionary['sort_date'] = 'failed to collect data'
            if element_date.attrib['type'] == 'display':
                try:
                    file_dictionary['date_display'] = element_date.text
                except TypeError:
                    file_dictionary['date_display'] = 'failed to collect data'

        for access_conditions in root.iterfind('mods:accessCondition', namespaces):
            for copyrights in access_conditions.iterfind('copyrightMD:copyright', copyright_ns):
                publication_status = copyrights.attrib['publication.status']
                file_dictionary['publication_status'] = publication_status
                copyright_status = copyrights.attrib['copyright.status']
                file_dictionary['copyright_status'] = copyright_status

        for placeTerm in root.iterfind('mods:originInfo/mods:place/mods:placeTerm', namespaces):
            pub_place = placeTerm.text
            file_dictionary['pub_place'] = pub_place

        for date_created in root.iterfind('mods:relatedItem/mods:originInfo/mods:dateCreated', namespaces):
            source_collection_date = date_created.text
            file_dictionary['source_collection_date'] = source_collection_date

        for norm_date in root.iterfind('mods:originInfo/mods:dateCreated', namespaces):
            if 'keyDate' in norm_date.attrib:
                keyDate = norm_date.attrib['keyDate']
                file_dictionary['keyDate'] = keyDate
            if 'encoding' in norm_date.attrib:
                encoding = norm_date.attrib['encoding']
                file_dictionary['encoding'] = encoding
            if 'qualifier' in norm_date.attrib:
                normalized_date_qualifier = norm_date.attrib['qualifier']
                file_dictionary['normalized_date_qualifier'] = normalized_date_qualifier

        for note in root.findall('mods:relatedItem/mods:note[@type]', namespaces):
            if note.get('type') == 'series':
                file_dictionary['series'] = note.text
            if note.get('type') == 'suberies':
                file_dictionary = note.text
            if note.get('type') == 'container':
                file_dictionary['container'] = note.text
            if note.get('type') == 'ownership':
                file_dictionary['ownership'] = note.text
            if note.get('type') == 'prefercite':
                file_dictionary['prefercite'] = note.text

        for dateCreated in root.findall('mods:originInfo/mods:dateCreated', namespaces):
            dateCreate_text = dateCreated.text
            file_dictionary['date_created'] = dateCreate_text

        writer.writerow(file_dictionary)

print("Process complete. CSV has been created!")