from lxml import etree as ET
from spacy.lang.en import English
nlp = English()
import os

path = 'path/to/directory/containing/findingaids'
ns = {'schema_loc' :'urn:isbn:1-931666-22-9 http://www.loc.gov/ead/ead.xsd',
'ns2' : 'http://www.w3.org/1999/xlink',
'urn' : 'urn:isbn:1-931666-22-9',
'xsi' : 'http://www.w3.org/2001/XMLSchema-instance'}

audit = []
for rootdir, subdir, file in os.walk(path):
    for f in file:
        #print(f)
        '''try:
            tree = ET.parse(os.path.join(path, f))
        except Exception:
            print('Skipping invalid XML from URL {}'.format(f))
            continue  # go on to the next URL''' #this is an exception initially created to handle an error occuring on my Mac based 
            #system. In my directory a .DS_store file kept throwing an error. This is unnecessary for window based systems and might
            #not be necessary for your Mac. Attempt the script without it first.'''
        parser = ET.XMLParser(recover=True, attribute_defaults=True, ns_clean=True, huge_tree=True, dtd_validation=True)
        lxmlobject = ET.parse(os.path.join(path, f), parser=parser)
        root = lxmlobject.getroot()
        #print(root)
        newlist = []
        bioghist = root.findall('archdesc/bioghist/p')
        scopecontent = root.findall('archdesc/scopecontent/p')
        for p in bioghist:
            #print(p.text)
            newlist.append(p.text)
        for p in scopecontent:
            #print(p.text)
            newlist.append(p.text)

        bioghist_string = ''

        doc = nlp(bioghist_string.join(str(newlist)))

        #print(doc)

        #first_token = doc[0]
        #print(first_token.text)

        list_tokens = []
        for token in doc:
            list_tokens.append(token.text)
        #print(list_tokens)

        harmful_terms = ['slave', 'slavery', 'homosexual', 'Mrs.', 'Mrs', 'indian', 'Indian', 'Native', 'deviant', 'huns', 'Huns', 'Hunky', 'hunky', 'colored', 'negro', 'oriental', 'illegal', 'alien', 'redman', 'redskin', 'squaw', 'wop', 'blight', 'blacks']
        for i in harmful_terms:
        #print(i)
            if i in list_tokens:
                #counter += 1
                item_to_audit = "The following term is found in {}: {}".format(f, i)
                audit.append(item_to_audit)
print(audit)


