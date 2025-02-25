from django import forms
from django.utils.html import format_html

class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True

    def render(self, name, value, attrs=None, renderer=None):
        attrs['multiple'] = 'multiple'
        return super().render(name, value, attrs)

    def value_from_datadict(self, data, files, name):
        if hasattr(files, 'getlist'):
            return files.getlist(name)
        else:
            return []
