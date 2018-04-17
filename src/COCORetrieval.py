#!/usr/bin/env python
#__author__      = "biendltb"
#__email__       = "biendltb@gmail.com"

"""json2sqlite.py: Move the image information and annotations from json to sqlite database."""

import sqlite3
import re
import math
import json
import operator
import time



class COCORetrievalSQLite:

    # query image from database
    # return top num_top images
    def query(self, query, num_top):

        db_conn = DBConnection()

        # get the list of words in the query
        q_words = re.split('; |, |\*|\s+|\n', query.lower())

        # remove stop words from the query
        stop_words = db_conn.get_stop_word_list()
        for w in q_words:
            if w in stop_words:
                q_words.remove(w)

        # dictionary contains idf for each words
        # key: word | value: idf
        idf_dic = {}

        # calculate idf for each word
        for w in q_words:
            total_doc = db_conn.count_total_doc()
            num_doc_contain = db_conn.count_doc_contain(w)

            if num_doc_contain > 0:
                idf_dic[w] = math.log(float(total_doc) / num_doc_contain)
            else:
                idf_dic[w] = 0

        # keep the tf-idf values for each captions
        # key: caption id | value: tfidf
        tf_idf_dic = {}

        # loop through all words in the query sentence
        # calculate tf-idf for each caption containing the word
        for w in q_words:
            for doc_id, doc in db_conn.get_docs_contain(w).items():

                norm_doc = re.split('; |, |\*|\s+|\n', doc.lower())
                tf = norm_doc.count(w.lower()) / float(len(norm_doc))
                # because of avoiding duplicate words in a caption
                # number of types is better than the number of a object
                # if count > 0 => count = 1
                if tf > 0:
                    tf = 1
                if doc_id in tf_idf_dic:
                    tf_idf_dic[doc_id] += tf * idf_dic[w]
                else:
                    tf_idf_dic[doc_id] = tf * idf_dic[w]

        # sort the list of tf-idf score
        sorted_tfidf = sorted(tf_idf_dic.items(), key=operator.itemgetter(1))
        sorted_tfidf.reverse()

        # get image name from caption id
        # avoid getting duplicated images
        ims = []
        for ele in sorted_tfidf:
            im_name = db_conn.get_im_name(ele[0])
            if im_name not in ims:
                ims.append(im_name)
            if len(ims) >= num_top:
                break

        #print ims
        return ims

class DBConnection:
    db_path = "../data/captions_val2014.db"

    # count total number of captions in database
    def count_total_doc(self):
        # connect to database
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        query = "SELECT COUNT(*) FROM annotations"

        cur.execute(query)
        rows = cur.fetchall()

        res = 0

        for row in rows:
            res = row[0]

        conn.commit()
        conn.close()

        return res

    # count how many documents in database contain a word
    # to calculate the idf
    def count_doc_contain(self, word):

        w = word.lower().strip()
        # connect to database
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        query = "SELECT COUNT(*) FROM annotations WHERE ((caption LIKE '%% %s %%') OR ('%s %%') OR ('%% %s'))" \
                "" % (w, w, w)

        cur.execute(query)
        rows = cur.fetchall()

        res = 0

        for row in rows:
            res = row[0]

        #print res

        conn.commit()
        conn.close()

        return res

    # find all documents contain a word
    def get_docs_contain(self, word):
        # connect to database
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        query = "SELECT id, caption from annotations WHERE ((caption LIKE '%% %s %%') OR ('%s %%') OR ('%% %s'))" \
                "" % (word, word, word)

        cur.execute(query)
        rows = cur.fetchall()

        # build a dictionary to store document id and its content
        list_docs = {}

        for row in rows:
            list_docs[row[0]] = row[1]

        conn.commit()
        conn.close()

        return list_docs

    # get image name from caption id
    def get_im_name(self, cap_id):
        # connect to database
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        query = 'SELECT file_name from images im INNER JOIN annotations ann ON im.id = ann.image_id WHERE ann.id = %d' % (cap_id)

        cur.execute(query)
        rows = cur.fetchall()

        res = ''

        for row in rows:
            res = row[0]

        #print res

        conn.commit()
        conn.close()

        return res

    def get_stop_word_list(self):
        # connect to database
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        query = 'SELECT word FROM stop_words'

        cur.execute(query)
        rows = cur.fetchall()

        res = []

        for row in rows:
            res.append(row[0])

        conn.commit()
        conn.close()

        return res


