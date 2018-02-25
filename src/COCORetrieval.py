import json

import operator

from TfidfCalculator import TfidfCalculator


class COCORetrieval:
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


    def getClosestCaption(self, query):
        with open(self.IMG_DETAIL_PATH) as data_file:
            data = json.load(data_file)

        tfidf_calculator = TfidfCalculator()

        # extract list of words from the query
        norm_query = tfidf_calculator.extracting_terms(query)

        # all annotations
        anns = data["annotations"]

        # store all captions in a list
        docs = []
        for ann in anns:
            docs.append(ann["caption"])

        # dictionary to store idf values of terms in the query
        idf_dic = {}

        # dictionary to store id of caption and the accumulative tf-idf values
        tfidf_dic = {}

        # loop through all terms in query
        # calculate their idf
        # loop through all docs
        # calculate tf-idf for each docs

        for w in norm_query:
            idf_dic[w] = tfidf_calculator.idf(w, docs)

        for ann in anns:
            cap_id = ann["id"]
            tfidf_dic[cap_id] = 0
            for w in norm_query:
                tfidf_dic[cap_id] = tfidf_dic[cap_id] + tfidf_calculator.tf(w, ann["caption"]) * idf_dic[w]

        sorted_tfidf = sorted(tfidf_dic.items(), key=operator.itemgetter(1))
        sorted_tfidf.reverse()

        list_top10 = []
        for i in range(1, 10):
            print(sorted_tfidf[i])
            list_top10.append(sorted_tfidf[i][0])

        for ann in anns:
            for cap_id in list_top10:
                if ann["id"] == cap_id:
                    print(ann["caption"])

        # for ann in data["annotations"]:
        #     print(ann["caption"])

        #print(data["annotations"][0]["caption"])