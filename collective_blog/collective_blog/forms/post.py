from django.forms import ModelForm
from s_appearance.widgets import LightSelect

from ..models import Post
from s_markdown.widgets import CodeMirror
from s_appearance.forms import BaseFormRenderer


class PostForm(ModelForm, BaseFormRenderer):
    renderer = [
        'heading',
        'content',
        'blog',
        'is_draft',
    ]

    class Meta:
        model = Post
        fields = [
            'heading',
            'content',
            'blog',
            'is_draft',
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
            'blog': LightSelect(),
        }
