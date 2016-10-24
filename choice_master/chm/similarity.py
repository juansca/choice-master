from chm.models import Question


def repeated(question):
    return Question.objects.filter(text=question.text).exists()


def similar_exists(question):
    return False
