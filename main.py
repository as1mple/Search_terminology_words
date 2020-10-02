import httplib2 as httplib2
from bs4 import BeautifulSoup, SoupStrainer


def scrapper_page(request):
    URL = f"https://ru.wikipedia.org/wiki/{request}"
    http = httplib2.Http()
    _, response = http.request(URL)
    return [words['title'] for words in BeautifulSoup(response, parse_only=SoupStrainer('a')) if
            words.has_attr('title')]



