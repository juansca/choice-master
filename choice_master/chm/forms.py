from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple

from chm.models import XMLFile
from chm.models import Topic


class XMLFileForm(forms.ModelForm):
    class Meta:
        model = XMLFile
        fields = ['file']


class QuizForm(forms.Form):
    """Provide form to configure quiz options"""
    RANDOM = 1
    HELP_IMPROVE = 2

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

    def make_quiz(self):
        """Make a quiz based on user input"""
        assert self.is_valid()
        return None
