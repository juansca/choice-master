from django.db import models
from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from django.contrib import messages
from django.contrib.auth.models import User


class Subject(models.Model):
    """
    """
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=500)


class Topic(models.Model):
    """
    """
    name = models.CharField(max_length=200)
    subject = models.ForeignKey('Subject')


class Question(models.Model):
    """
    """
    topic = models.ForeignKey('Topic')
    text = models.CharField(max_length=300)


class Answer(models.Model):
    """
    """
    text = models.CharField(max_length=300)
    question = models.ForeignKey('Question')
    is_correct = models.BooleanField(default=False)


class Flag(models.Model):
    """
    A question flagged by a user
    """
    question = models.ForeignKey('Question')
    datetime = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User)
    description = models.TextField()


@receiver(user_signed_up)
def user_signed_up_callback(sender, request, user, **kwargs):
    messages.success(request, 'Se ha registrado exitosamente!')
