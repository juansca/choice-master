from django.contrib import admin

from chm.models import Subject
from chm.models import Topic
from chm.models import Question
from chm.models import Answer


class AnswerInline(admin.TabularInline):
    extra = 1
    model = Answer
    fields = ('is_correct', 'text',)


class QuestionAdmin(admin.ModelAdmin):
    model = Question
    inlines = (AnswerInline,)


admin.site.register(Question, QuestionAdmin)
admin.site.register(Subject)
admin.site.register(Topic)
