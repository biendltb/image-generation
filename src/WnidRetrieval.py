import re

SYNSET_URI = "./data/synset_words.txt"

# search for synsets containing the query and get its wnid
def getWnid(query):
    wnid_list = []
    # read all lines in file
    # file will be closed automatically after reading process is completed ("with")
    with open(SYNSET_URI) as f:
        for line in f:
            m_re = r"" + query + r"\W"
            if re.search(m_re, line, re.IGNORECASE):
                # get wnid (9 characters)
                wnid_list.append(line[:9])
    return wnid_list

