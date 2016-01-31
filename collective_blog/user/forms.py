from registration.forms import RegistrationFormUniqueEmail
from captcha.fields import ReCaptchaField

class RegistrationFormCaptcha(RegistrationFormUniqueEmail):
    captcha = ReCaptchaField()
