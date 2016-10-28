from django.conf.urls import url
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.urls import reverse

from chm.forms import XMLFileForm
from chm.messages import LoadQuestionsMessageManager
from chm.models import Answer
from chm.models import Flag
from chm.models import FlaggedQuestion
from chm.models import Question
from chm.models import Subject
from chm.models import Topic
from chm.models import XMLFile

from chm.xml import XMLParser
from lxml.etree import XMLSyntaxError


class XMLFileAdmin(admin.ModelAdmin):
    """The representation of XMLFile model in the admin interface."""

    model = XMLFile
    change_form_template = 'change_XMLFile.html'

    def add_view(self, request, form_url='', extra_context=None):
        # Change the form_url of the in order to redirect after submit
        form_url = reverse('admin:chm_load_questions')
        return super(XMLFileAdmin, self).add_view(request, form_url)

    def get_urls(self):
        """
        Associate the url with name "admin:chm_load_questions" with the view
        "load_questions_view".
        """
        urls = [
            url('^loadquestions/$',
                self.admin_site.admin_view(self.load_questions_view),
                name='chm_load_questions'),
        ]
        return urls + super(XMLFileAdmin, self).get_urls()

    def load_question(self, request, data, mm):
        """
        Parse the data, create all the instances of the corresponding models,
        validate them and then save them. Handle all the validation errors that
        might be raised in the validation process by using the given
        MessageManager.
        """
        try:
            subject = Subject.objects.get(name=data['subject'])
            topic = Topic.objects.get(name=data['topic'], subject=subject)

            question = Question(text=data['question'], topic=topic)
            question.full_clean()
            question.save()

            for ans in data['answers']:
                answer = Answer()
                answer.question = question
                answer.text = ans['text']
                answer.is_correct = ans['is_correct']
                answer.full_clean()
                answer.save()
            mm.added.append(question)

        except Subject.DoesNotExist:
            mm.no_subject.append((data['subject'], data['question']))

        except Topic.DoesNotExist:
            mm.no_topic.append((data['topic'], data['question']))

        except ValidationError as err:
            mm.validation_error.append((err, data['question']))

    def load_questions_view(self, request):
        """
        Parse and load the questions and answers from the specified file into
        the database. Handle any validation error showing the corresponding
        message.
        """
        mm = LoadQuestionsMessageManager()
        try:
            form = XMLFileForm(request.POST, request.FILES)
            if form.is_valid():
                xmlfile = request.FILES['file']
                parser = XMLParser(xmlfile)
                for data in parser.parse_questions():
                    self.load_question(request, data, mm)
            else:
                mm.form_is_valid = False
                mm.set_messages(request)
                print(reverse('admin:chm_xmlfile_add'))
                return redirect(reverse('admin:chm_xmlfile_add'))

        except XMLSyntaxError as err:
            mm.syntax_error = err

        mm.set_messages(request)
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
    get_text.short_description = 'Question'

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
