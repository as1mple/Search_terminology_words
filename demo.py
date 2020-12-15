from text_extration import Extract
from clean_text import *
from pyate.term_extraction_pipeline import TermExtractionPipeline
import spacy
import os
import pandas as pd

result = {}
# Каталог из которого будем брать файлы
directory = 'Samples for term extractor'

# Получаем список файлов в переменную files
for index, name in enumerate(os.listdir(directory)):
    ex = Extract(f"{directory}/{name}")
    if ex is None:
        continue
    text = ex.extract()
    text = re.sub(r"[^A-Za-z.]", " ",
                  text)

    text = remove_stop_words_eng(text)
    nlp = spacy.load("en_core_web_sm")
    nlp.add_pipe(TermExtractionPipeline())
    doc = nlp(text)
    # doc._.combo_basic.sort_values(ascending=False).to_csv(f'save/{name}.csv')
    print("================================================================")
    result.update({index: dict(doc._.combo_basic.sort_values(ascending=False))})
    # print(dict(doc._.combo_basic.sort_values(ascending=False))
    #       )


def update_score(global_dict: dict, key: str, value, index_doc):
    last_value = global_dict.get(key, 0)
    if last_value == 0:
        global_dict.update({key: {'weight': value,
                                  'in_document': [index_doc]}})

    elif last_value['weight'] < value:

        global_dict[key]['weight'] = value
        global_dict[key]['in_document'].append(index_doc)


global_dict = {}
for index, dict_ in result.items():

    for key, value in dict_.items():
        update_score(global_dict=global_dict, key=key, value=value, index_doc=index)


def duplicate(global_dict, global_dict_keys):
    clean_terms = set()
    for el in global_dict_keys:
        tmp = el
        for el1 in global_dict_keys:
            if tmp == el1:
                continue
            if len(set(tmp.lower().split()) & set(el1.lower().split())) > 1:
                #                 print(tmp, len(tmp), 'vs', el1, len(el1))
                if global_dict[el1]['weight'] > global_dict[tmp]['weight']:
                    tmp = el1
        clean_terms.add(tmp)
    if len(global_dict_keys) > len(clean_terms):
        return clean_terms, True
    else:
        return clean_terms, False


n = set(list(global_dict.keys()))
Flag = True
while Flag:
    n, Flag = duplicate(global_dict, n)

result = {key: global_dict[key] for key in n}
res = sorted(result.items(), key=lambda x: x[1]['weight'])
res.reverse()
res = {k: v for k, v in res}

data = pd.DataFrame({"term": value} for value in list(res.keys()))

data['weight'] = [i['weight'] for i in list(res.values())]
data['in_document'] = [i['in_document'] for i in list(res.values())]
data.to_csv('save2.csv')
