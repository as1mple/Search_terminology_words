from nltk import sent_tokenize
from nltk import word_tokenize
from threading import Thread
from keybert import KeyBERT
import pandas as pd
import argparse
import json
import re


def initialization() -> tuple:
    parser = argparse.ArgumentParser(description='Test')
    parser.add_argument('-path_to_dict', type=str, default='TITLE.csv')
    parser.add_argument('-path_to_text', type=str, default='text.txt')
    parser.add_argument('-path_to_save', type=str, default='save.json')

    args = parser.parse_args()
    return args.path_to_dict, args.path_to_text, args.path_to_save


PATH_TO_DICT, PATH_TO_TEXT, PATH_TO_SAVE = initialization()
data = set(map(lambda word: word.lower(), list(pd.read_csv(PATH_TO_DICT).Word)))
model = KeyBERT('distilbert-base-nli-mean-tokens')
result = {}
key_words = set()


class FindThread(Thread):

    def __init__(self, word, sent_index, word_index):
        Thread.__init__(self)
        self.word = word
        self.sent_index = sent_index
        self.word_index = word_index

    def run(self):
        if self.word in data:
            update_dict(dict_=result, key=self.word, value=[self.sent_index, self.word_index])


def main(text: str, sent_index) -> None:
    for index_word, word in enumerate(word_tokenize(text)):
        thread = FindThread(word, sent_index, index_word)
        thread.start()


def update_dict(dict_: dict, key: str, value) -> None:
    el = dict_.get(key, 'error')
    if el == 'error':
        dict_.update({key: [value]})
    else:
        el.append(value)


def common_words(key_words: list) -> list:
    return [el for el in key_words if el in data]


with open(PATH_TO_TEXT, 'r') as code_book:
    for sent_index, sent in enumerate(sent_tokenize(code_book.read())):

        try:
            n1 = model.extract_keywords(sent.lower(), keyphrase_length=1, use_maxsum=True)
            n2 = model.extract_keywords(sent.lower(), keyphrase_length=2, use_maxsum=True)
            key_words = key_words.union(set(n1 + n2))

        except Exception as e:
            e = e

        main(sent, sent_index)

with open(PATH_TO_SAVE, 'w') as fp:
    json.dump(result, fp)

bert_words = common_words(key_words=key_words)
text = open(PATH_TO_TEXT, 'r')
text = text.read()
key_res = {}

for i in bert_words:
    index = []
    for match in re.finditer(i.split()[0], text):
        index.append((match.start(), match.end()))
    key_res.update({i: index})

with open(f"BERT_version_{PATH_TO_SAVE}", 'w') as fp:
    json.dump(key_res, fp)