from django.forms import ModelForm, HiddenInput

from ..models import Comment
from s_markdown.widgets import CodeMirror
from s_appearance.forms import BaseFormRenderer


class CommentForm(ModelForm, BaseFormRenderer):
    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['author'].required = False
        self.fields['post'].required = False
        self.fields['parent'].required = False

    def clean_author(self):
        return self.initial['author']

    def clean_post(self):
        return self.initial['post']

    class Meta:
        model = Comment
        fields = [
            'content',
            'author',
            'post',
            'parent',
        ]
        widgets = {
            'content': CodeMirror(
                mode='gfm',
                addons=['mode/overlay'],
                theme='light',
                theme_path='s_markdown/light.css',
                options={
                    'lineNumbers': True,
                    'matchBrackets': True,
                    'viewportMargin': float('inf'),
                },
                additional_modes=['markdown', 'python', 'javascript'],
                js_var_format='editor_%s'
            ),
            'author': HiddenInput(),
            'post': HiddenInput(),
            'parent': HiddenInput(),
        }
