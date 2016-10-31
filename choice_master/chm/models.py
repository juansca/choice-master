"""
Models for app chm
"""

# python imports
from allauth.account.signals import user_signed_up
from model_utils import Choices

# django imports
from django.db import models
from django.db.models import Count
from django.dispatch import receiver
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

# project imports
from choice_master import settings
from chm.similarity import is_similar


class XMLFile(models.Model):
    """
    The XMLFile object is used to upload files to the server in order to
    support bulk uploading of questions and answers to the database.
    No instace of this object will actually exist in the database.
    """
    file = models.FileField(upload_to=settings.MEDIA_ROOT)


class Subject(models.Model):
    """Subject Model"""
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
    """Question Model"""
    topic = models.ForeignKey('Topic')
    text = models.CharField(max_length=300)

    def __str__(self):
        return self.text

    def is_repeated(self):
        """
        Check if a identical question exists in the database.
        :return: True only if an identical question exists in the database
        :rtype: bool
        """
        return Question.objects.filter(
            text=self.text,
            topic=self.topic
        ).exclude(
            pk=self.pk
        ).exists()

    def similar_exists(self):
        """
        Check if a similar question exists in the database.
        :return: True only if a similar question exists in the database
        :rtype: bool
        """
        queryset = Question.objects.filter(topic=self.topic).exclude(pk=self.pk)
        for q in queryset:
            if is_similar(self.text, q.text):
                return True
        return False

    def clean(self):
        if self.is_repeated():
            raise ValidationError(_('The question already exists'))

        if self.similar_exists():
            raise ValidationError(_('A similar question already exists'))

    def to_json(self):
        return {
            'id': self.id,
            'text': self.text,
            'topic': self.topic.name,
            'answers': [a.to_json() for a in self.answers.all()]
        }


class Answer(models.Model):
    """Answer Model"""
    text = models.CharField(max_length=300)
    question = models.ForeignKey('Question', related_name='answers')
    is_correct = models.BooleanField(default=False)

    def to_json(self):
        return {
            'id': self.id,
            'text': self.text,
        }

    def __str__(self):
        return self.text


class Flag(models.Model):
    """
    Flag Model. An instance of this model indicates that a question has been
    flagged by some user.
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

    STATUS = Choices(
        'in_progress',
        'finished',
        'aborted',       # the user never finished the quiz
    )
    # the user taking the exam
    user = models.ForeignKey(User)

    # when did the user ask to take an exam
    datetime = models.DateTimeField(auto_now_add=True)

    # selected topics
    topics = models.ManyToManyField('Topic')

    # USER CONFIGURATION

    # amount of questions
    nr_of_questions = models.IntegerField()

    # time available to answer each question (in seconds)
    seconds_per_question = models.IntegerField()

    state = models.CharField(choices=STATUS,
                             default=STATUS.in_progress,
                             max_length=20)

    def score(self):
        """Return float indicating ratio of correct answers"""
        qq = QuestionOnQuiz.objects.filter(quiz=self)
        correct = qq.filter(state=QuestionOnQuiz.STATUS.right)
        score = correct.count() / float(qq.count())
        return score * 100

    def detailed_score(self):
        """Return queryset detailing total amount of answers in each state"""
        qq = QuestionOnQuiz.objects.filter(quiz=self)
        return qq.values('state').annotate(total=Count('state'))

    def to_json(self):
        result = {
            'id': self.id,
            'seconds': self.seconds_per_question,
            'questions': [qoq.question.to_json()
                          for qoq in QuestionOnQuiz.objects.filter(quiz=self)]
        }
        return result


class QuestionOnQuiz(models.Model):
    """
    A question on a Quiz deserves its own table.
    This way we can keep track of interesting
    things like user answers, e.g:

        >>> user = User.objects.get(some_query)
        >>> topic = Topic.objecs.filter(some_other_query)
        >>> qq = QuestionOnQuiz.objects.filter(quiz__user=user,
                                               question__topic=topic)
        >>> right = qq.filter(status=QuestionOnQuiz.STATUS.right)
        >>> score = right / float(qq.count())

    We also could later add attributes to this relationship,
    for example, time spent on giving the actual answer.
    """

    STATUS = Choices(
        'not_answered',  # the user didn't provide answer
        'wrong',         # the user missed the question
        'right'          # the user provided the right answer
    )

    question = models.ForeignKey('Question')
    quiz = models.ForeignKey('Quiz', related_name='questions')
    state = models.CharField(choices=STATUS,
                             default=STATUS.not_answered,
                             max_length=20)


@receiver(user_signed_up)
def user_signed_up_callback(sender, request, user, **kwargs):
    messages.success(request, 'You signed up succesfully !')
