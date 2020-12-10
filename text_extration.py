import os
from urllib.request import urlopen

import textract
from bs4 import BeautifulSoup
from docx2txt import docx2txt
import extract_msg
from odf import text, teletype
from odf.opendocument import load


class Extract:
    def __init__(self, path: str):
        self.path = path
        self.UNIT_TO_MULTIPLIER = {
            '.docx': self.get_text_with_docx,
            '.txt': self.get_text_with_txt,
            '.eml': None,
            '.html': self.get_text_with_html,
            '.idml': None,
            '.msg': self.get_text_with_msg,
            '.mht': None,
            '.odt': self.get_text_with_odt,
            '.odp': None,
            '.ods': None,
            '.pdf': self.get_text_with_pdf,
            '.rtf': None,
            '.xls': None,
            '.xml': None,
            '.xps': None,
            '.zip': None
        }

    def extract(self):
        return self.switch_case()

    def get_format(self):
        filename, file_extension = os.path.splitext(self.path)
        return file_extension

    def switch_case(self) -> str:
        try:
            command = self.UNIT_TO_MULTIPLIER[self.get_format()]
            return command()
        except Exception as e:
            raise ValueError('Undefined unit: {}'.format(e.args[0]))

    def get_text_with_docx(self) -> str:
        return docx2txt.process(self.path)

    def get_text_with_txt(self) -> str:
        return textract.process(self.path)

    def get_text_with_html(self) -> str:
        html = urlopen(self.path).read()
        soup = BeautifulSoup(html, features="html.parser")

        # kill all script and style elements
        for script in soup(["script", "style"]):
            script.extract()  # rip it out

        # get text
        text = soup.get_text()

        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)

        return text

    def get_text_with_msg(self) -> str:
        return extract_msg.openMsg(self.path)

    def get_text_with_odt(self) -> str:
        textdoc = load(self.path)
        allparas = textdoc.getElementsByType(text.P)
        return teletype.extractText(allparas)

    def get_text_with_pdf(self) -> str:
        return textract.process(self.path)


PATH = ""
ex = Extract(PATH)
print(ex.extract())
