from django import forms
from chm.models import Topic
from chm.models import Subject


class XMLFileForm(forms.Form):
    subject = forms.ModelChoiceField(queryset=Subject.objects.all())
    topic = forms.ModelChoiceField(queryset=Topic.objects.all())
    XMLfile = forms.FileField(
        label='Seleccionar un archivo',
        widget=forms.FileInput({'accept': 'text/xml'})
    )
