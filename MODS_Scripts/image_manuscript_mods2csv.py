from lxml import etree as ET
import re
import glob
import csv
import pandas as pd

file_dir = input('Provide full directory path to XML files:')
list_of_files = glob.glob('{}/*.xml'.format(file_dir))

csv_name = input('Enter full pathname for csv:')

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

    def get_element_attrib(self):
        if root.find(self.xpath, namespaces) is not None:
            elementattrib = 'yes'
            return elementattrib

def your_while_generator(e):
    parent_list = []
    while e.getparent() != root:
        parent_list.append(e.getparent().tag.replace('{http://www.loc.gov/mods/v3}', ''))
        e = e.getparent()
    return parent_list

master_dict = []
for file in list_of_files:
    xmlObject = ET.parse(file)  # create an xml object that python can parse
    root = xmlObject.getroot()  # get the root of that object
    namespaces = {'mods': 'http://www.loc.gov/mods/v3'}  # define your namespace
    copyright_ns = {'copyrightMD': 'http://www.cdlib.org/inside/diglib/copyrightMD'}


    xml_dictionary = {}

    elements = {}
    for item in root.xpath('.//*'):
        #print(item)
        if item.getparent().tag != '{http://www.loc.gov/mods/v3}subject' and item.tag != '{http://www.loc.gov/mods/v3}subject':
            if item.text is not None:
                try:
                    elements.setdefault(item.tag + '/' + item.attrib.get('type'), []).append({item.text.replace('\n    ', '').replace('\n', '').strip() : [e for e in your_while_generator(item)]})
                except TypeError:
                    if item.text is not None:
                        elements.setdefault(item.tag, []).append({item.text.replace('\n    ', ' ').replace('\n', '').strip() : [e for e in your_while_generator(item)]})
                    else:
                        pass

    #print(elements) #['{http://www.loc.gov/mods/v3}subject']
    #print(elements['{http://www.loc.gov/mods/v3}topic'])

    for i in elements:
        for dict2 in elements[i]:
            for key in dict2:
                if key != '\n      ' and key != '\n         ':
                    if dict2[key] != []:
                        xml_dictionary.setdefault(i.replace('{http://www.loc.gov/mods/v3}', '') + '/' + dict2[key][-1] , []).append(key)
                    else:
                        xml_dictionary.setdefault(i.replace('{http://www.loc.gov/mods/v3}', ''), []).append(key)
    #print(xml_dictionary)

    xml_dict2 = {}

    for key2 in xml_dictionary:
        #print(xml_dictionary[key2])
        if '\n    ' in xml_dictionary[key2]:
            pass
        else:
            try:
                if key2 != 'namePart/name' and key2 != 'roleTerm/text/name' and xml_dictionary[key2][0] is not None:
                    xml_dict2.setdefault(key2, '; '.join(xml_dictionary[key2])) #removed [0] index from the end of this statement
                else:
                    pass
            except TypeError:
                pass

    for access_conditions in root.iterfind('mods:accessCondition', namespaces):
        for copyrights in access_conditions.iterfind('copyrightMD:copyright', copyright_ns):
            publication_status = copyrights.attrib['publication.status']
            copyright_status = copyrights.attrib['copyright.status']


    for subject in root.iterfind('mods:subject', namespaces):
        # print([child.text for child in subject.getchildren()])
        if subject.getchildren() != []:
            xml_dict2.setdefault(['subject_' + subject_type.tag.replace('{http://www.loc.gov/mods/v3}', '') for subject_type in subject.getchildren()][0], []).append(
                '--'.join([child.text for child in subject.getchildren() if child.text != '\n      ' and child.text is not None]))

    for key in xml_dict2: #get subjects for manuscripts and images
        if type(xml_dict2[key]) is list:
            xml_dict2[key] = '; '.join(xml_dict2[key])
        else:
            xml_dict2[key] = xml_dict2[key]


    contributor = ModsElement('.//mods:roleTerm', namespaces, 'contributor', text='contributor')
    creator = ModsElement('.//mods:roleTerm', namespaces, 'creator', text='creator')
    depositor = ModsElement('.//mods:roleTerm', namespaces, 'depositor', text='depositor')
    date_qualifier = ModsElement(".//mods:dateCreated[@qualifier='approximate'][@encoding='iso8601'][@keyDate='yes']", namespaces, 'date_qualifier')

    xml_dict2.setdefault('copyright_status', copyright_status)
    xml_dict2.setdefault('publication_status', publication_status)
    xml_dict2.setdefault('contributor', contributor.get_complex_element())
    xml_dict2.setdefault('creator', creator.get_complex_element())
    xml_dict2.setdefault('depositor', depositor.get_complex_element())
    xml_dict2.setdefault('normalized_date_qualifier', date_qualifier.get_element_attrib())

    master_dict.append(xml_dict2)

df = pd.DataFrame.from_dict(master_dict)
df.to_csv (csv_name, index = False, header=True)

new_csv = input('CSV has been created but headers need to be renamed and reindexed. Provide full pathname for new csv:')

fieldnames = ['title/titleInfo', 'creator', 'subject_geographic', 'subject_topic', 'namePart/subject', 'abstract', 'dateCreated/originInfo', 'normalized_date_qualifier','dateOther/display/originInfo',
             'dateOther/sort/originInfo', 'identifier/pitt', 'publication_status', 'copyright_status', '{http://www.cdlib.org/inside/diglib/copyrightMD}name/accessCondition','typeOfResource', 'languageTerm/code/language', 'title/relatedItem',
              'identifier/relatedItem', 'depositor', 'contributor', 'genre', 'form/physicalDescription', 'extent/physicalDescription', 'publisher/originInfo', 'note/prefercite/relatedItem', 'placeTerm/text/originInfo',
              'note/series/relatedItem', 'note/subseries/relatedItem', 'note/container/relatedItem']

df = pd.read_csv(csv_name) #===> Include the headers
correct_df = df.copy()
#print(df.columns.values)
for i in correct_df.columns.values:
    if i not in fieldnames:
        fieldnames.append(i)
    else:
        pass
df_reorder = correct_df.reindex(columns=fieldnames)
df_reorder.to_csv(new_csv, index=False, header=True)

new_df = pd.read_csv(new_csv)
correct_df2 = new_df.copy()
correct_df2.rename(columns={'title/titleInfo': 'title', 'typeOfResource': 'type_of_resource','publisher/originInfo': 'publisher','dateOther/display/originInfo': 'display_date','dateOther/sort/originInfo': 'sort_date',
'languageTerm/code/language': 'language', 'form/physicalDescription': 'format', 'extent/physicalDescription': 'extent', 'identifier/pitt' : 'identifier',
'title/relatedItem': 'source_collection', 'dateCreated/originInfo': 'normalized_date', 'note/prefercite/relatedItem': 'source_citation', 'identifier/relatedItem': 'source_collection_id', 'note/container/relatedItem': 'source_container',
'note/series/relatedItem': 'source_series', 'note/subseries/relatedItem': 'source_subseries', 'placeTerm/text/originInfo': 'pub_place',
'abstract': 'description', 'namePart/subject': 'subject_name', '{http://www.cdlib.org/inside/diglib/copyrightMD}name/accessCondition' : 'rights_holder'}, inplace=True)

#data cleaning
nan_value = float("NaN")
correct_df2.replace("", nan_value, inplace=True)
correct_df2.dropna(how='all', axis=1, inplace=True)
correct_df2.to_csv(new_csv, index=False, header=True)