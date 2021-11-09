from bs4 import BeautifulSoup
import requests
import os
import spacy
import pandas as pd
from lxml import etree as ET
from spacy.lang.en import English
from spacy.matcher import Matcher

nlp = English()

path = '/Users/kaylaheslin/Desktop/Digital Collection MODS'
namespaces = {'mods': 'http://www.loc.gov/mods/v3'}

file_audit = []
file_audit2 = []
terms_found = []
expression_matched = []

nlp = spacy.load('en_core_web_sm')
matcher = Matcher(nlp.vocab)
pattern1 = [{'TEXT': 'Afro'}, {'TEXT': 'American'}]
pattern2 = [{'TEXT': 'Native'}, {'TEXT': 'American'}]
matcher.add('', None, pattern1, pattern2)

for rootdir, subdir, file in os.walk(path):
    for f in file:
        xmlObject = ET.parse(os.path.join(path, f))  # create an xml object that python can parse
        root = xmlObject.getroot()

        newlist = []
        obj_titles = root.findall('mods:titleInfo/mods:title', namespaces)
        obj_descript = root.findall('mods:abstract', namespaces)
        for title in obj_titles:
            newlist.append(title.text)
        for description in obj_descript:
            newlist.append(description.text)

        string = ''

        doc = nlp(string.join(str(newlist)))
        # print(doc)
        matches = matcher(doc)
        # print('Total macthes found: ', len(matches))

        for match_id, start, end in matches:
            expression_matched.append(doc[start:end].text)
            file_audit2.append(f)

        list_tokens = []
        for token in doc:
            list_tokens.append(token.text.lower())

        harmful_terms = ['slave', 'slavery', 'homosexual', 'Mrs.', 'Mrs', 'indian', 'native', 'deviant',
                         'huns', 'Huns', 'Hunky', 'hunky', 'colored', 'negro', 'oriental', 'illegal', 'alien', 'redman',
                         'redskin', 'squaw', 'wop', 'blight', 'blacks', 'negro', 'mankind', 'manpower']

        for i in harmful_terms:
            # print(i)
            if i in list_tokens:
                # counter += 1
                file_audit.append(f)
                terms_found.append(i)
dict1 = {'files': file_audit, 'term_found': terms_found}
dict2 = {'files': file_audit2, 'expression_matched': expression_matched}

df = pd.DataFrame(dict1)
df2 = pd.DataFrame(dict2)

df.to_csv('/Users/kaylaheslin/Desktop/digital_obj_audit.csv')
df2.to_csv('/Users/kaylaheslin/Desktop/digital_obj_audit_matched_expressions.csv')
