from django.contrib import admin

from chm.models import Answer
from chm.models import FlaggedQuestion
from chm.models import Question
from chm.models import Subject
from chm.models import Topic


class AnswerInline(admin.TabularInline):
    extra = 1
    model = Answer
    fields = ('is_correct', 'text',)


class QuestionAdmin(admin.ModelAdmin):
    model = Question
    inlines = (AnswerInline,)


class FlaggedQuestionAdmin(admin.ModelAdmin):

    list_display = ('text', 'flags_count')
    fields = ('text',)
    inlines = (AnswerInline,)

    change_form_template = 'change_flagged_question.html'

    def flags_count(self, request):
        return Question.objects.filter(flags__isnull=False).count()
    flags_count.short_description = 'Cantidad de denuncias'

    def get_queryset(self, request):
        return Question.objects.filter(flags__isnull=False)

    def has_add_permission(self, request):
        return False


admin.site.register(Question, QuestionAdmin)
admin.site.register(FlaggedQuestion, FlaggedQuestionAdmin)
admin.site.register(Subject)
admin.site.register(Topic)
