"""
Models for app chm
"""

# python imports
from allauth.account.signals import user_signed_up
from model_utils import Choices
from math import floor

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

    def learning_coeff(self, user):
        """Return user knowledge as a float in [0..10]"""

        # get all topics, even if user didn't answer any questions yet
        topics = self.topics.all()
        try:
            lc = sum([t.learning_coeff(user) for t in topics]) / topics.count()
        except ZeroDivisionError:
            lc = float()  # 0.0
        return lc

    def similar_exists(self):
        """
        Check if a subject in the database has the same name (ignoring case)
        than the question.
        :return: True only if a subject with the same name ignoring case exists
        in the database
        :rtype: bool
        """
        queryset = Subject.objects.exclude(pk=self.pk)

        for q in queryset:
            if self.name.lower() == q.name.lower():
                return True
        return False

    def clean(self):
        if self.similar_exists():
            raise ValidationError(_('A similar subject already exists'))

    def __str__(self):
        return self.name


class Topic(models.Model):
    """
    A specific topic related to the subject
    """
    name = models.CharField(max_length=200)
    subject = models.ForeignKey('Subject', related_name='topics')

    def learning_coeff(self, user):
        """Return user knowledge as a float in [0..10]"""
        qoq = QuestionOnQuiz.objects.filter(
            question__topic=self,
            quiz__user=user,
            quiz__state=Quiz.STATUS.finished,
        ).exclude(state=QuestionOnQuiz.STATUS.not_answered)

        correct = qoq.filter(state=QuestionOnQuiz.STATUS.right)
        try:
            lc = correct.count() / qoq.count()
        except ZeroDivisionError:
            lc = float()  # 0.0
        return lc * 100

    def similar_exists(self):
        """
        Check if a Topic in the database has the same name (ignoring case)
        than the question.
        :return: True only if a Topic with the same name ignoring case exists
        in the database
        :rtype: bool
        """
        queryset = Topic.objects.filter(
            subject=self.subject
        ).exclude(
            pk=self.pk)

        for q in queryset:
            if self.name.lower() == q.name.lower():
                return True
        return False

    def clean(self):
        try:
            if self.similar_exists():
                raise ValidationError(_('A similar topic already exists'))
        except Subject.DoesNotExist:
            pass

    def __str__(self):
        return '{} ({})'.format(self.name, self.subject)


class Question(models.Model):
    """Question Model"""
    topic = models.ForeignKey('Topic')
    text = models.CharField(max_length=300)
    number_ranked = models.IntegerField(default=0)
    ranked_score = models.IntegerField(default=0)

    @staticmethod
    def round_down(n):
        """Round down floating number n"""
        if n - floor(n) == 0.5:
            return floor(n)
        return round(n)

    def avg_rank(self):
        """Return the answer's average ranking score"""
        if self.ranked_score == 0:
            return 1
        return self.round_down(self.usr_ranked_score *
                               (number_ranked - 1) /
                               self.number_ranked)

    def __str__(self):
        return self.text

    def is_repeated(self):
        """
        Check if an identical question exists in the database.
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
        queryset = Question.objects.filter(
            topic=self.topic
        ).exclude(pk=self.pk)
        for q in queryset:
            if is_similar(self.text, q.text):
                return True
        return False

    def clean(self):
        try:
            if self.is_repeated():
                raise ValidationError(_('The question already exists'))
        except Topic.DoesNotExist:
            pass

    def to_json(self):
        """"Converts a Question to json format"""
        return {
            'id': self.id,
            'text': self.text,
            'topic': self.topic.name,
            'topic_id': self.topic.pk,
            'answers': [a.to_json() for a in self.answers.all()]
        }


class Answer(models.Model):
    """Answer Model"""
    text = models.CharField(max_length=300)
    question = models.ForeignKey('Question', related_name='answers')
    is_correct = models.BooleanField(default=False)

    def to_json(self):
        """Converts a Answer to json format"""
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

    def score(self, **kwargs):
        """Return float indicating ratio of correct answers"""
        qq = QuestionOnQuiz.objects.filter(quiz=self, **kwargs)
        correct = qq.filter(state=QuestionOnQuiz.STATUS.right)
        try:
            score = correct.count() / qq.count()
        except ZeroDivisionError:
            score = 0
        return score * 100

    def detailed_score(self):
        """Return queryset detailing total amount of answers in each state"""
        qq = QuestionOnQuiz.objects.filter(quiz=self)
        return qq.values('state').annotate(total=Count('state'))

    def to_json(self, exclude_answered=False):
        """"
            Converts a Quiz to json format. Only save id and seconds to
            use them later
        """
        result = {
            'id': self.id,
            'seconds': self.seconds_per_question,
        }

        questions_qs = QuestionOnQuiz.objects.filter(quiz=self)

        if exclude_answered:
            questions_qs = questions_qs.filter(
                state=QuestionOnQuiz.STATUS.not_answered
            )

        result['questions'] = [qoq.question.to_json() for qoq in questions_qs]
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
