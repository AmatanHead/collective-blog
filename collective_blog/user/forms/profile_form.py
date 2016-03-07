from django.contrib.auth import get_user_model
from django.forms import ModelForm, ValidationError
from django.utils.translation import ugettext_lazy as _

from ..models import Profile
from s_markdown.widgets import CodeMirror
from s_appearance.forms import BaseFormRenderer


User = get_user_model()


class UserForm(ModelForm, BaseFormRenderer):
    required_css_class = 'required'

    renderer = [
        'email',
        ('first_name', 'last_name'),
    ]

    def __init__(self, *args, **kwargs):
        """User editing form

        Usually works with `ProfileForm`
        (e.g. both forms are placed into the same `<form>` tag).

        """
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True

    def clean_email(self):
        """Validate that the supplied email address is unique for the site"""
        email_match = User.objects.filter(email__iexact=self.cleaned_data['email']).first()
        if email_match and email_match.pk != self.instance.pk:
            raise ValidationError(_('This email is already used'))
        return self.cleaned_data['email']

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class ProfileForm(ModelForm, BaseFormRenderer):
    """Profile editing form

    Usually works with `UserForm`
    (e.g. both forms are placed into the same `<form>` tag).

    """
    required_css_class = 'required'

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
                theme_path='s_markdown/light.css',
                options={
                    'lineNumbers': True,
                    'matchBrackets': True,
                    'viewportMargin': float('inf'),
                },
                additional_modes=['markdown', 'python', 'javascript'],
                js_var_format='editor_%s'
            )
        }
