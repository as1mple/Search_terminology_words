from pyate.term_extraction_pipeline import TermExtractionPipeline
from nltk.tokenize import word_tokenize
from text_extration import Extract
from nltk.corpus import stopwords
import pandas as pd
import spacy
import os
import re


class TermsExtraction:

    def __init__(self, directory, nlp: spacy):
        self.directory = directory
        self.nlp = nlp
        self.nlp.add_pipe(TermExtractionPipeline())
        self.result_extract_terms = {}  # рузультат извлечение терминов из текста
        self.cleaning_dict_terms = {}  # результат удаление корелирующих фраз

    def get_terms_dict_with_text(self, text) -> dict:
        doc = self.nlp(text)
        return dict(doc._.combo_basic.sort_values(ascending=False))

    def get_clean_terms(self):
        return self.cleaning_dict_terms

    def get_extract_terms(self):
        return self.result_extract_terms

    @staticmethod
    def update_score(global_dict: dict, key: str, value, index_doc):
        last_value = global_dict.get(key, 0)
        if last_value == 0:
            global_dict.update({key: {'weight': value,
                                      'in_document': [index_doc]}})

        elif last_value['weight'] < value:

            global_dict[key]['weight'] = value
            global_dict[key]['in_document'].append(index_doc)

    def conveyor(self, remove_all_except_letter_dot, remove_stop_words):

        for name in os.listdir(self.directory):
            text = Extract(f"{self.directory}/{name}").extract()
            if text is None:
                continue

            text = remove_stop_words(remove_all_except_letter_dot(text))

            print("=" * 20)
            self.result_extract_terms.update({name: self.get_terms_dict_with_text(text=text)})

    @staticmethod
    def duplicate(global_dict, global_dict_keys):
        clean_terms = set()
        for el in global_dict_keys:
            tmp = el
            for el1 in global_dict_keys:
                if tmp == el1:
                    continue
                if len(set(tmp.lower().split()) & set(el1.lower().split())) > 0:
                    if global_dict[el1]['weight'] > global_dict[tmp]['weight']:
                        tmp = el1
            clean_terms.add(tmp)
        if len(global_dict_keys) > len(clean_terms):
            return clean_terms, True
        else:
            return clean_terms, False

    @staticmethod
    def duplicate_lemms(list_terms, global_dict, lemma_dict):
        clean_terms = set()
        for k1 in list_terms:
            tmp = k1
            tmp_v1 = lemma_dict[k1]
            for k2 in list_terms:
                v2 = lemma_dict[k2]
                if tmp_v1 == v2:
                    continue
                if len(set(tmp_v1.lower().split()) & set(v2.lower().split())) > 0:
                    if global_dict[k2]['weight'] > global_dict[k1]['weight']:
                        tmp = k2
                        tmp_v1 = v2

            clean_terms.add(tmp)

        if len(list_terms) > len(clean_terms):
            return clean_terms, True
        else:
            return clean_terms, False

    @staticmethod
    def lemma_dict(nlp, text):
        lemma_dict = {}
        for sent in text:
            tmp = set()
            for word in nlp(sent.lower()):
                tmp.add(word.lemma_)
            lemma_dict.update({sent: " ".join(tmp)})
        return lemma_dict

    def cleaning(self):
        cleaning_dict = {}
        for index, dict_ in self.result_extract_terms.items():
            for key, value in dict_.items():
                self.update_score(global_dict=cleaning_dict, key=key, value=value, index_doc=index)

        tmp_terms = set(list(cleaning_dict.keys()))
        flag = True
        while flag:
            tmp_terms, flag = self.duplicate(global_dict=cleaning_dict, global_dict_keys=tmp_terms)
        self.cleaning_dict_terms = {key: cleaning_dict[key] for key in tmp_terms}

        flag = True

        lemma_dict = self.lemma_dict(text=self.cleaning_dict_terms, nlp=self.nlp)
        list_terms = list(lemma_dict.keys())
        while flag:
            list_terms, flag = self.duplicate_lemms(list_terms=list_terms, global_dict=self.cleaning_dict_terms,
                                                    lemma_dict=lemma_dict)

        self.cleaning_dict_terms = {key: cleaning_dict[key] for key in list_terms}


def remove_all_except_letter_dot_eng(text: str) -> str:
    return re.sub(r"[^A-Za-z.]", " ",
                  text)


def remove_stop_words_eng(text: str) -> str:
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(text)
    filtered_sentence = []
    for w in word_tokens:
        if w not in stop_words:
            filtered_sentence.append(w)

    return " ".join(filtered_sentence)


extract = TermsExtraction(directory='Samples for term extractor', nlp=spacy.load("en_core_web_sm"))
extract.conveyor(remove_all_except_letter_dot=remove_all_except_letter_dot_eng, remove_stop_words=remove_stop_words_eng)
extract.cleaning()

res = extract.get_clean_terms()

res = sorted(res.items(), key=lambda x: x[1]['weight'])
res.reverse()
res = {k: v for k, v in res}

data = pd.DataFrame({"term": value} for value in list(res.keys()))

data['weight'] = [i['weight'] for i in list(res.values())]
data['in_document'] = [i['in_document'] for i in list(res.values())]
data.to_csv('save.csv')
