from django import forms
from .models import XMLFile


class XMLFileForm(forms.ModelForm):
    class Meta:
        model = XMLFile
        fields = ['file']
