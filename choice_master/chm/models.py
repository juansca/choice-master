from allauth.account.signals import user_signed_up
from chm.similarity import is_similar
from choice_master import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _


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
    """Topic Model"""
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
        return Question.objects.filter(text=self.text,
                                       topic=self.topic).exists()

    def similar_exists(self):
        """
        Check if a similar question exists in the database.
        :return: True only if a similar question exists in the database
        :rtype: bool
        """
        queryset = Question.objects.filter(topic=self.topic)
        for q in queryset:
            if is_similar(self.text, q.text):
                return True
        return False

    def clean(self):
        if self.is_repeated():
            raise ValidationError(_('The question already exists'))

        if self.similar_exists():
            raise ValidationError(_('A similar question already exists'))


class Answer(models.Model):
    """Answer Model"""
    text = models.CharField(max_length=300)
    question = models.ForeignKey('Question')
    is_correct = models.BooleanField(default=False)

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
    """Proxy model used to manage flagged questions"""

    class Meta:
        proxy = True


@receiver(user_signed_up)
def user_signed_up_callback(sender, request, user, **kwargs):
    messages.success(request, 'You signed up succesfully !')
