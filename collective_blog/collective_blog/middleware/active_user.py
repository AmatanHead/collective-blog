"""Middleware that prevents inactive user from login

Logs out all inactive users as they request anything.
Taken from http://stackoverflow.com/a/7871831/3993308

"""

from django.contrib.auth import logout


class ActiveUserMiddleware(object):
    @staticmethod
    def process_request(request):
        if not request.user.is_authenticated():
            return
        if not request.user.is_active:
            logout(request)
