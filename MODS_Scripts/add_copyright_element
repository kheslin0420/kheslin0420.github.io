from lxml import etree as ET
import sys
import glob
import os.path
import csv


list_of_files = glob.glob('/Directory/to/xml-files/*.xml') #The glob module finds all
#the pathnames matching a specified pattern. Here I am telling the script to find all files 
#that end with .xml. There are several ways of getting files in python, but I use glob.glob here because personally
#I find it easiest and it returns the full path name of each file

for file in list_of_files:
  mods_namespaces = 'http://www.loc.gov/mods/v3'  # define your namespace
  mods = '{%s}' % mods_namespaces #this will be a prefix we use later in our script
  ns_map = {'mods': mods_namespaces} 
  copyright_ns = 'http://www.cdlib.org/inside/diglib/copyrightMD' #because we are working with the copyright field
  #we need to define the namespace for copyrightMD as well
  cp = '{%s}' % copyright_ns #this will be a prefix we use later in our script
  copyright_nsmap = {'copyrightMD': 'http://www.cdlib.org/inside/diglib/copyrightMD'}
  xmlObject = ET.parse(file)  # create an xml object that python can parse using lxml libraries
  root = xmlObject.getroot() #get the root of that object. Finding the root allows us to traverse the xml object heirarchacly
  
  access_condition = ET.SubElement(root, mods + 'accessCondition') we are using the lxml library agin to create the 
  #<accessCondition> element. lxml provides the .SubElement method for creating tree nodes as children. The syntax for 
  #this method is .SubElement([parent_node], child node tag, *attributes) *attributes are optional
  
  copyright_status = ET.SubElement(access_condition, cp + 'copyright', nsmap=copyright_nsmap) #After we have created
  #the <accessCondition> element, we can create the copyright element as a child.
  copyright_status.attrib['copyright.status'] = "unknown" #rather than define my attributes in the element creation above
  #I had to create attributes for the <copyright> element after
  copyright_status.attrib['publication.status'] = "unknown"
  
  #in order to apply to correct "copyright.status", I used a csv spreadsheet with the 
  #identifier and copyright status for each item
  #I used the barcode embedded in each file name to match the data supplied in the spreadsheet

  barcode = file.split('_')[1]

  print(barcode)

  with open('/Users/kaylaheslin/Desktop/rights_eval_with_ID.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for row in csv_reader:
      if row[0] == barcode:
        copyright_status.attrib['copyright.status'] = row[1]
        #print(abstract.text)
    
    directory_to_write_to = os.path.join('/new/directory/tosaveto', os.path.basename(file))

    xmlString = ET.tostring(root, encoding='utf-8')
    with open(directory_to_write_to, 'wb') as nf:
        nf.write(xmlString)

print('Copyright tag has been added')
