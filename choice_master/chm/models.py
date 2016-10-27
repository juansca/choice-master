from allauth.account.signals import user_signed_up
from chm import similarity
from choice_master import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _


class XMLFile(models.Model):
    """
    The option to upload questions from files
    """
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
    A specidic topic related to the subject
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

    def is_repeated(self):
        return Question.objects.filter(text=self.text,
                                       topic=self.topic).exists()

    def similar_exists(self):
        queryset = Question.objects.filter(topic=self.topic)
        return similarity.similar_exists(self, queryset)

    def clean(self):
        if self.is_repeated():
            raise ValidationError(_('The question already exists'))

        if self.similar_exists():
            raise ValidationError(_('A similar question already exists'))


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
    Proxy model used to manage flagged questions
    """

    class Meta:
        proxy = True


@receiver(user_signed_up)
def user_signed_up_callback(sender, request, user, **kwargs):
    messages.success(request, 'You signed up succesfully !')
