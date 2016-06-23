from django.db.models import Q
from django.forms import ModelForm, HiddenInput, ModelChoiceField

from ..models import Post, Blog
from s_markdown.widgets import CodeMirror
from s_appearance.forms import BaseFormRenderer
from s_appearance.widgets import LightSelect


class PostForm(ModelForm, BaseFormRenderer):
    def __init__(self, **kwargs):
        super(PostForm, self).__init__(**kwargs)
        choices = (
            Blog.objects.filter(
                (Q(type='O') & Q(post_membership_required=False) & Q(post_admin_required=False)) |
                (Q(post_admin_required=False) & Q(members=self.initial['author']) & Q(membership__role__in=['A', 'O', 'M'])) |
                (Q(post_admin_required=True) & Q(members=self.initial['author']) & Q(membership__role__in=['A', 'O']))
            ).distinct()
        )
        self.fields['blog'].queryset = choices

    renderer = [
        'heading',
        'content',
        'blog',
        'is_draft',
    ]

    def clean_author(self):
        return self.initial['author']

    class Meta:
        model = Post
        fields = [
            'heading',
            'content',
            'blog',
            'is_draft',
            'author',
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
            'author': HiddenInput(),
            'created': HiddenInput(),
        }


class PostCreateForm(PostForm):
    def __init__(self, created, **kwargs):
        self._created = created
        super(PostCreateForm, self).__init__(**kwargs)

        if self._created:
            self.fields['blog'].widget.attrs['disabled'] = 'disabled'

    def clean_blog(self):
        if self._created:
            return self.initial['blog']
        else:
            return self.cleaned_data['blog']
