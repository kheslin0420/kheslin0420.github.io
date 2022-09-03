from lxml import etree as ET
import sys
import glob
import os.path
import csv
import re


file_dir = input("Enter full path of directory where MODS live: ")
csv_name = input("Enter full path for new CSV: ")

class ModsElement:
    def __init__(self, xpath, namespace, elementname, **kwargs):
        self.xpath = xpath
        self.namespace = namespace
        self.elementname = elementname
        self.additional_args = kwargs

    def get_element_value(self):
        if root.find(self.xpath, namespaces) is not None:
            elementname = root.find(self.xpath, namespaces).text
            return elementname
        else:
            elementname = ''
            return elementname

    def get_complex_element(self):
        if 'text' in self.additional_args.keys():
            for element in root.iterfind(self.xpath, self.namespace):
                if element is not None and element.text == self.additional_args['text']:
                    elementname = element.getparent().getprevious().text
                    return elementname
                '''else:
                    elementname = ''
                    return elementname'''

    def get_element_attrib(self):
        if root.find(self.xpath, namespaces) is not None:
            elementattrib = 'yes'
            return elementattrib

list_of_files = glob.glob('{}/*.xml'.format(file_dir))

with open(csv_name, mode='w') as csv_file:
    fieldnames = ['title', 'identifier', 'description', 'subject_element', 'subject_value', 'date_display', 'sort_date', 'normalized_date_qualifier', 'date_digitized',
                  'normalized_date', 'language', 'creator', 'depositor', 'contributor', 'gift_of', 'genre', 'address',
                  'type_of_resource', 'format', 'extent', 'publisher', 'publication_status',
                  'copyright_status', 'source_id', 'source_citation', 'source_collection_id', 'source_collection_title',
                  'source_collection_date', 'pub_place', 'source_series', 'source_subseries', 'source_container']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

    for file in list_of_files:
        barcode = file.split('_')[1]
        xmlObject = ET.parse(file)  # create an xml object that python can parse
        root = xmlObject.getroot()  # get the root of that object
        namespaces = {'mods': 'http://www.loc.gov/mods/v3'}  # define your namespace
        copyright_ns = {'copyrightMD': 'http://www.cdlib.org/inside/diglib/copyrightMD'}

        title = ModsElement('mods:titleInfo/mods:title', namespaces, 'title')
        container_info = ModsElement(".//mods:note[@type='container']", namespaces, 'container')
        lang = ModsElement(".//mods:languageTerm[@type='code'][@authority='iso639-2b']", namespaces, 'language')
        abstract = ModsElement(".//mods:abstract", namespaces, 'description')
        pitt_ID = ModsElement(".//mods:identifier[@type='pitt']", namespaces, 'identifier')
        genre = ModsElement('mods:genre', namespaces, 'genre')
        source_id = ModsElement(".//mods:identifier[@type='source']", namespaces, 'source_id')
        contributor = ModsElement('.//mods:roleTerm', namespaces, 'contributor', text='contributor')
        creator = ModsElement('.//mods:roleTerm', namespaces, 'creator', text='creator')
        depositor = ModsElement('.//mods:roleTerm', namespaces, 'depositor', text='depositor')
        address = ModsElement(".//mods:note[@type='address']", namespaces, 'address')
        donor = ModsElement('.//mods:note[@type="donor"]', namespaces, 'gift_of')
        date_digitized = ModsElement('.//mods:dateCaptured', namespaces, 'date_digitized')
        normalizedDate = ModsElement(".//mods:dateCreated[@encoding='iso8601'][@keyDate='yes']", namespaces, 'normalized_date')
        date_qualifier = ModsElement(".//mods:dateCreated[@qualifier='approximate'][@encoding='iso8601'][@keyDate='yes']", namespaces, 'date_qualifier')
        display_date = ModsElement(".//mods:dateOther[@type='display']", namespaces, 'display_date')
        sort_date = ModsElement(".//mods:dateOther[@type='sort']", namespaces, 'sort_date')
        publisher = ModsElement('mods:originInfo/mods:publisher', namespaces, 'publisher')
        pub_place = ModsElement("mods:placeTerm[@type='text']", namespaces, 'pub_place')
        extent = ModsElement(".//mods:extent", namespaces, 'extent')
        form = ModsElement("mods:physicalDescription/mods:form", namespaces, 'format')
        source_collection_date = ModsElement("mods:relatedItem[@type='host']/mods:originInfo/mods:dateCreated", namespaces, 'source_collection_date')
        source_collection_title = ModsElement("mods:relatedItem/mods:titleInfo/mods:title", namespaces, 'source_collection_title')
        source_collection_id = ModsElement("mods:relatedItem[@type='host']/mods:identifier", namespaces, 'source_collection_id')
        prefercite = ModsElement(".//mods:note[@type='prefercite']", namespaces, 'prefercite')
        type_of_resource = ModsElement("mods:typeOfResource", namespaces, 'type_of_resource')
        source_series = ModsElement(".//mods:note[@type='series']", namespaces, 'series')
        source_subseries = ModsElement(".//mods:note[@type='subseries']", namespaces, 'subseries')
        subject_value = ModsElement('subject_value', namespaces, 'subjectValue')
        subject_element = ModsElement('subject_element', namespaces, 'subject_element')

        for access_conditions in root.iterfind('mods:accessCondition', namespaces):
            for copyrights in access_conditions.iterfind('copyrightMD:copyright', copyright_ns):
                publication_status = copyrights.attrib['publication.status']
                copyright_status = copyrights.attrib['copyright.status']


        writer.writerow({'title': title.get_element_value(),
                         'identifier': pitt_ID.get_element_value(), 'description': abstract.get_element_value(),
                         'subject_element': subject_element.get_element_value(), 'subject_value': subject_value.get_element_value(),
                         'date_display': display_date.get_element_value(), 'sort_date': sort_date.get_element_value(),
                         'normalized_date': normalizedDate.get_element_value(),
                         'normalized_date_qualifier': date_qualifier.get_element_attrib(),
                         'date_digitized': date_digitized.get_element_value(),
                         'language': lang.get_element_value(), 'gift_of': donor.get_element_value(),
                         'creator': creator.get_complex_element(), 'depositor': depositor.get_complex_element(),
                        'contributor': contributor.get_complex_element(), 'genre': genre.get_element_value(),
                         'address': address.get_element_value(),
                        'type_of_resource': type_of_resource.get_element_value(), 'format': form.get_element_value(),
                         'extent': extent.get_element_value(), 'publisher': publisher.get_element_value(),
                         'publication_status': publication_status,
                        'copyright_status': copyright_status, 'source_id': source_id.get_element_value(),
                         'source_citation': prefercite.get_element_value(),
                         'source_collection_id': source_collection_id.get_element_value(),
                        'source_collection_date': source_collection_date.get_element_value(),
                         'source_collection_title': source_collection_title.get_element_value(),
                         'pub_place': pub_place.get_element_value(), 'source_series': source_series.get_element_value(),
                         'source_subseries':source_subseries.get_element_value(), 'source_container':container_info.get_element_value()})

print('MODS flattened!')