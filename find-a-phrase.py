import spacy
from spacy.lang.en import English
from spacy.matcher import Matcher
nlp = English()
from lxml import etree as ET

nlp = spacy.load('en_core_web_sm') #define the nlp object, which contained the language processing pipeline
matcher = Matcher(nlp.vocab) #initialize the matcher using the shared nlp vocab

text = txt_string
doc = nlp(text)

pattern = [{'TEXT': 'passed'}, {'TEXT': 'away'}] #define the pattern you wish to look for
#match patterns in spaCy are defined using dictionaries. The key of the dictionary is the token attribute you wish to access
#here, we are telling the program that we want to look at the text ('TEXT') of the tokens (words) in whatever we use the matcher on. 
#the value of the dictionary is whatever your expected value will be. In this simple examples, we are looking for text that matches 'passed'
#and 'away

matcher.add('passed_away_pattern', None, pattern) #the matcher.add method allows you to add the defined pattern. The first argument is a unique ID 
#you define to help identify what pattern was matched later in the script, the thrid argument is an optional callback and the third argument is the patter

path = '/path/to/your/files' #define your file path

for rootdir, subdir, file in os.walk(path): #using the os module we can interact with the underlying system of our computers
    for f in file: #tell python what to do with each file
        #print(f)
        lxmlobject = ET.parse(os.path.join(path, f)) #we have to parse each file with the lxml librayr, since these are EAD files (xml)
        root = lxmlobject.getroot() #we define the root, which will allow us to iterate the xml tree
        #print(root)
        newlist = [] #define an empty list, which we will append to later
        
        bioghist = root.findall('archdesc/bioghist/p') #tell python what to look for in the EAD tree
        scopecontent = root.findall('archdesc/scopecontent/p') #I want both the bioghist and the scope and content, so I create variables for each
        
        for p in bioghist: #but we need to access the text of each, and not just the iterator object returned by the root.findall() method
            newlist.append(p.text) #so we iterate over the 'p' contents and append only the text (p.text) to our newlist variable
        for p in scopecontent: #do this for both
            newlist.append(p.text)

        bioghist_string = '' #create an empty string variable

        doc = nlp(bioghist_string.join(newlist)) define a spaCy doc object using the empty string variable and the contents of newlist
        matches = matcher(doc) # call the matcher on the doc object 
        #print('Total matches found: ', len(matches))

        for match_id, start, end in matches: #the matcher returns a list of tuples, so we can iterate over this information using a for loop
            #to get the information in the following format --> "A matc for the expression:", doc[start:end].text returns the pattern matched + (used to concatentate in python) 'in the following finding aid {f}" where f = filename
            print("A match for the expression:", doc[start:end].text + " in the following finding aid {}".format(f))
