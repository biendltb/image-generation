import re
import math
import json

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