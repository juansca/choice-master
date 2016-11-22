"""
Test voting funcionality
"""
from unittest import TestCase
from chm.models import Question
from chm.models import Subject
from chm.models import Topic


SUBJECT = Subject.objects.create(name='S')
TOPIC = Topic.objects.create(name='Test_topic', subject=SUBJECT)


def batch_voting(*votes):
    """ Create a question, vote all votes and return difficulty
    :param: *votes list of int
    """
    question = Question.objects.create(text='?', topic=TOPIC)
    for vote in votes:
        question.vote(vote)
    return question.difficulty


class TestVoting(TestCase):
    """Test voting combinations and check question difficulty"""

    def test_vote_one(self):
        for i in range(5):
            self.assertEqual(batch_voting(i), i)

    def test_two_equal_votes(self):
        for i in range(5):
            self.assertEqual(batch_voting(i, i), i)

    def test_three_equal_votes(self):
        for i in range(5):
            self.assertEqual(batch_voting(i, i, i), i)

    def test_a_lot_of_equal_votes(self):
        for i in range(5):
            self.assertEqual(batch_voting(*([i] * 100)), i)

    def test_dot_zero_does_not_change(self):
        cases = (
            ((1, 5), 3),
            ((1, 3), 2),
            ((2, 4), 3),
            ((3, 5), 4),
            ((2, 5, 5), 4),
        )
        for votes, expected_difficulty in cases:
            self.assertEqual(batch_voting(*votes), expected_difficulty)

    def test_dot_five_rounds_down(self):
        cases = (
            ((1, 2), 1),  # 1.5 -> 1
            ((2, 3), 2),  # 2.5 -> 2
            ((3, 4), 3),  # etc.
            ((4, 5), 4),
        )
        for votes, expected_difficulty in cases:
            self.assertEqual(batch_voting(*votes), expected_difficulty)

    def test_dot_four_rounds_down(self):
        cases = (
            ((1, 1, 1, 1, 1, 1, 1, 1, 2, 3, 1), 1),  # 1.4 -> 1
            ((2, 2, 2, 2, 2, 2, 2, 2, 4, 3, 1), 2),  # 2.4 -> 2
        )
        for votes, expected_difficulty in cases:
            self.assertEqual(batch_voting(*votes), expected_difficulty)

    def test_dot_six_rounds_up(self):
        cases = (
            ((1, 1, 1, 1, 4), 2),  # 1.6 -> 2
            ((5, 5, 1, 1, 1), 3),  # 2.6 -> 3
        )
        for votes, expected_difficulty in cases:
            self.assertEqual(batch_voting(*votes), expected_difficulty)
