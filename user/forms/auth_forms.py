"""Forms that are used in built-in authentication and registration views

For most of that forms we just mixin renderer.

"""
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from registration.forms import RegistrationFormUniqueEmail
from captcha.fields import ReCaptchaField
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.forms import AuthenticationForm as _AuthenticationForm
from django.contrib.auth.forms import PasswordResetForm as _PasswordResetForm
from django.contrib.auth.forms import PasswordChangeForm as _PasswordChangeForm
from django.contrib.auth.forms import SetPasswordForm as _SetPasswordForm

from s_appearance.forms import BaseFormRenderer
from collective_blog.settings import DEBUG

User = get_user_model()


class AuthenticationForm(_AuthenticationForm, BaseFormRenderer):
    required_css_class = ''


class PasswordResetForm(_PasswordResetForm, BaseFormRenderer):
    required_css_class = ''


class PasswordChangeForm(_PasswordChangeForm, BaseFormRenderer):
    required_css_class = ''


class RegistrationFormCaptcha(RegistrationFormUniqueEmail, BaseFormRenderer):
    required_css_class = ''

    if DEBUG:
        def __init__(self, *args, **kwargs):
            if 'data' in kwargs:
                kwargs['data'] = kwargs['data'].copy()
                if kwargs['data'].get('g-recaptcha-response', None):
                    kwargs['data']['g-recaptcha-response'] = 'PASSED'
            super(RegistrationFormCaptcha, self).__init__(*args, **kwargs)
        captcha = ReCaptchaField(help_text='This ReCaptcha is running '
                                           'with DEBUG=True.')
    else:
        captcha = ReCaptchaField()

    def clean_username(self):
        if User.objects.filter(username__iexact=self.cleaned_data['username']).count():
            raise ValidationError(_('A user with that username already exists.'))
        return self.cleaned_data['username']


class SetPasswordForm(_SetPasswordForm, BaseFormRenderer):
    required_css_class = ''
