from django.contrib import admin
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.conf.urls import url
from django.urls import reverse
from django.utils.html import format_html
from django.contrib import messages

from chm.models import Answer
from chm.models import Flag
from chm.models import FlaggedQuestion
from chm.models import Question
from chm.models import Subject
from chm.models import Topic
from chm.models import XMLFile

from chm.similarity import repeated
from chm.similarity import similar_exists

from chm.xml import parse_questions
from lxml.etree import XMLSyntaxError


class XMLFileAdmin(admin.ModelAdmin):
    model = XMLFile
    list_fields = ['load_questions_link']
    list_display = ['get_name', 'load_questions_link']

    def get_name(self, obj):
        return obj.name
    get_name.short_description = 'File'

    def load_questions_link(self, obj):
        dest = reverse('admin:chm_load_questions_link',
                       kwargs={'pk': obj.pk})
        return format_html('<a href="{url}">{title}</a>',
                           url=dest, title='Cargar Preguntas')
    load_questions_link.short_description = 'Cargar preguntas'
    load_questions_link.allow_tags = True

    def get_urls(self):
        urls = [
            url('^(?P<pk>\d+)/loadquestions/?$',
                self.admin_site.admin_view(self.load_questions_view),
                name='chm_load_questions_link'),
        ]
        return urls + super(XMLFileAdmin, self).get_urls()

    def load_questions_view(self, request, *args, **kwargs):
        obj = get_object_or_404(XMLFile, pk=kwargs['pk'])
        xmlfile = obj.file

        added_count = 0
        message_added = '%s preguntas fueron agregadas'

        similar_count = 0
        message_similar = '%s preguntas no fueron agregadas pues ya existían' \
                          ' similares en la base de datos.'

        repeated_count = 0
        message_repeated = '%s preguntas no fueron agregadas pues ya' \
                           ' existían en la base de datos.'
        message_syntax_error = 'Hubo un error de sintaxis. Por favor,' \
                               ' verifique la sintaxis del xml.'

        try:
            questions_gen = parse_questions(xmlfile)
            for question, answers in questions_gen:
                question.topic = obj.topic
                if Question.objects.filter(text=pquestion.text,
                                   topic=pquestion.topic).exists():
                    repeated_count += 1
                elif similar_exists(question, Question.objects.filter(topic=question.topic)):
                    similar_count += 1
                else:
                    added_count += 1
                    question.save()
                    for ans in answers:
                        ans.question = question
                        ans.save()
        except XMLSyntaxError as err:
            messages.error(request, message_syntax_error)

        if added_count:
            messages.success(request, message_added % added_count)
        if similar_count:
            messages.error(request, message_similar % similar_count)
        if repeated_count:
            messages.error(request, message_repeated % repeated_count)

        return redirect(reverse('admin:chm_xmlfile_changelist'))


class AnswerInline(admin.TabularInline):
    extra = 1
    model = Answer
    fields = ('is_correct', 'text',)


class QuestionAdmin(admin.ModelAdmin):
    model = Question
    inlines = (AnswerInline,)
    list_display = ['get_text', 'get_topic_name', 'get_subject_name']

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
    list_display = ['get_name', 'get_subject_name']

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
admin.site.register(XMLFile, XMLFileAdmin)
admin.site.register(Topic, TopicAdmin)
