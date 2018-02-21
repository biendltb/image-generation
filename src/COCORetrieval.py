import json

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

        for ann in data["annotations"]:
            print(ann["caption"])

        #print(data["annotations"][0]["caption"])