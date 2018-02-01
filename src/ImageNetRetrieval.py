import re

SYNSET_PATH = "./data/synset_words.txt"
IN_URL_PATH = "./data/fall11_urls.txt"

# limited at 10 images per wnid are retrieved
IMAGE_PER_WNID = 10

# search for synsets containing the query and get its wnid
def getWnid(query):
    wnid_list = []
    # read all lines in file
    # file will be closed automatically after reading process is completed ("with")
    with open(SYNSET_PATH) as f:
        for line in f:
            m_re = r"" + query + r"\W"
            if re.search(m_re, line, re.IGNORECASE):
                # get wnid (9 characters)
                wnid_list.append(line[:9])

    return wnid_list

def getUrl(wnid):
    with open(IN_URL_PATH) as f:
        cnt = 0
        url_list = []
        for line in f:
            # string start with wnid
            m_re = r"^" + wnid + r""
            # url pattern
            url_re = r"http://\S*$"
            if re.search(m_re, line, re.IGNORECASE):
                url_list.append(re.search(url_re, line, re.IGNORECASE).group())
                cnt += 1
            if (cnt >= IMAGE_PER_WNID):
                break

    return url_list

def getUrlFromQuery(query):
    url_list = []
    wnid_list = getWnid(query)
    for wnid in wnid_list:
        url_list += getUrl(wnid)

        # put temporarily for test
        break

    return url_list
