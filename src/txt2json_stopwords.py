# To read data in txt file and store in json format

import json

TXT_PATH = '../data/google_stopwords.txt'
JSON_PATH = '../data/google_stopwords.json'

stopword_list = []

with open(TXT_PATH) as f:
    for line in f:
        stopword_list.append(line.strip())

with open(JSON_PATH, 'wb') as f:
    json.dump(stopword_list, f)