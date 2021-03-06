from django.forms import ModelForm
from s_appearance.widgets import LightSelect

from ..models import Blog
from s_markdown.widgets import CodeMirror
from s_appearance.forms import BaseFormRenderer


class BlogFormCreate(ModelForm, BaseFormRenderer):
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
        'post_admin_required',
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
            'post_admin_required',
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


class BlogForm(BlogFormCreate):
    def __init__(self, *args, **kwargs):
        super(BlogFormCreate, self).__init__(*args, **kwargs)
        self.fields.pop('name')
        self.renderer = self.renderer[:]
        self.renderer.remove('name')
