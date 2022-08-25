import requests
import json
import pandas as pd

url = 'https://api.hatebase.org/4-4/authenticate'

api_key = "yourAPIkeyhere"
headers = {
    'Content-Type': "application/x-www-form-urlencoded",
    'cache-control': "no-cache"
    }


r = requests.post(url, data=api_key, headers=headers)
#r = requests.get('https://api.dp.la/v2/items?q=flowers&api_key=3fa61288b0362230533fbceec534fd4c')
r_json = r.json()
r_string = json.dumps(r_json, indent=2)

token = r_json["result"]["token"]

vocab_url = 'https://api.hatebase.org/4-4/get_vocabulary'
lang = 'eng'
resp_format = 'json'

vocab_payload = "token=" + token + "&format=" + resp_format + "&language=" + lang
voc_resp = requests.post(vocab_url, data=vocab_payload, headers=headers)

voc_json = voc_resp.json()

pages = voc_json['number_of_pages']
results = voc_json['number_of_results']

df_voc = pd.DataFrame(voc_json["result"])

#create empty term list
english_term_list = []

# now get results of all the remaining pages
# append those results to our dataframe "df_voc"
for page in range(1,pages+1):
    vocab_payload = "token=" + token + "&format=json&language=" + lang + "&page=" + str(page)
    voc_resp = requests.post(vocab_url, data=vocab_payload, headers=headers)
    voc_json = voc_resp.json()
    df_voc = df_voc.append(voc_json["result"])
    english_term_list


# reset the df_voc index so that all entries are nicely numbered in an ascending way
df_voc.reset_index(drop=True, inplace=True)

#Full Term List
term_list = df_voc['term'].tolist()

#Filter frame to rows where terms are marked unambiguous
unambiguous_df = df_voc[df_voc['is_unambiguous'] == True]
unambiguous_term_list = unambiguous_df['term'].tolist()


# save the vocabulary in the df_voc dataframe as a csv
df_voc.to_csv("path/to/csv") 
unambiguous_df.to_csv("path/to/csv")

#with open('/Users/kaylaheslin/Desktop/dpla-data.json', 'w') as f:
    #json.dump(r_json, f, indent=2)
