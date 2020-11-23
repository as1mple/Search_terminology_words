import csv
from lxml import etree as et
from bz2file import BZ2File

FILENAME = "Index_words_eng.csv"  # file to save
path = "eng.xml.bz2"

index = 0

users = [
    ["Index", "Word"],
]
with open(FILENAME, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerows(users)

with BZ2File(path) as xml_file:
    parser = et.iterparse(xml_file, events=('end',))
    for events, elem in parser:

        if elem.tag == "{http://www.mediawiki.org/xml/export-0.10/}title":
            with open(FILENAME, "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerows([[index, elem.text.lower()]])

        elif elem.tag == "{http://www.mediawiki.org/xml/export-0.10/}text":
            file = open(f"dataset_eng/{index}.txt", "w")
            file.write(str(elem.text))
            file.close()
            index += 1
        elem.clear()

    while elem.getprevious() is not None:
        del elem.getparent()[0]
