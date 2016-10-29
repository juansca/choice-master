"""
Forms for app chm
"""

# python import
import random

# django imports
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple

# project imports
from chm.models import Question
from chm.models import QuestionOnQuiz
from chm.models import Quiz
from chm.models import Topic
from chm.models import XMLFile


class XMLFileForm(forms.ModelForm):
    class Meta:
        model = XMLFile
        fields = ['file']


class QuizForm(forms.Form):
    """Provide form to configure quiz options"""
    RANDOM = '1'
    HELP_IMPROVE = '2'

    SELECTION_ALGORITHMS = ((RANDOM, 'Random'),
                            (HELP_IMPROVE, 'Based on previows errors'))

    topics = forms.ModelMultipleChoiceField(
        queryset=Topic.objects.all(),
        widget=FilteredSelectMultiple('Topics', is_stacked=False)
    )

    nr_of_questions = forms.IntegerField(
        min_value=1,
        initial=4,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
    )
    seconds_per_question = forms.IntegerField(
        min_value=10,
        initial=10,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
    )
    selection_algorithm = forms.ChoiceField(
        choices=SELECTION_ALGORITHMS,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    class Media:
        # jsi18n is required by the widget
        js = ('/admin/jsi18n/',)
        css = {'all': ('/static/admin/css/widgets.css',)}

    def __init__(self, *args, **kwargs):
        """ Add custom attribute to hold candidates questions"""
        self.candidates = None
        self.user = kwargs.pop('user', None)
        super(QuizForm, self).__init__(*args, **kwargs)

    def clean_topics(self):
        """ Use the oportunity to populate `candidates` attribute"""
        self.candidates = Question.objects.filter(
            topic__in=self.cleaned_data['topics']
        )
        return self.cleaned_data['topics']

    def clean(self):
        """ Make shure there are enough questions
        on the DDBB to satisfy user configuration"""
        cleaned_data = super(QuizForm, self).clean()
        if self.candidates is not None:
            if self.candidates.count() < cleaned_data['nr_of_questions']:
                msg = ('There are {} questions for the chosen topics. '
                       'Please choose fewer questions or '
                       'provide more topics.'.format(len(self.candidates)))
                raise forms.ValidationError(msg)
        if cleaned_data['selection_algorithm'] == self.HELP_IMPROVE:
            msg = ('Selection based on previous errors is not implemented yet')
            self.add_error(None, msg)
        return cleaned_data

    def make_quiz(self):
        """Make a quiz based on user input"""
        assert self.is_valid()
        quiz = Quiz.objects.create(
            user=self.user,
            nr_of_questions=self.cleaned_data['nr_of_questions'],
            seconds_per_question=self.cleaned_data['seconds_per_question'],
        )
        for topic in self.cleaned_data['topics']:
            quiz.topics.add(topic)

        # add questions to the quiz
        for question in self.choose_questions():
            QuestionOnQuiz.objects.create(question=question, quiz=quiz)

        return quiz

    def choose_questions(self):
        """ Chose questions based on topics and selection method"""
        assert self.is_valid()
        candidates = list(Question.objects.filter(
            topic__in=self.cleaned_data['topics']
        ))
        random.shuffle(candidates)
        return candidates[:self.cleaned_data['nr_of_questions']]
