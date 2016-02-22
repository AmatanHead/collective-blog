from registration.forms import RegistrationFormUniqueEmail
from captcha.fields import ReCaptchaField

from django.contrib.auth.forms import AuthenticationForm as _AuthenticationForm

from collective_blog.forms import BaseFormRenderer

class AuthenticationForm(_AuthenticationForm, BaseFormRenderer):
    pass

class RegistrationFormCaptcha(RegistrationFormUniqueEmail):
    captcha = ReCaptchaField()
