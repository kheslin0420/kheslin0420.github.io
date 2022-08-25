import csv
import os
import spacy
from spacy.lang.en import English
from spacy.matcher import PhraseMatcher
import pandas as pd
import re

path = ''


file_audit2 = []
expression_matched = []
vocab_matched = []
context_snippet = []

fa_url_base = ''

nlp = spacy.load('en_core_web_sm')
matcher = PhraseMatcher(nlp.vocab, attr='LOWER')
for rootdir, subdir, file in os.walk(path):
    for f in file:
        with open(os.path.join(rootdir, f), 'r') as file:
            new_list = []
            for line in file:
                new_list.append(re.sub(r'[^\w\s]', '', line).strip())

            string = ''
            doc = nlp(string.join(str(new_list)))


            a_list_of_words = ['native americans', 'natives', 'mulatto', 'mulattos', 'creole', 'creoles',
										  'oriental',
										  'aborigines', 'aboriginals', 'arab', 'arabs', 'hispanics', 'japs', 'coolies',
										  'coolie',
										  'ethnic', 'indian', 'indians', 'savages', 'uncivilized', 'squaws', 'pygmy',
										  'pygmies',
										  'primitives', 'primitive people', 'bushmen', 'bushman', 'bushwoman',
										  'bushwomen',
										  'fag',
										  'dyke', 'mammy', 'negro', 'negroes', 'negros', 'nigger', 'nigga' 'gypsy', 'sambo', 'blacks',
										  'asians',
										  'asiatic', 'chink',]
            words = [nlp.make_doc(term) for term in a_list_of_words]

            matcher.add('words', None, *words)
            matches = matcher(doc)

            for match_id, start, end in matches:
                print('A match has been found. The term {} was found in {}. Lexicon: {}'.format(doc[start:end].text, f, doc.vocab.strings[match_id]))

                vocab_matched.append(doc.vocab.strings[match_id])
                expression_matched.append(doc[start:end].text)
                file_audit2.append(fa_url_base + f.split('_')[1])
                #context_snippet.append(doc[start - 10:end + 10])

dict2 = {'file_urls': file_audit2, 'expression_matched': expression_matched, 'vocabulary_matched': vocab_matched}
df2 = pd.DataFrame(dict2)
df2.to_csv('.csv')
