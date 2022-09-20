from lxml import etree as ET
import re
import csv
import sys
import glob
import os.path
import datetime
import sys

mods_xml = input('Enter full path to mods XML file:\n')
xmlObject = ET.parse(mods_xml)  # create an xml object that python can parse
print('Parsing xml data....')
root = xmlObject.getroot()  # get the root of that object  
NSMAP = root.nsmap
mods_namespaces = 'http://www.loc.gov/mods/v3'  # define your namespace
mods = '{%s}' % mods_namespaces
copyright_ns = 'http://www.cdlib.org/inside/diglib/copyrightMD'
cp = '{%s}' % copyright_ns
copyright_nsmap = {'copyrightMD': 'http://www.cdlib.org/inside/diglib/copyrightMD'}
CSV_path = input('Enter full path to extended csv:\n')


user_input = input("Enter full path name of directory where your MODS will be stored:")
directory1 = user_input

try:
    with open(CSV_path, mode='r', encoding="utf-8", newline='') as csvfile:
        csv_reader = csv.DictReader(csvfile, delimiter=',', )
        for row in csv_reader:
            mms_id = row['MMS ID']
            recID = root.xpath('.//*[contains(text(), "{}")]'.format(mms_id))
            for i in recID:
                if i.text == mms_id:
                    recordInfo = i.getparent()
                    mods_xml = recordInfo.getparent()
                    tree = ET.ElementTree(mods_xml)
                    tree.write(directory1 + '/pitt_{}_MODS.xml'.format(row['identifier']))
                else:
                    sys.exit("MMS IDs not found in batch MODS. Check batch MODS to ensure it matches extended metadata csv.")
except FileNotFoundError:
    with open(CSV_path, mode='r', encoding="utf-8", newline='') as csvfile:
        csv_reader = csv.DictReader(csvfile, delimiter=',', )
        for row in csv_reader:
            mms_id = row['MMS ID']
            recID = root.xpath('.//*[contains(text(), "{}")]'.format(mms_id))
            for i in recID:
                if i.text == mms_id:
                    recordInfo = i.getparent()
                    mods_xml = recordInfo.getparent()
                    tree = ET.ElementTree(mods_xml)
                    path = os.path.join(directory1, '/pitt_{}_MODS.xml'.format(row['identifier']))
                    tree.write(os.makedirs(path))
                else:
                    sys.exit("MMS IDs not found in batch MODS. Check batch MODS to ensure it matches extended metadata csv.")

#####Code above writes XML files for each row in the spreadsheet, based on its MMS ID

