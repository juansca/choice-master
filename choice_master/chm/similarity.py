from chm.models import Question


def distance(str1, str2):
    distance_table = dict()

    for i in range(len(str1) + 1):
        distance_table[i] = dict()
        distance_table[i][0] = i

    for i in range(len(str2) + 1):
        distance_table[0][i] = i

    for i in range(1, len(str1) + 1):
        for j in range(1, len(str2) + 1):
            distance_table[i][j] = min(distance_table[i][j - 1] + 1,
                                       distance_table[i - 1][j] + 1,
                                       distance_table[i - 1][j - 1] +
                                       (not str1[i - 1] == str2[j - 1]))
    return distance_table[len(str1)][len(str2)]


def is_similar(str1, str2):
    return distance(str1, str2) < 5


def repeated(pquestion):
    return Question.objects.filter(text=pquestion.text,
                                   topic=pquestion.topic).exists()


def similar_exists(pquestion):
    topic_questions = Question.objects.filter(topic=pquestion.topic)
    some_similar = False
    for db_question in topic_questions.values('text'):
        dbqtext = db_question['text']
        some_similar = some_similar or is_similar(pquestion.text, dbqtext)
        if some_similar:
            break
    return some_similar
