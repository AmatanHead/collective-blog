from django.contrib.auth import get_user_model
from django.forms import ModelForm
from s_appearance.widgets import LightSelect

from ..models import Blog
from s_markdown.widgets import CodeMirror
from s_appearance.forms import BaseFormRenderer


User = get_user_model()


class BlogForm(ModelForm, BaseFormRenderer):
    renderer = [
        'name',
        'icon',
        'about',
        '-----',
        'type',
        '-----',
        ('join_condition', 'join_karma_threshold'),
        '-----',
        'post_membership_required',
        ('post_condition', 'post_karma_threshold'),
        '-----',
        'comment_membership_required',
        ('comment_condition', 'comment_karma_threshold'),
    ]

    class Meta:
        model = Blog
        fields = [
            'name',
            'about',
            'icon',
            'type',
            'join_condition',
            'join_karma_threshold',
            'post_condition',
            'post_membership_required',
            'post_karma_threshold',
            'comment_condition',
            'comment_membership_required',
            'comment_karma_threshold',
        ]
        widgets = {
            'about': CodeMirror(
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
            'icon': LightSelect(),
            'type': LightSelect(),
            'join_condition': LightSelect(),
            'post_condition': LightSelect(),
            'comment_condition': LightSelect(),
        }
