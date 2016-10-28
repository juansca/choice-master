from os import path
from lxml import etree
from choice_master.settings import BASE_DIR


class XMLParser(object):
    SCHEMA_PATH = path.join(BASE_DIR, 'static', 'xml_files', 'question.xml')

    def __init__(self, xmlfile):
        """
        Create a new XMLParser using the given file.
        :param xmlfile: The file object to parse
        :xmlfile: xml file-like object
        :return: None
        :rtype: NoneType
        """
        with open(self.SCHEMA_PATH, "r") as f:
            xmlschema_doc = etree.parse(f)
        self.schema = etree.XMLSchema(xmlschema_doc)
        self.xmlfile = xmlfile

    def parse_questions(self):
        """
        Yield dictionary containing a question parsed from the file setted
        after creating the object. A file might contain several questions, thus
        several dictionaries might be yielded. A dictionary contains only the
        information of one question.

        :return: A dictionary containing: 'subject' (string), 'topic' (string),
        'question' (string), 'answers' (list of dictionaries containing: 'text'
        (string) and 'is_correct' (bool)).

        :rtype: dict
        """
        gen = etree.iterparse(self.xmlfile, tag='question', schema=self.schema)
        for _, data in gen:
            result = {'subject': data.attrib['subject'],
                      'topic': data.attrib['topic'],
                      'question': data[0].text,
                      'answers': []}

            for i in range(1, len(data)):
                ans = {'text': data[i].text,
                       'is_correct': data[i].tag is "correct"}
                result['answers'].append(ans)

            yield result
