import re
import urllib.parse as urlparse
from urllib.parse import urlencode


def extract_integer(text):
    for t in text.split(' '):
        if t.isdigit():
            return int(t)


def extract_number_with_two_decimals(text):
    pattern = r"([0-9]{1,}\.[0-9]{2})"
    x = re.search(pattern, text)
    return x.group()


def mode_of_array(array):
    counts = {}
    compare = 0
    most_frequent = None
    for i in range(len(array)):
        word = array[i]
        if not counts.get(word):
            counts[word] = 1
        else:
            counts[word] += 1
        if counts[word] > compare:
            compare = counts[word]
            most_frequent = array[i]
    return most_frequent


def update_url_query(url, data):
    url_parse = urlparse.urlparse(url)
    query = url_parse.query
    url_dict = dict(urlparse.parse_qsl(query))
    url_dict.update(data)
    url_new_query = urlparse.urlencode(url_dict)
    url_parse = url_parse._replace(query=url_new_query)
    new_url = urlparse.urlunparse(url_parse)
    return new_url

