from django.contrib import admin

from chm.models import Answer
from chm.models import Flag
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
    list_display = ['get_text', 'get_topic_name', 'get_subject_name',]

    def get_text(self, obj):
        return obj.text
    get_text.short_description = 'Pregunta'

    def get_topic_name(self, obj):
        return obj.topic.name
    get_topic_name.admin_order_field = 'topic'
    get_topic_name.short_description = 'Tema'

    def get_subject_name(self, obj):
        return obj.topic.subject.name
    get_subject_name.short_description = 'Materia'

class TopicAdmin(admin.ModelAdmin):
    model = Topic
    list_display = [ 'get_name', 'get_subject_name',]

    def get_name(self, obj):
        return obj.name
    get_name.short_description = 'Tema'

    def get_subject_name(self, obj):
        return obj.subject.name
    get_subject_name.admin_order_field = 'subject'
    get_subject_name.short_description = 'Materia'


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

    def save_model(self, request, obj, form, change):
        """Delete all flags for this question"""
        Flag.objects.filter(question=obj).delete()


admin.site.register(Question, QuestionAdmin)
admin.site.register(FlaggedQuestion, FlaggedQuestionAdmin)
admin.site.register(Subject)
admin.site.register(Topic, TopicAdmin)
