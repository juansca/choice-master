def distance(str1, str2):
    """

    :param str1: String to compute distance
    :param str2: String to compute distance
    :return: the Lehvenstein distance between str1 and str2
    """
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
    """

    :param str1: String to verify the similarity
    :param str2: String to verify the similarity
    :return: If the distance between str1 and str2 is short enough, we consider
             that are similar
    """
    return distance(str1, str2) < 5


def similar_exists(pquestion, dbtopic_questions):
    """

    :param pquestion: a Question model object to verify if a similar question
                      is in the db
    :param dbtopic_questions: a QuerySet with all the questions that has the
                              same topic that pquestion
    :return: True if a similar question exists
    """
    some_similar = False
    for db_question in dbtopic_questions.values('text'):
        dbqtext = db_question['text']
        some_similar = some_similar or is_similar(pquestion.text, dbqtext)
        if some_similar:
            break
    return some_similar
