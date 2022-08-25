from bs4 import BeautifulSoup
import requests
import os
import spacy #spaCy is a python library for natural language processing 
from spacy.lang.en import English #I am using english langauge text, so I import the English lang module
#but spaCy supports a wide variety of languages
from spacy.matcher import Matcher
nlp = English()

path = 'path/to/your/files'

nlp = spacy.load('en_core_web_sm') #creating the nlp object from spaCy, which contains the language processing pipeline
matcher = Matcher(nlp.vocab)

audit = [] #here we are creating an empty list, which we will append the names of files to later in the script
#we will then print the items in the list to have a clear understanding of what files may need attention based on matched tokens

for rootdir, subdir, file in os.walk(path): #the os module allows us to interact with the underlying operating system of your machine
    for f in file: #we have to tell python that for each file found in the path was have just given it to "walk" i.e. search and scan 
    #we want it to open the file, read the file, and parse that file's text.
        
        with open(os.path.join(path, f), 'r', encoding='latin-1') as html_file:
            soup = BeautifulSoup(html_file, 'lxml') #This text is then stored in the "soup" variable
            #which we will use in the remainder of the script to search for specific token (ie words)
        
        p_list = [] #we are creating an empty list, where we will tell python to store the text of any <p> tag found in the html file
        p_tag = soup.find_all('p') #we must find all of the <p> tags in the html file, which we can do using the .findall() method of the lxml library
        #this creates a list of iterator-objects, which we will need to iterator through
        for p in p_tag:
            p_list.append(p.text) #we only want the text of each <p> tag, so we use the .text attribute from the lxml library to tell python to store only 
            #the text in the <p> tag to the p_list variable
        #print(p_list) #this can be used to help trouble shoot/confirm the script is working as is expected up to this point. 

        collec_desc_string = '' #here we create an empty string variable, which we will use to store the content of p_list as a simple string

        doc = nlp(collec_desc_string.join(str(p_list))) # we want to process our new text/string with the nlp object defined earlier
        #when this is done, spaCy creates a 'doc' object, and so, the variable used to define this is typically called 'doc'.
        #working with spaCy is not required, and the same could be accomplished with using the p_list created above, but spaCy does provide
        #exceptional functionality and is incredibly powerful for matching particalar patterns and phrases. This is why I suggest familiarlizing yourself
        #with the library

        list_tokens = [] #empty list to store the "tokens" ie words from the doc object created above
        for token in doc: #we have to iterate through each word
            list_tokens.append(token.text) #and appended it to our list variable
        
        harmful_terms = ['slave', 'slavery', 'homosexual', 'Mrs.', 'Mrs', 'indian', 'Indian', 'Native', 'deviant',
                         'huns', 'Huns', 'Hunky', 'hunky', 'colored', 'negro', 'oriental', 'illegal', 'alien', 'redman',
                         'redskin', 'squaw', 'wop', 'blight', 'blacks'] #in order to audit the collection descriptions, we must tell python what word/words
                         #we want it to look for. This list is NOT comphrehensive, but merely an example. You can add as many terms here as is necessary.
                         #however, the terms are case sensitive.
                         
        for i in harmful_terms: #now we iterate over each word defined in the marhful_term variable
            if i in list_tokens: #and we tell the program that if that term is in the list of tokens we provided 
                item_to_audit = "The following term is found in {}: {}".format(f, i) #store the file name (f) and the term (i) in this variable
                #using the format 'The following term is found in {filename}: {term}."
                audit.append(item_to_audit) #but then we need to append this variable and the information it carries to our empty audit list

for i in audit: #and to see what collection descriptions might need to be audited we used a simple for loop
#which iterates through our audit list (which is no longer empty!)
#and prints each item_to_audit variable
    print(i)

