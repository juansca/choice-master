from django.db import models
from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from django.contrib import messages
from django.contrib.auth.models import User
from choice_master import settings


class XMLFile(models.Model):
    """
    """
    topic = models.ForeignKey('Topic')
    file = models.FileField(upload_to=settings.MEDIA_ROOT)


class Subject(models.Model):
    """
    """
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=500)

    def __str__(self):
        return self.name


class Topic(models.Model):
    """
    """
    name = models.CharField(max_length=200)
    subject = models.ForeignKey('Subject')

    def __str__(self):
        return '{} ({})'.format(self.name, self.subject)


class Question(models.Model):
    """
    """
    topic = models.ForeignKey('Topic')
    text = models.CharField(max_length=300)

    def __str__(self):
        return self.text


class Answer(models.Model):
    """
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
    """Proxy model used to manage
    flagged questions"""

    class Meta:
        proxy = True


@receiver(user_signed_up)
def user_signed_up_callback(sender, request, user, **kwargs):
    messages.success(request, 'Se ha registrado exitosamente!')