class COCORetrievalJSON:
    IMG_DETAIL_PATH = '../data/captions_val2014.json'

    # json format
    # {
    # "info" :
    #   {
    #       "description" : str
    #       "url" : str
    #       "version" : str
    #       "year" : int
    #       "contributor" : str
    #       "date_created" : str
    #   },
    #
    # "images" :
    #   [
    #       {
    #           "license" : int
    #           "file_name" : str
    #           "coco_url" : str
    #           "height" : int
    #           "width" : int
    #           "date_captured" : str
    #           "flickr_url" : str
    #           "id" : int
    #       },
    #       ...
    #   ],
    # "annotations" : ...
    #   [
    #       {
    #           "image_id" : int
    #           "id" : int
    #           "caption" : str
    #       },
    #       ...
    #   ]
    #   }

    def __init__(self):

        with open(self.IMG_DETAIL_PATH) as data_file:
            data = json.load(data_file)

        # all annotations
        self.anns = data["annotations"]
        # all image information
        self.ims = data["images"]

    # return list of top caption id related to the query
    def get_closest_captions(self, query):
        tfidf_calculator = TfidfCalculator()

        # extract list of words from the query
        norm_query = tfidf_calculator.extracting_terms(query)

        # number of top results
        num_top_res = 10

        # collect and store all captions in a list
        docs = []

        # TODO: optimize time loop through json data: ~30s
        # loop in a list of annotation dictionaries
        for i in range (0, len(self.anns)):
            # access to a dictionary
            for key, value in self.anns[i].items():
                if key == "caption":
                    self.anns[i][key] = tfidf_calculator.remove_stop_words(value)
                    docs.append(self.anns[i][key])

        # dictionary to store idf values of terms in the query
        idf_dic = {}

        # dictionary to store id of caption and the accumulative tf-idf values
        tfidf_dic = {}

        # loop through all terms in query
        # calculate their idf
        for w in norm_query:
            idf_dic[w] = tfidf_calculator.idf(w, docs)

        # loop through all docs
        # calculate tf-idf for each docs
        # store results in a dictionary with keys are caption ids
        for ann in self.anns:
            cap_id = ann["id"]
            cap_content = ann["caption"]
            tfidf_dic[cap_id] = 0
            for w in norm_query:
                tfidf_dic[cap_id] += tfidf_calculator.tf(w, cap_content) * idf_dic[w]
        # sort the results DESC
        sorted_tfidf = sorted(tfidf_dic.items(), key=operator.itemgetter(1))
        sorted_tfidf.reverse()

        # get top tf-idf scores, take caption id and add to the list
        list_cap_id = []
        for i in range(1, num_top_res):
            #print(sorted_tfidf[i])
            list_cap_id.append(sorted_tfidf[i][0])

        return list_cap_id

    def get_im_file_list(self, query):
        list_cap_id = self.get_closest_captions(query)

        # collect image id from list of top cap id
        # make sure that there is no duplication of image id
        im_ids = []
        for ann in self.anns:
            for cap_id in list_cap_id:
                if ann["id"] == cap_id:
                    im_id = ann["image_id"]
                    if im_id not in im_ids:
                        im_ids.append(im_id)

        # get image file name from list of image ids
        im_file_list = []
        for im in self.ims:
            for im_id in im_ids:
                if im_id == im["id"]:
                    im_file_list.append(im["file_name"])
                    #print(im["file_name"])

        return im_file_list

class TfidfCalculator():
    STOP_WORD_PATH = "../data/google_stopwords.json"

    def __init__(self):
        with open(self.STOP_WORD_PATH) as data_file:
            self.stop_word_arr = json.load(data_file)

    # extract all terms from documents and store in a list
    def extracting_terms(self, doc):
        return re.split('; |, |\*|\s+|\n', doc.lower())

    # calculate term frequency in a single document
    def tf(self, term, doc):
        norm_doc = self.extracting_terms(doc)
        return norm_doc.count(term.lower()) / float(len(norm_doc))

    # inverse document frequency = logarithm (to base 10) of (total_doc / num_doc_has_term)
    # need to test between log base 10 and log base e to choose the best
    def idf(self, term, docs):
        num_containing_doc = 0
        for doc in docs:
            if term.lower() in self.extracting_terms(doc):
                num_containing_doc = num_containing_doc + 1

        if num_containing_doc > 0:
            return math.log(float(len(docs)) / num_containing_doc)
        else:
            return 0

    # remove stop words from captions before ranking
    def remove_stop_words(self, doc):
        for sw in self.stop_word_arr:
            sw_re = r'\b' + sw.lower() + r'\b'
            doc = re.sub(sw_re, '', doc.lower())
        return doc



# db = DBConnection()
# db.count_doc_contain('dog')
# db.get_docs_contain('dog')
#
# coco = COCORetrievalSQLite()
# coco.query('dog',10)