def distance(str1, str2):
    """
    Compute the Levenshtein distance between str1 and str2
    :param str1: String to compute distance
    :param str2: String to compute distance
    :type str1: string
    :type str2: string
    :return: the Levenshtein distance between str1 and str2
    :rtype: int
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
    Determine if the str1 is different from the str2
    :param str1: String to compare
    :param str2: String to compare
    :type str1: string
    :type str2: string
    :return: True only if the strings are similar
    :rtype: bool
    """
    return distance(str1, str2) < 5
