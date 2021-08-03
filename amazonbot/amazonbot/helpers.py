def extract_integer(text):
    for t in text.split(' '):
        if t.isdigit():
            return int(t)
