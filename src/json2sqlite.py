#!/usr/bin/env python

"""json2sqlite.py: Move the image information and annotations from json to sqlite database."""
__author__      = "biendltb"
__email__       = "biendltb@gmail.com"

import re
import json
import sqlite3


db_path = "../data/captions_val2014.db"
IMG_DETAIL_PATH = '../data/captions_val2014.json'
STOP_WORD_PATH = "../data/google_stopwords.json"

# connect to database
conn = sqlite3.connect(db_path)

c = conn.cursor()

with open(IMG_DETAIL_PATH) as data_file:
    data = json.load(data_file)

# all annotations
anns = data["annotations"]
# all image information
ims = data["images"]

with open(STOP_WORD_PATH) as data_file:
    stop_word_arr = json.load(data_file)

# insert all data from images to database
for i in range(0, len(ims)):
    # get each key/value in each field
    # order: license, file_name, coco_url, height, width, date_captured, flickr_url, id
    ele_list = list()
    for key, value in ims[i].items():
        ele_list.append(value)

    query = 'INSERT INTO images VALUES(%d, %d, \'%s\', \'%s\', %d, %d, \'%s\', \'%s\')' % (ele_list[7], ele_list[0],
                ele_list[1], ele_list[2], ele_list[3], ele_list[4], ele_list[5], ele_list[6])

    #c.execute(query)

# insert all data from annotations to database
for i in range(0, len(anns)):
    ele_list = list()
    # order: image_id, id, caption
    for key, value in anns[i].items():
        ele_list.append(value)

    # avoid the single quote when inserting to database
    doc = str(ele_list[2]).replace('\'', '\'\'')
    #remove the stop words
    for sw in stop_word_arr:
        sw_re = r'\b' + sw.lower() + r'\b'
        doc = re.sub(sw_re, '', doc.lower())
        # remove multiple spaces
        doc = re.sub(' +', ' ', doc)
    query = 'INSERT INTO annotations VALUES(%d, %d, \'%s\')' % (ele_list[1], ele_list[0], doc)

    #print(query)
    #c.execute(query)


# insert list of the stop words
#for sw in stop_word_arr:
    #query = 'INSERT INTO stop_words(word) VALUES(\'%s\')' % sw
    #c.execute(query)

conn.commit()
conn.close()

