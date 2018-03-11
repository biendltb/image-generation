import json
import operator
import time

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

    def __init__(self):

        with open(self.IMG_DETAIL_PATH) as data_file:
            data = json.load(data_file)

        # all annotations
        self.anns = data["annotations"]
        # all image information
        self.ims = data["images"]

    # return list of top cap id
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
                tfidf_dic[cap_id] = tfidf_dic[cap_id] + tfidf_calculator.tf(w, cap_content) * idf_dic[w]
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