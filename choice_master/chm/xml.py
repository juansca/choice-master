from lxml.etree import XMLSchema
from lxml.etree import iterparse
from lxml.etree import parse
from chm.models import Question
from chm.models import Answer
from choice_master.settings import BASE_DIR
import os

xml_schema_path = os.path.join(BASE_DIR, 'static', 'xml_files', 'question.xml')

def get_schema():
    with open(xml_schema_path, "r") as g:
        xml_schema_doc = parse(g)
    xml_schema = XMLSchema(xml_schema_doc)
    return xml_schema

def load_questions(xml_file):
    schema = get_schema()
    for _, question_data in iterparse(xml_file, tag='question', schema=schema):
        question = Question()
        question.text = question_data[0].text
        answers = []

        for i in range(1, len(question_data)):
            answer = Answer(text=question_data[i].text,
                            question=question,
                            is_correct=(question_data[i].tag is "correct"))
            answers.append(answer)

        question_data.clear()
        yield question, answers
