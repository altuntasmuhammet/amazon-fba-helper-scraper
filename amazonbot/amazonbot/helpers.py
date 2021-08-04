import re


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
