from django import forms

from editor.models import Content

class PartialContentForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = ['section', 'body', 'formatting']
        # user to be populated from the authorized request
        # section to be populated from the GET request
        # created will be autogenerated
