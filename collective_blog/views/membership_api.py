from datetime import timedelta
from django.contrib import messages
from messages_extends import constants as constants_messages
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_protect
from django.views.generic import View

from collective_blog.models import Blog, Membership

import json


@method_decorator(csrf_protect, 'dispatch')
class MembershipApi(View):
    def dispatch(self, request, *args, **kwargs):
        self.blog_slug = kwargs.pop('blog_slug')

        self.blog = get_object_or_404(Blog.objects,
                                      slug=self.blog_slug)
        self.self_membership = self.blog.check_membership(self.request.user)

        return super(MembershipApi, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponse('This page is ajax-only', status=418)

        try:
            data = json.loads(request.POST['data'])
        except (KeyError, ValueError):
            return HttpResponse('Wrong data', status=400)

        if 'username' not in data or not isinstance(data['username'], str):
            return HttpResponse('Wrong data', status=400)
        self.membership = Membership.objects.filter(blog=self.blog, user__username=data['username']).first()

        if 'type' not in data or data['type'] not in ['fetch', 'accept', 'refuse', 'ban', 'unban', 'manage']:
            return HttpResponse('Wrong data', status=400)

        if data['type'] == 'fetch':
            return self.fetch(data)
        elif data['type'] == 'accept':
            return self.accept()
        elif data['type'] == 'refuse':
            return self.refuse()
        elif data['type'] == 'ban':
            return self.ban(data)
        elif data['type'] == 'unban':
            return self.unban(data)
        elif data['type'] == 'manage':
            return self.manage(data)

    def fetch(self, data):
        if 'username' not in data or not isinstance(data['username'], str):
            return HttpResponse('Wrong data', status=400)
        return self.response()

    def accept(self):
        if not self.accept_perm():
            return HttpResponse(_('You can\'t perform this action'), status=400)

        if self.membership is not None and self.membership.role == 'W':
            self.membership.role = 'M'
            self.membership.color = 'gray'
            self.membership.save()
            messages.add_message(
                self.request,
                constants_messages.INFO_PERSISTENT,
                _('Your request to join the "%(blog)s" blog was accepted.') % {
                    'blog': self.membership.blog.name
                },
                user=self.membership.user)
        return self.response('accept')

    def refuse(self):
        if not self.accept_perm():
            return HttpResponse(_('You can\'t perform this action'), status=400)

        if self.membership is not None and self.membership.role == 'W':
            self.membership.role = 'L'
            self.membership.color = 'gray'
            self.membership.save()
            messages.add_message(
                self.request,
                constants_messages.INFO_PERSISTENT,
                _('Your request to join the "%(blog)s" blog was declined.') % {
                    'blog': self.membership.blog.name
                },
                user=self.membership.user)
        return self.response('refuse')

    def ban(self, data):
        if self.membership is None or not self.ban_perm():
            return HttpResponse(_('You can\'t perform this action'), status=400)

        time = {
            '5m': timedelta(minutes=5),
            '30m': timedelta(minutes=30),
            '1h': timedelta(minutes=60),
            '1d': timedelta(days=1),
            '1w': timedelta(days=7),
            'forever': None,
        }

        if 'time' not in data or data['time'] not in time:
            return HttpResponse('Wrong data', status=400)

        self.membership.ban(time=time[data['time']])

        return self.response('ban')

    def unban(self, data):
        if self.membership is None or not self.ban_perm():
            return HttpResponse(_('You can\'t perform this action'), status=400)

        self.membership.unban()

        return self.response('unban')

    def manage(self, data):
        if self.membership is None or not self.manage_perm():
            return HttpResponse(_('You can\'t perform this action'), status=400)

        if ('can_change_settings' not in data or
                'can_delete_posts' not in data or
                'can_delete_comments' not in data or
                'can_ban' not in data or
                'can_accept_new_users' not in data or
                'can_manage_permissions' not in data):
            return HttpResponse('Wrong data', status=400)

        if self.membership.role in ['M', 'A']:
            self.membership.can_change_settings_flag = data['can_change_settings']
            self.membership.can_delete_posts_flag = data['can_delete_posts']
            self.membership.can_delete_comments_flag = data['can_delete_comments']
            self.membership.can_ban_flag = data['can_ban']
            self.membership.can_accept_new_users_flag = data['can_accept_new_users']
            self.membership.can_manage_permissions_flag = data['can_manage_permissions']
        if any([data['can_change_settings'],
                data['can_delete_posts'],
                data['can_delete_comments'],
                data['can_ban'],
                data['can_accept_new_users'],
                data['can_manage_permissions']]):
            if self.membership.role == 'M':
                self.membership.role = 'A'
            self.membership.save()
        elif self.membership.role == 'A':
            self.membership.role = 'M'
            self.membership.save()

        return self.response('manage')

    def ban_perm(self):
        return (
            (self.self_membership.role == "O" and self.membership.role not in ["O", "A"]) or (
                self.self_membership.can_ban() and
                self.membership.role in ["M", "B", "LB"])
        ) if self.membership is not None and self.self_membership is not None else False

    def accept_perm(self):
        return (
            self.self_membership.can_accept_new_users() and
            self.membership.role == "W"
        ) if self.membership is not None and self.self_membership is not None else False

    def manage_perm(self):
        return (
            (self.self_membership.role == "O" and self.membership.role != "O") or (
                self.self_membership.can_manage_permissions() and
                self.membership.role in ["M", "A"]) and
            not self.membership.is_banned() and
            self.self_membership.user != self.membership.user
        ) if self.membership is not None and self.self_membership is not None else False

    def caption(self):
        caption = ''
        if self.membership is None or self.membership.is_left():
            caption += _('Not a member of this blog;') + ' '
        if self.membership is None or self.membership.role == 'A':
            caption += _('Admin;') + ' '
        if self.membership is None or self.membership.role == 'O':
            caption += _('Owner;') + ' '
        if self.membership is not None and self.membership.is_banned():
            caption += _('Banned;') + ' '
            if not self.membership.ban_is_permanent():
                caption += _("Ban expires %(expires)s.") % {
                    'expires': naturaltime(self.membership.ban_expiration)
                } + ' '
        return caption

    def response(self, success=''):
        return HttpResponse(json.dumps({
            'ban_perm': self.ban_perm(),
            'accept_perm': self.accept_perm(),
            'manage_perm': self.manage_perm(),
            'caption': self.caption(),
            'success': success,
            'banned': self.membership.is_banned() if self.membership is not None else False,
            'role': self.membership.role if self.membership is not None else '',
            'can_change_settings': (self.membership.can_change_settings_flag and self.membership.role in ['A', 'O']) if self.membership is not None else False,
            'can_delete_posts': (self.membership.can_delete_posts_flag and self.membership.role in ['A', 'O']) if self.membership is not None else False,
            'can_delete_comments': (self.membership.can_delete_comments_flag and self.membership.role in ['A', 'O']) if self.membership is not None else False,
            'can_ban': (self.membership.can_ban_flag and self.membership.role in ['A', 'O']) if self.membership is not None else False,
            'can_accept_new_users': (self.membership.can_accept_new_users_flag and self.membership.role in ['A', 'O']) if self.membership is not None else False,
            'can_manage_permissions': (self.membership.can_manage_permissions_flag and self.membership.role in ['A', 'O']) if self.membership is not None else False,
        }))
