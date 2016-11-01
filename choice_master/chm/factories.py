import factory
import factory.django
from . import models


class SubjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Subject


class TopicFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Topic


class QuestionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Question


class AnswerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Answer


class FlagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Flag
