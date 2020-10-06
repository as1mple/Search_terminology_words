import httplib2
from bs4 import BeautifulSoup, SoupStrainer
import urllib.parse


def scrapper_page(request: set, tag: str) -> list:
    """Парсинг странцы с целью получения всех аргументов заданного тега"""
    URL = f"https://ru.wikipedia.org/wiki/{request}"
    http = httplib2.Http()
    _, response = http.request(URL)
    return list(set([words[tag] for words in BeautifulSoup(response, parse_only=SoupStrainer('a')) if
                     words.has_attr(tag)]))


def filter_url(array: list) -> list:
    """Удаление лишних ссылок которые не ссылаються на термины"""
    return [i[6:] for i in list(filter(lambda x: 1 if x[:5] == "/wiki" else 0, array))]


def decode_name(array: list) -> list:
    """Декодирование ссылок в нормальный формат"""
    return [urllib.parse.unquote(i) for i in array]


def filtred_and_control(array: list):
    """Превращение листа в сет и обратно с контролем обьма  искомых слов"""
    array = list(set(array))
    if len(array) > 5_000:
        exit(-1)


result = ["Радиоактивный_распад"]  # Первый элемент этого листа является стартовым словом, в процессе выполнения -
# все уникальнные найденные слова будут добавляться сюда

[print(word, len(result)) or result.append(word) or filtred_and_control(result) for i in result for word in
 decode_name(filter_url(scrapper_page(i, 'href')))]
