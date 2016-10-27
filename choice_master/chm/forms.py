from django import forms
from chm.models import XMLFile


class XMLFileForm(forms.ModelForm):
    class Meta:
        model = XMLFile
        fields = ['file']
