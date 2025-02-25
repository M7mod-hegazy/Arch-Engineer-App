from django import forms
from .models import Subject, Image

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['customer', 'price', 'comment', 'date_limit']

class ImageForm(forms.ModelForm):
    done = forms.BooleanField(required=False)
    class Meta:
        model = Image
        fields = ['image']
