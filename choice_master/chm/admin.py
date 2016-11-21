import json

from django.conf.urls import url
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.http import Http404
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from lxml.etree import XMLSyntaxError

from .forms import XMLFileForm
from .messages import LoadQuestionsMessageManager
from .models import Answer
from .models import Flag
from .models import FlaggedQuestion
from .models import Question
from .models import Subject
from .models import Topic
from .models import XMLFile
from .xml import XMLParser


class SimilarQuestionError(Exception):
    """When two questions are similar raise this error"""
    def __init__(self, msg, data):
        self.msg = msg
        self.data = data


class XMLFileAdmin(admin.ModelAdmin):
    """The representation of XMLFile model in the admin interface."""

    model = XMLFile
    change_form_template = 'change_XMLFile.html'

    def add_view(self, request, form_url='', extra_context=None):
        # Change the form_url of the in order to redirect after submit
        form_url = reverse('admin:chm_load_questions')
        return super(XMLFileAdmin, self).add_view(request, form_url)

    def get_urls(self):
        urls = [
            url('^loadquestions/$',
                self.admin_site.admin_view(self.load_questions_view),
                name='chm_load_questions'),
            url('^acceptsimilarquestion/$',
                self.admin_site.admin_view(self.accept_similar_question_view),
                name='chm_accept_similar_question'),
        ]
        return urls + super(XMLFileAdmin, self).get_urls()

    @staticmethod
    def load_question(data, mm, request, ignore_similar=False):
        """
        Parse the data, create all the instances of the corresponding models,
        validate them and then save them. Handle all the validation errors that
        might be raised in the validation process by using the given
        MessageManager
        :param data: The data to be parsed
        :param mm: A message manager to handle messages
        :param request: The request
        :param ignore_similar: load the questions regarless of the existence
                               of similar questions
        :type data: dict[string, T]
        :type mm: messages.LoadQuestionsMessageManager
        :type ignore_similar: bool
        """
        try:
            subject = Subject.objects.get(name=data['subject'])
            topic = Topic.objects.get(name=data['topic'], subject=subject)

            question = Question(text=data['question'], topic=topic)
            question.full_clean()
            answers = []
            for ans in data['answers']:
                answer = Answer()
                answer.text = ans['text']
                answer.is_correct = ans['is_correct']
                answers.append(answer)

            if question.similar_exists() and not ignore_similar:
                raise SimilarQuestionError(_("A similar question exists"),
                                           data)
            else:
                question.save()
                for answer in answers:
                    answer.question = question
                    answer.full_clean()
                    answer.save()
                mm.added.append(question)

        except Subject.DoesNotExist:
            mm.no_subject.append((data['subject'], data['question']))

        except Topic.DoesNotExist:
            mm.no_topic.append((data['topic'], data['question']))

        except ValidationError as err:
            mm.validation_error.append((err, data['question']))

        except SimilarQuestionError as err:
            request.session['duplicates'].append(err.data)

    def load_questions_view(self, request):
        """
        Parse and load the questions and answers from the specified file into
        the database. Handle any validation error showing the corresponding
        message.
        :param request: The request
        :return: The response
        """
        request.session['duplicates'] = []
        mm = LoadQuestionsMessageManager()
        try:
            form = XMLFileForm(request.POST, request.FILES)
            if form.is_valid():
                xmlfile = request.FILES['file']
                parser = XMLParser(xmlfile)
                for data in parser.parse_questions():
                    self.load_question(data, mm, request)
            else:
                mm.form_is_valid = False
                mm.set_messages(request)
                print(reverse('admin:chm_xmlfile_add'))
                return redirect(reverse('admin:chm_xmlfile_add'))

        except XMLSyntaxError as err:
            mm.syntax_error = err

        mm.set_messages(request)
        return redirect(reverse('admin:chm_question_changelist'))

    @csrf_exempt
    def accept_similar_question_view(self, request):
        """
        Save the given question in the POST request ignoring if a similar
        one exists
        :param request: The request
        :return: The response
        """
        if request.method == 'POST':
            data = json.loads(request.POST['data'])
            mm = LoadQuestionsMessageManager()
            self.load_question(data, mm, request, ignore_similar=True)
            return JsonResponse({'ok': True})
        else:
            raise Http404(_("Nothing to see here."))


class AnswerInline(admin.TabularInline):
    extra = 1
    model = Answer
    fields = ('is_correct', 'text',)


class QuestionAdmin(admin.ModelAdmin):
    model = Question
    inlines = (AnswerInline,)
    list_display = ['get_text', 'get_topic_name', 'get_subject_name']
    fields = ['topic', 'text']

    change_list_template = 'change_question_list.html'

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}

        extra_context['duplicates'] = request.session.pop('duplicates',
                                                          False)

        extra_context['dup_json'] = json.dumps(extra_context['duplicates'])

        return super(QuestionAdmin, self).changelist_view(
            request, extra_context=extra_context,
        )

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
        return Question.objects.filter(flags__isnull=False).distinct()

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
