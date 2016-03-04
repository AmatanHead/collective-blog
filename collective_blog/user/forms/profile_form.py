from django.contrib.auth import get_user_model
from django.forms import ModelForm, ValidationError
from django.utils.translation import ugettext_lazy as _

from ..models import Profile
from dj_markdown.widgets import CodeMirror
from appearance.forms import BaseFormRenderer


User = get_user_model()


class UserForm(ModelForm, BaseFormRenderer):
    renderer = [
        'email',
        ('first_name', 'last_name'),
    ]

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True

    def clean_email(self):
        """
        Validate that the supplied email address is unique for the
        site.

        """
        if User.objects.filter(email__iexact=self.cleaned_data['email']):
            raise ValidationError(_('This email is already used'))
        return self.cleaned_data['email']

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class ProfileForm(ModelForm, BaseFormRenderer):
    renderer = [
        ('location', 'birthday'),
        'about',
    ]

    class Meta:
        model = Profile
        fields = '__all__'
        widgets = {
            'about': CodeMirror(
                mode='gfm',
                addons=['mode/overlay'],
                theme='light',
                theme_path='dj_markdown/light.css',
                options={
                    'lineNumbers': True,
                    'matchBrackets': True,
                    'viewportMargin': float('inf'),
                },
                additional_modes=['markdown', 'python', 'javascript'],
                js_var_format='editor_%s'
            )
        }
