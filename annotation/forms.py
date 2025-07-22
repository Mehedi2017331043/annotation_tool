from django import forms
from .models import Project, Document, Label


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description']

class DocumentImportForm(forms.Form):
    file = forms.FileField()
    
class LabelForm(forms.ModelForm):
    class Meta:
        model = Label
        fields = ['text', 'color']