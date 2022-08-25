from lxml import etree as ET
import re
import csv

print('Provide full path to EAD: ')
EAD_path = input()
xmlObject = ET.parse(EAD_path)  # create an xml object that python can parse 
root = xmlObject.getroot() #get the root of that object  
NSMAP = root.nsmap
NS2_Namespace = "http://www.w3.org/1999/xlink"
NS2 = '{%s}' % NS2_Namespace

print('Provide full export path for csv: ')
CSV_path = input()

with open(CSV_path, mode='w') as csv_file:
    print('creating csv.....')
    fieldnames = ['title', 'creator', 'subject', 'subject_location', 'subject_name', 'description', 'normalized_date', 'normalized_date_qualifier', 'identifier', 'copyright_status', 'publication_status', 'rights_holder', 'type_of_resource', 'source_collection', 'depositor', 'genre', 'format', 'contributor', 'source_id', 'source_collection_id', 'source_citation', 'source_series', 'source_subseries', 'source_otherlevel', 'source_container', 'batch']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    ##collection level metadata
    print('parsing collection level metadata....')
    collection_title = ' '.join(root.find('archdesc/did/unittitle', NSMAP).text.split())
    collection_ID = root.find('archdesc/did/unitid', NSMAP).text
    source_citation = " ".join(root.find('.//prefercite/p', NSMAP).text.split())

    ##item level metadata
    print('parsing item level metadata...')
    source_series = ''
    source_subseries = ''
    source_otherlevel = ''
    abstract = ''
    for dao in root.findall('.//dao', NSMAP):
        title = dao.attrib[NS2 + 'title'].split()
        cleaned_title_list = []
        cleaned_title_list2 = []
        for word in title:
            cleaned_title_list.append(re.sub('^<emph>', '', word))
        for w in cleaned_title_list:
            cleaned_title_list2.append(re.sub('</emph>$', '', w))
        cleaned_title = ' '.join(cleaned_title_list2)
        item_identifier = dao.get(NS2 + 'href')
        for child in dao.getparent():
            #print(child.tag)
            if child.tag == '{urn:isbn:1-931666-22-9}unitdate':
                item_date = child.get('normal')
        item_container_list = ['{}, {}'.format(child.attrib['type'], child.text) for child in dao.getparent() if child.tag == '{urn:isbn:1-931666-22-9}container']
        item_container = ' '.join(item_container_list)

        did = dao.getparent()

        c0 = did.getparent()
        c0_list = list(c0)
        while c0.get('level') == 'file' or c0.get('level') == 'item':
            c0 = c0.getparent()
            if c0.get('level') == 'file':
                c0 = c0.getparent()
                if c0.get('level') == 'subseries' or c0.get('level') == 'subgrp':
                    subseries_title = c0.find('.//did/unittitle', NSMAP).text
                    subseries_unitid = c0.find('.//did/unitid', NSMAP)
                    if subseries_unitid is not None:
                        source_subseries = subseries_title + ' ' + subseries_unitid.text # changed from root.find to c0.find
                    else:
                        source_subseries = subseries_title
                    c0 = c0.getparent()
                elif c0.get('level') == 'otherlevel':
                    other_level_title = c0.find('.//did/unittitle', NSMAP).text
                    other_level_unitID = c0.find('.//did/unitid', NSMAP)
                    if other_level_unitID is not None:
                        source_otherlevel =  other_level_title + ' ' + other_level_unitID.text
                    else:
                        source_otherlevel = other_level_title
                elif c0.get('level') == 'series' or c0.get('level') == 'subgrp':
                    source_series_title = c0.find('.//did/unittitle', NSMAP).text
                    source_series_unitID = c0.find('.//did/unitid', NSMAP)
                    if source_series_unitID is not None:
                        source_series =  source_series_title+ ' ' + source_series_unitID.text
                    else:
                        source_series = source_series_title
                else:
                    break
            elif c0.get('level') == 'subseries' or c0.get('level') == 'subgrp':
                source_subseries_title = c0.find('.//did/unittitle', NSMAP).text
                source_subseries_unitID = c0.find('.//did/unitid', NSMAP)
                if source_subseries_unitID is not None:
                    source_subseries =  source_subseries_title + ' ' + source_subseries_unitID.text
                else:
                    source_subseries = source_subseries_title
                c0 = c0.getparent()
            elif c0.get('level') == 'series' or c0.get('level') == 'subgrp':
                source_series_title = c0.find('.//did/unittitle', NSMAP).text
                source_series_unitID = c0.find('.//did/unitid', NSMAP)
                if source_series_unitID is not None:
                    source_series =  source_series_title + ' ' + source_series_unitID.text
                else:
                    source_series = source_series_title
                #print(source_series)
            else:
                break

        for element in c0_list:
            cleaned_sc_list = []
            if re.search('.scopecontent', element.tag):
                for i in element.find('.//p', NSMAP).xpath('string()').split('\n'):
                    cleaned_sc_list.append(i.strip())
                abstract = ' '.join(cleaned_sc_list)
        writer.writerow({'title': cleaned_title, 'creator': '', 'subject': '', 'subject_location': '','subject_name': '', 'description': abstract, 'normalized_date': item_date, 'normalized_date_qualifier': '','identifier': item_identifier,'copyright_status': '','publication_status': '','rights_holder': '','type_of_resource': '','source_collection': collection_title,'depositor': '','genre': '','format': '','contributor': '','source_id': '','source_collection_id': collection_ID, 'source_citation': source_citation,'source_series': source_series,'source_subseries': source_subseries, 'source_otherlevel': source_otherlevel,'source_container': item_container,'batch':''})

print('Process complete!')
