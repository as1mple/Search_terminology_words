import xml.etree.ElementTree as ET
from nltk.corpus import stopwords
import spacy
import gzip
import csv
import re

FILENAME_TO_SAVE = 'TITLE.csv'
path = 'enwiki-latest-abstract.xml.gz'
stop_words = set(stopwords.words('english'))
nlp = spacy.load("en_core_web_sm")

users = [
    ["Word"],
]
with open(FILENAME_TO_SAVE, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerows(users)


def clean_spam_info(word: str) -> bool:
    count = 0
    for el in word.split():
        for symbol in el:
            if symbol.isupper():
                count += 1
                if count > 1:
                    return False
    if not (all(ord(c) < 128 for c in word)):
        return False
    if len(re.sub(r'[^0-9]', '', word)) > 0:
        return False
    return True


with gzip.open(path) as xml_file:
    for event, elem in ET.iterparse(xml_file, events=("start", "end")):
        if elem.tag == "title" and event == "end":
            word = str(elem.text).split(' ', 1)[1]
            if len(word) > 2:
                Flag = True
                doc = nlp(word)
                for ent in doc.ents:
                    Flag = False
                if not (word.lower() in stop_words) and Flag and clean_spam_info(word=word):
                    with open(FILENAME_TO_SAVE, "a", newline="") as file:
                        writer = csv.writer(file)
                        writer.writerows([[word]])
