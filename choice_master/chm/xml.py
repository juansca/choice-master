from os import path
from lxml import etree
from chm import models
from choice_master.settings import BASE_DIR

xmlschema_path = path.join(BASE_DIR, 'static', 'xml_files', 'question.xml')


def get_schema():
    with open(xmlschema_path, "r") as g:
        xmlschema_doc = parse(g)
    xmlschema = etree.XMLSchema(xmlschema_doc)
    return xmlschema


def parse_questions(xmlfile):
    schema = get_schema()
    for _, question_data in etree.iterparse(xmlfile,
                                            tag='question',
                                            schema=schema):
        answers = []
        question = models.Question()
        question.text = question_data[0].text

        for i in range(1, len(question_data)):
            text = question_data[i].text
            is_correct = question_data[i].tag is "correct"
            answer = models.Answer(text=text, is_correct=is_correct)
            answers.append(answer)

        yield question, answers