###Code below modifies those xml files based off of spreadsheet data
list_of_files = glob.glob(directory1 + '/*.xml')
with open(CSV_path, mode='r', encoding='utf-8', newline='') as csvfile:
    csv_reader = csv.DictReader(csvfile, delimiter=',')
    for row in csv_reader:
        for file in list_of_files:
            xmlObject = ET.parse(file)  # create an xml object that python can parse
            r = xmlObject.getroot()
            barcode = os.path.basename(file).split('_')[1]  # create a variable that contains the barcode for each file by taking
            # only the relevant portion from the filename
            mods_namespaces = 'http://www.loc.gov/mods/v3'  # define your namespace
            mods = '{%s}' % mods_namespaces
            copyright_ns = 'http://www.cdlib.org/inside/diglib/copyrightMD'
            cp = '{%s}' % copyright_ns
            copyright_nsmap = {'copyrightMD': 'http://www.cdlib.org/inside/diglib/copyrightMD'}
            nsmap = {'mods': 'http://www.loc.gov/mods/v3', 'xlink': 'http://www.w3.org/1999/xlink',
                     'ns2': 'http://www.w3.org/1999/xlink', 'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                     'copyrightMD': 'http://www.cdlib.org/inside/diglib/copyrightMD'}


            class Dates:  # create a class to handle dates in list format
                def __init__(self, date_list):
                    self.date_list = date_list


            class Date_obj(
                Dates):  # then create a subclass of Class Dates. This Subclass will create a date object we will used
                def __init__(self,
                             date_list):  # pass the same arguments as the parent class, plus any unique attributes. In this case
                    # we do not have any new attributes to add
                    self.date_list = date_list
                    super().__init__(date_list)

                def get_date_obj(
                        self):  # create a function that will take the date list supplied in the class above and
                    # turn the list into a date object depending on the format of the date
                    if len(self.date_list) == 3:  # handles dates in YYYY, MM, DD format
                        dt_obj = datetime.datetime(int(self.date_list[0]), int(self.date_list[1]),
                                                   int(self.date_list[2]))
                        return dt_obj
                    elif len(self.date_list) == 2:  # YYYY, MM
                        dt_obj = datetime.datetime(int(self.date_list[0]), int(self.date_list[1]), 1)
                        return dt_obj
                    elif len(self.date_list) == 1:  # YYYY
                        dt_obj = datetime.datetime(int(self.date_list[0]), 1, 1)
                        return dt_obj


            class Display_Date(
                Date_obj):  # create a new sublass that inherits from Date_Object sublass, so that we can create
                # a display date using the date_object created above
                def __init__(self, date_list,
                             dt_obj):  # here we do have a new attribute. We are passing the date list AND the date
                    # object created in Subclass Date_obj, which should be stored as a variable
                    self.date_list = date_list
                    self.dt_obj = dt_obj
                    super().__init__(date_list)

                def get_display_date(self):  # a function to produce a dislay date, based on the format of the date_list
                    if len(self.date_list) == 3:  # handles dates in YYYY, MM, DD format
                        display_date = self.dt_obj.strftime("%B %d, %Y")
                        return display_date
                    elif len(self.date_list) == 2:  # YYYY, MM
                        display_date = self.dt_obj.strftime("%B %Y")
                        return display_date
                    elif len(self.date_list) == 1:  # YYYY
                        display_date = self.dt_obj.strftime("%Y")
                        return display_date


            if row[
                'identifier'] == barcode:  # compare the identifier in the CSV to the barcode variable we created above
                access_condition = ET.SubElement(r,
                                                 mods + 'accessCondition')  # removed mods namespace declaration "mods + 'accessCondition'"
                copyright_status = ET.SubElement(access_condition, cp + 'copyright',
                                                 nsmap=copyright_nsmap)  # removed copyright namespace declaration
                identifier = ET.SubElement(r, mods + 'identifier', type="pitt")  # removed mods namespace declaration

                name = ET.SubElement(r, mods + 'name')  # creating a new subelement in the MODS tree
                namePart = ET.SubElement(name, mods + 'namePart')
                namePart.text = row['depositor']  # assigning the text of new subelement by accessing csv data
                role = ET.SubElement(name, mods + 'role')
                roleTerm = ET.SubElement(role, mods + 'roleTerm', type="text")
                roleTerm.text = 'depositor'

                title = r.find('.//mods:titleInfo/mods:title', nsmap)
                titleInfo = r.find('.//mods:titleInfo', nsmap)

                copyright_status.attrib['copyright.status'] = row['copyright_status']
                copyright_status.attrib['publication.status'] = row['publication_status']
                identifier.text = row['identifier']

                try:
                    if row['rights_holder'] == '':
                        pass
                    else:
                        rights_holder = ET.SubElement(copyright_status, cp + 'rights.holder')
                        rights_holder_name = ET.SubElement(rights_holder, cp + 'name')
                        rights_holder_name.text = row['rights_holder']
                except:
                    pass
                if row['extent'] == '':
                    pass
                else:
                    try:
                        physDesc = r.find('.//mods:physicalDescription', nsmap)
                        extent = ET.SubElement(physDesc, mods + 'extent')
                        extent.text = row['extent']
                    except TypeError:
                        physDesc = ET.SubElement(r, mods + 'physicalDescription')
                        extent = ET.SubElement(physDesc, mods + 'extent')
                        extent.text = row['extent']
                if row['partNumber'] == '':
                    pass
                else:
                    partNumber = ET.SubElement(titleInfo, mods + 'partNumber')
                    partNumber.text = row['partNumber']
                if row['normalized_date'] == '':
                    pass
                else:
                    originInfo = r.find('.//mods:originInfo', nsmap)
                    normalized_date = ET.SubElement(originInfo, mods + 'dateCreated', encoding='iso8601', keyDate='yes')
                    sort_date = ET.SubElement(originInfo, mods + 'dateOther', type='sort')
                    display_date = ET.SubElement(originInfo, mods + 'dateOther', type='display')
                    normalized_date.text = row['normalized_date']
                    if '/' in row[
                        'normalized_date']:  # assessing the date format from CSV. This helps to handle complex dates
                        try:
                            split_date = row['normalized_date'].split(
                                '/')  # create two different dates to access individually by splitting on the /
                            d1 = split_date[0].split('-')  # create a variable containing the first date expression
                            d2 = split_date[1].split('-')  # create a variable containing the second date expression
                            date_object1 = Date_obj(
                                d1).get_date_obj()  # creating a class object and getting the datetime object from the class object
                            date_object2 = Date_obj(d2).get_date_obj()
                            if row['display_date'] == '':
                                display1 = Display_Date(d1,
                                                        date_object1).get_display_date()  # creating a subclass object for display_date. MUST pass datetime object created above
                                display_date2 = Display_Date(d2, date_object2).get_display_date()
                                display_date_string = str(display1) + ' - ' + str(
                                    display_date2)  # storing the display_date string in a variable
                                display_date.text = display_date_string  # assigning text of SubElement display_date
                                sort_date.text = str(date_object1).replace(" ", "T")
                                if row['normalized_date_qualifier'] == '':  # assess whether a "ca" date
                                    pass
                                else:
                                    normalized_date.set('qualifier',
                                                        'approximate')  # if yes, assign a new attribute to normalized_date element
                                    display_date.text = 'ca. ' + display_date_string  # and precede display string with ca.
                            else:
                                display_date.text = row['display_date']
                                sort_date.text = str(date_object1).replace(" ", "T")
                        except:
                            print("There is an issue with the date for object {}".format(row['identifier']))
                    else:  # if not a complex date
                        try:
                            date = row['normalized_date'].split('-')
                            date_object = Date_obj(date).get_date_obj()
                            display = Display_Date(date, date_object).get_display_date()
                            display_date_string = display
                            if row['display_date'] == '':
                                display_date.text = display_date_string
                                sort_date.text = str(date_object).replace(" ", "T")
                                if row['normalized_date_qualifier'] == '':
                                    pass
                                else:
                                    normalized_date.set('qualifier', 'approximate')
                                    display_date.text = 'ca. ' + display_date_string
                            else:
                                display_date.text = row['display_date']
                                sort_date.text = str(date_object).replace(" ", "T")
                        except:
                            print("There is an issue with the date for object {}".format(row['identifier']))
                if row['genre'] == '':
                    pass
                else:
                    genre = ET.SubElement(r, mods + 'genre')
                    genre.text = row['genre']
                if row['description'] == '':
                    pass
                else:
                    desc = ET.SubElement(r, mods + 'abstract')
                    desc.text = row['description']
                if row['source_identifier'] == '':
                    pass
                else:
                    source_id = ET.SubElement(r, mods + 'identifier', type='source')
                    source_id.text = row['source_identifier']
            xmlString = ET.tostring(r, encoding='utf-8')  # indenting
            with open(file, 'wb') as nf:
                nf.write(xmlString)

# writes new MODS files with appropriate headers
print('MODS created, but headers need to be added. Processing now.....')
list_of_files = glob.glob(directory1 + '/*.xml')
for file in list_of_files:
    # print(file.split('/')[5])
    xmlObject = ET.parse(file)
    r = xmlObject.getroot()
    tree = ET.ElementTree(r)
    root2 = tree.getroot()
    schemaLoc = 'http://www.w3.org/2001/XMLSchema-instance'
    mods_declaration = 'http://www.loc.gov/mods/v3'
    ET.register_namespace('xsi', schemaLoc)
    ET.register_namespace('mods', mods_declaration)
    qname1 = ET.QName(schemaLoc, 'schemaLocation')
    qname2 = ET.QName(mods_declaration, "mods")
    nsmap = {'mods': 'http://www.loc.gov/mods/v3', 'xlink': 'http://www.w3.org/1999/xlink',
             'ns2': 'http://www.w3.org/1999/xlink', 'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
             'copyrightMD': 'http://www.cdlib.org/inside/diglib/copyrightMD'}  # removed copyright link

    root2 = ET.Element(qname2, {qname1: 'http://www.loc.gov/mods/v3 http://www.loc.gov/standards/mods/v3/mods-3-7.xsd'},
                       nsmap=nsmap)
    ID = r.xpath(".//mods:identifier[@type='pitt']", namespaces={'mods': 'http://www.loc.gov/mods/v3'})

    for child in r:
        root2.append(child)

    xmlString = ET.tostring(root2, encoding='utf-8', pretty_print=True)
    with open(directory1 + '/' + f"pitt_{ID[0].text}_MODS.xml", 'wb') as newfile:
        newfile.write(xmlString)

shutil.make_archive(directory1, 'zip', directory1)
print('Process complete!')