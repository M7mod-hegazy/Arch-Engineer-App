from django import forms
from .models import Subject
import datetime

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['customer', 'price', 'comment', 'date_limit']
        widgets = {
            'customer': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'date_limit': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control'
                }
            ),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4
            }),
        }
