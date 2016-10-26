"""
Models for app chm
"""

# python imports
from allauth.account.signals import user_signed_up
from model_utils import Choices

# django imports
from django.db import models
from django.dispatch import receiver
from django.contrib import messages
from django.contrib.auth.models import User

# project imports
from choice_master import settings


class XMLFile(models.Model):
    """
    The option to upload questions from files
    """
    name = models.CharField(max_length=200)
    topic = models.ForeignKey('Topic')
    file = models.FileField(upload_to=settings.MEDIA_ROOT)


class Subject(models.Model):
    """
    A subject that is mandatory to load a question
    """
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=500)

    def __str__(self):
        return self.name


class Topic(models.Model):
    """
    A specific topic related to the subject
    """
    name = models.CharField(max_length=200)
    subject = models.ForeignKey('Subject')

    def __str__(self):
        return '{} ({})'.format(self.name, self.subject)


class Question(models.Model):
    """
    A topic's question
    """
    topic = models.ForeignKey('Topic')
    text = models.CharField(max_length=300)

    def __str__(self):
        return self.text


class Answer(models.Model):
    """
    An answer for a question
    """
    text = models.CharField(max_length=300)
    question = models.ForeignKey('Question')
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class Flag(models.Model):
    """
    A question flagged by a user
    """
    question = models.ForeignKey('Question', related_name='flags')
    datetime = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User)
    description = models.TextField()


class FlaggedQuestion(Question):
    """
    Proxy model used to manage flagged questions.

    Its only purpose is to expose flagged questions
    to the system administrator through admin interface.

    See https://docs.djangoproject.com/es/1.10/ref/models/options/#proxy
    """

    class Meta:
        proxy = True


class Quiz(models.Model):
    """
    When a user takes an exam,
    an instance of Quiz is created.
    """

    # the user taking the exam
    user = models.ForeignKey(User)

    # when did the user ask to take an exam
    datetime = models.DateTimeField(auto_now_add=True)

    # selected topics
    topics = models.ManyToManyField('Topic')

    # user configuration: time available to
    # answer each question (in seconds)
    seconds_per_question = models.IntegerField()


class QuestionQuiz(models.Model):
    """
    A question in a Quiz deserves its own table.
    This way we can keep track of interesting
    things like user answer, or time spent to answer it
    """

    STATUS = Choices(
        'not_answered',  # the user didn't provide answer
        'wrong',         # the user missed the question
        'right'          # the user provided the right answer
    )

    # the question that become part of the exam
    question = models.ManyToManyField('Question')
    quiz = models.ForeignKey('Quiz')
    state = models.CharField(choices=STATUS,
                             default=STATUS.not_answered,
                             max_length=20)


class UserTopicScoring(models.Model):
    """
    To keep track of user performance
    and on which topics he or she could
    get better, we compute and save this
    scoring.

    Whenever a user misses a question about
    some topic, the scoring lowers somehow.
    On the other hand, if the user provides the
    right answer, this score rises.

    How the scoring is lowered or raised may
    vary depending on different policies.
    """

    user = models.ForeignKey(User)
    topic = models.ForeignKey(User)
    score = models.FloatField(default=0)

    class Meta:
        # Do not allow duplicates {user x topic}
        unique_together = ('user', 'topic')

    def raise_score(self):
        self.score += 1

    def lower_score(self):
        self.score -= 1.5


@receiver(user_signed_up)
def user_signed_up_callback(sender, request, user, **kwargs):
    messages.success(request, 'Se ha registrado exitosamente!')
