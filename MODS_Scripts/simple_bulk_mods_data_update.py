def bulk_mods_updates(base_dir, field_to_change):
    from lxml import etree as ET
    import sys
    import glob
    import os.path

    target_dir = os.mkdir(os.path.join(base_dir, str(date.today())+'-updated'))
    destination_dir = os.path.join(base_dir, str(date.today())+'-updated')


    list_of_files = glob.glob('{}/*.xml'.format(base_dir))
    for file in list_of_files:
        xmlObject = ET.parse(file)  # create an xml object that python can parse
        root = xmlObject.getroot()  # get the root of that object  
        NSMAP = root.nsmap

        for mods_field in root.findall('.//mods:{}'.format(field_to_change), NSMAP):
            # print(type_of_resource.text)
            updated = mods_field.text.replace(mods_field.text, 'still image')
            mods_field.text = updated
            
        directory_to_write_to = os.path.join(destination_dir,os.path.basename(file))

        xmlString = ET.tostring(root, encoding='utf-8')
        with open(directory_to_write_to, 'wb') as nf:
            nf.write(xmlString)

    print('mods data has been updated!')