# python import
import random

# django imports
from django import forms
from django.db.models import Case
from django.db.models import FloatField
from django.db.models import Q
from django.db.models import Sum
from django.db.models import Value
from django.db.models import When
from django.contrib.admin.widgets import FilteredSelectMultiple

# project imports
from chm.models import Question
from chm.models import QuestionOnQuiz
from chm.models import Quiz
from chm.models import Topic
from chm.models import XMLFile

NOT_ANSWERED = QuestionOnQuiz.STATUS.not_answered
WRONG = QuestionOnQuiz.STATUS.wrong
RIGHT = QuestionOnQuiz.STATUS.right


class XMLFileForm(forms.ModelForm):
    """Provide a form to upload the XML file"""
    class Meta:
        model = XMLFile
        fields = ['file']


class QuizForm(forms.Form):
    """Provide form to configure quiz options"""
    RANDOM = '1'
    MIN_DIFFICULTY = '2'
    HELP_IMPROVE = '3'

    SELECTION_ALGORITHMS = ((RANDOM, 'Random'),
                            (MIN_DIFFICULTY, 'Select minimum difficulty'),
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

    min_difficulty = forms.IntegerField(
        min_value=1,
        max_value=5,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
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
        """Add custom attribute to hold candidates questions"""
        self.candidates = None
        self.user = kwargs.pop('user', None)
        super(QuizForm, self).__init__(*args, **kwargs)

    def clean_topics(self):
        """Use the oportunity to populate `candidates` attribute"""
        self.candidates = Question.objects.filter(
            topic__in=self.cleaned_data['topics']
        )
        return self.cleaned_data['topics']

    def clean(self):
        """
        Make shure there are enough questions on the DDBB to satisfy
        user configuration
        """
        cleaned_data = super(QuizForm, self).clean()
        assert self.candidates is not None
        if self.cleaned_data['selection_algorithm'] == self.MIN_DIFFICULTY:
            self.candidates = self.candidates.filter(
                difficulty__gte=cleaned_data['min_difficulty']
            )
        if self.candidates.count() < cleaned_data['nr_of_questions']:
            msg = ('{} questions meet the current criteria. '
                   'You can try choosing fewer questions or more '
                   'topics.'.format(len(self.candidates)))
            if cleaned_data['selection_algorithm'] == self.MIN_DIFFICULTY:
                if cleaned_data['min_difficulty'] > 1:
                    msg += (' You could also try with a'
                            ' lower minimum difficulty.')
                else:
                    msg += (' You could also try with a'
                            ' different selection algorithm.')
            raise forms.ValidationError(msg)
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
        """
        Chose questions based on topics and selection method
        :return: The selected questions
        :rtype: list[Question]
        """
        assert self.is_valid()
        selection_algorithm = self.cleaned_data['selection_algorithm']

        if selection_algorithm in [QuizForm.RANDOM, QuizForm.MIN_DIFFICULTY]:
            candidates = list(self.candidates)
            random.shuffle(candidates)
        elif selection_algorithm == QuizForm.HELP_IMPROVE:
            # order by amount of previous errors
            candidates = self.candidates.annotate(

                # we'll add column with some 'score' to order the questions
                score=Sum(
                    Case(

                        # how many times did the user leave the question blank?
                        When(Q(questiononquiz__quiz__user=self.user) &
                             Q(questiononquiz__state=NOT_ANSWERED),
                             then=1),

                        # how many times did the user hit the correct answer?
                        When(Q(questiononquiz__quiz__user=self.user) &
                             Q(questiononquiz__state=RIGHT),
                             then=-1),

                        # how many times did the user provide a wrong answer?
                        When(Q(questiononquiz__quiz__user=self.user) &
                             Q(questiononquiz__state=WRONG),
                             then=2),

                        # may be the user never saw the question
                        default=Value(0),
                        output_field=FloatField(),
                    )
                )
            ).order_by('score')
            candidates = list(candidates)
        else:
            assert False
        return candidates[:self.cleaned_data['nr_of_questions']]


class FlagForm(forms.Form):
    """Form used to flag a question"""
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control'})
    )
