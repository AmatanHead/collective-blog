from registration.forms import RegistrationFormUniqueEmail
from captcha.fields import ReCaptchaField

from django.contrib.auth.forms import AuthenticationForm as _AuthenticationForm
from django.contrib.auth.forms import PasswordResetForm as _PasswordResetForm
from django.contrib.auth.forms import PasswordChangeForm as _PasswordChangeForm

from collective_blog.forms import BaseFormRenderer


class AuthenticationForm(_AuthenticationForm, BaseFormRenderer):
    pass


class PasswordResetForm(_PasswordResetForm, BaseFormRenderer):
    pass


class PasswordChangeForm(_PasswordChangeForm, BaseFormRenderer):
    pass


class RegistrationFormCaptcha(RegistrationFormUniqueEmail, BaseFormRenderer):
    captcha = ReCaptchaField()
