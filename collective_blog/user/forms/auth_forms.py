"""
Forms that are used in built-in authentication and registration views.

For most of that forms we just mixin renderer.

"""

from registration.forms import RegistrationFormUniqueEmail
from captcha.fields import ReCaptchaField

from django.contrib.auth.forms import AuthenticationForm as _AuthenticationForm
from django.contrib.auth.forms import PasswordResetForm as _PasswordResetForm
from django.contrib.auth.forms import PasswordChangeForm as _PasswordChangeForm

from appearance.forms import BaseFormRenderer
from collective_blog.settings import DEBUG


class AuthenticationForm(_AuthenticationForm, BaseFormRenderer):
    pass


class PasswordResetForm(_PasswordResetForm, BaseFormRenderer):
    pass


class PasswordChangeForm(_PasswordChangeForm, BaseFormRenderer):
    pass


class RegistrationFormCaptcha(RegistrationFormUniqueEmail, BaseFormRenderer):
    if DEBUG:
        def __init__(self, *args, **kwargs):
            if 'data' in kwargs:
                kwargs['data'] = kwargs['data'].copy()
            else:
                kwargs['data'] = {}
            kwargs['data']['g-recaptcha-response'] = 'PASSED'
            print(kwargs['data'])
            super().__init__(*args, **kwargs)
        captcha = ReCaptchaField(help_text='This ReCaptcha is running '
                                           'with DEBUG=True.')
    else:
        captcha = ReCaptchaField()
