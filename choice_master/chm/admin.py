from django.contrib import admin
from django.shortcuts import redirect
from django.conf.urls import url
from django.urls import reverse

from chm.models import Answer
from chm.models import Flag
from chm.models import FlaggedQuestion
from chm.models import Question
from chm.models import Subject
from chm.models import Topic
from chm.models import XMLFile
from chm.forms import XMLFileForm
from chm.messages import LoadQuestionsMessageManager

from chm.xml import parse_questions
from lxml.etree import XMLSyntaxError


class XMLFileAdmin(admin.ModelAdmin):
    model = XMLFile
    change_form_template = 'change_XMLFile.html'

    def add_view(self, request, form_url='', extra_context=None):
        form_url = reverse('admin:chm_load_questions')
        return super(XMLFileAdmin, self).add_view(request, form_url)

    def get_urls(self):
        urls = [
            url('^loadquestions/$',
                self.admin_site.admin_view(self.load_questions_view),
                name='chm_load_questions'),
        ]
        return urls + super(XMLFileAdmin, self).get_urls()

    def load_question(self, mm, topic_name, subject_name, question, answers):
        try:
            subject = Subject.objects.get(name=subject_name)
            topic = Topic.objects.get(name=topic_name, subject=subject)
            question.topic = topic

            if question.is_repeated():
                mm.repeated.append(question)

            elif question.similar_exists():
                mm.similar.append(question)

            else:
                mm.added.append(question)
                question.save()
                for ans in answers:
                    ans.question = question
                    ans.save()

        except Subject.DoesNotExist:
            mm.non_existent_subjects.append((subject_name, question))

        except Topic.DoesNotExist:
            mm.non_existent_topics.append((topic_name, question))

    def load_questions_view(self, request):
        mm = LoadQuestionsMessageManager()

        form = XMLFileForm(request.POST, request.FILES)
        mm.form_is_valid = form.is_valid()

        if mm.form_is_valid:
            xmlfile = request.FILES['file']
            try:
                for parsed_question in parse_questions(xmlfile):
                    self.load_question(mm, *parsed_question)

            except XMLSyntaxError as err:
                mm.syntax_error = err

        mm.set_messages(request)

        if not mm.form_is_valid:
            return redirect(reverse('admin:chm_xmlfile_add'))

        return redirect(reverse('admin:chm_question_changelist'))


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
    get_topic_name.short_description = 'Topic'

    def get_subject_name(self, obj):
        return obj.topic.subject.name
    get_subject_name.short_description = 'Subject'


class TopicAdmin(admin.ModelAdmin):
    model = Topic
    list_display = ['get_name', 'get_subject_name']

    def get_name(self, obj):
        return obj.name
    get_name.short_description = 'Topic'

    def get_subject_name(self, obj):
        return obj.subject.name
    get_subject_name.admin_order_field = 'subject'
    get_subject_name.short_description = 'Subject'


class FlaggedQuestionAdmin(admin.ModelAdmin):

    list_display = ('text', 'flags_count')
    fields = ('text',)
    inlines = (AnswerInline,)

    change_form_template = 'change_flagged_question.html'

    def flags_count(self, request):
        return Question.objects.filter(flags__isnull=False).count()
    flags_count.short_description = 'Number of complains'

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
