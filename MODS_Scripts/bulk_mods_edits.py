from lxml import etree as ET
import glob
import os.path

list_of_files = glob.glob('/Users/username/Directory/subdir/*.xml')
for file in list_of_files:
    xmlObject = ET.parse(file)  # create an xml object that python can parse
    root = xmlObject.getroot() #get the root of that object
    NSMAP = root.nsmap

    for source in root.findall(xpath, NSMAP): #xpath example: './/relatedItem[@type]/titleInfo/title'
        if source.text != 'string to find':
            updated = source.text.replace(source.text, 'string to replace with')
            source.text = updated
        else:
            continue

    directory_to_write_to = os.path.join([base_dir_path], os.path.basename(file))
    xmlString = ET.tostring(root, encoding='utf-8')
    with open(directory_to_write_to, 'wb') as nf:
        nf.write(xmlString)