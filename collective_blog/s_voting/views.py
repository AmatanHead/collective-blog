"""Abstract class-based views"""
import json

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.generic import View
from django.utils.translation import ugettext as __

from collective_blog.utils.errors import PermissionCheckFailed

User = get_user_model()


@method_decorator(csrf_protect, 'dispatch')
class VoteView(View):
    # A model through which the votes counted (derived from the `AbstractVote`)
    model = None

    # An object that is being voted (set this up in the `get_object` method)
    object = None

    # A method that will be used to serialize the response data
    serialize = staticmethod(json.dumps)

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object(*args, **kwargs)
        return super(VoteView, self).dispatch(request, *args, **kwargs)

    def get_object(self, *args, **kwargs):
        raise NotImplementedError()

    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponse('This page is ajax-only', status=418)
        try:
            try:
                vote = int(request.GET['vote'])
                assert vote in [-1, 0, 1]
            except (ValueError, AssertionError, KeyError):
                raise PermissionCheckFailed(__('Wrong vote'))

            self.model.vote_for(request.user, self.object, vote)
            data = self.model.objects.filter(object=self.object).score_query()
            data['state'] = vote
            return HttpResponse(self.serialize(data))
        except PermissionCheckFailed as e:
            return HttpResponse(e.note, status=400)
