from django.db import models
from django.utils.translation import ugettext_lazy as _

from datetime import datetime

from collective_blog import settings

from user.models import Karma

from dj_markdown.models import MarkdownField, HtmlCacheField
from dj_markdown.datatype import Markdown
from dj_markdown.renderer import BaseRenderer
from dj_markdown.extensions import (FencedCodeExtension,
                                    EscapeHtmlExtension,
                                    SemiSaneListExtension,
                                    StrikethroughExtension,
                                    AutomailExtension,
                                    AutolinkExtension,
                                    CommentExtension)


class CantJoinException(Exception):
    pass


class Blog(models.Model):
    name = models.CharField(max_length=100,
                            verbose_name=_('Name'),
                            unique=True)
    slug = models.SlugField(max_length=100,
                            verbose_name=_("Blog's url"),
                            unique=True)

    about = MarkdownField(blank=True,
                          markdown=Markdown,
                          renderer=BaseRenderer(
                              extensions=[
                                  'markdown.extensions.smarty',
                                  'markdown.extensions.abbr',
                                  'markdown.extensions.def_list',
                                  'markdown.extensions.tables',
                                  'markdown.extensions.smart_strong',
                                  FencedCodeExtension(),
                                  EscapeHtmlExtension(),
                                  SemiSaneListExtension(),
                                  StrikethroughExtension(),
                                  AutolinkExtension(),
                                  AutomailExtension(),
                                  CommentExtension(),
                              ]
                          ),
                          verbose_name=_('About this blog'))

    _about_html = HtmlCacheField(about)

    ICONS = (
        ('aircraft', _('aircraft')),
        ('aircraft-take-off', _('aircraft take off')),
        ('aircraft-landing', _('aircraft landing')),
        ('area-graph', _('area graph')),
        ('archive', _('archive')),
        ('attachment', _('attachment')),
        ('awareness-ribbon', _('awareness ribbon')),
        ('back-in-time', _('back in time')),
        ('bar-graph', _('bar graph')),
        ('beamed-note', _('beamed note')),
        ('bell', _('bell')),
        ('blackboard', _('blackboard')),
        ('book', _('book')),
        ('bowl', _('bowl')),
        ('bookmarks', _('bookmarks')),
        ('box', _('box')),
        ('briefcase', _('briefcase')),
        ('brush', _('brush')),
        ('bucket', _('bucket')),
        ('bug', _('bug')),
        ('cake', _('cake')),
        ('camera', _('camera')),
        ('chat', _('chat')),
        ('clapperboard', _('clapperboard')),
        ('classic-computer', _('classic computer')),
        ('clipboard', _('clipboard')),
        ('cloud', _('cloud')),
        ('code', _('code')),
        ('cog', _('cog')),
        ('colours', _('colours')),
        ('compass', _('compass')),
        ('database', _('database')),
        ('dial-pad', _('dial pad')),
        ('documents', _('documents')),
        ('feather', _('feather')),
        ('flag', _('flag')),
        ('flash', _('flash')),
        ('flashlight', _('flashlight')),
        ('flat-brush', _('flat brush')),
        ('flow-branch', _('flow branch')),
        ('flower', _('flower')),
        ('folder', _('folder')),
        ('info-with-circle', _('info with circle')),
        ('infinity', _('infinity')),
        ('image', _('image')),
        ('hand', _('hand')),
        ('hair-cross', _('hair cross')),
        ('grid', _('grid')),
        ('graduation-cap', _('graduation cap')),
        ('globe', _('globe')),
        ('lab-flask', _('lab flask')),
        ('landline', _('landline')),
        ('keyboard', _('keyboard')),
        ('key', _('key')),
        ('layers', _('layers')),
        ('laptop', _('laptop')),
        ('leaf', _('leaf')),
        ('lifebuoy', _('lifebuoy')),
        ('light-bulb', _('light bulb')),
        ('light-up', _('light up')),
        ('line-graph', _('line graph')),
        ('location-pin', _('location pin')),
        ('modern-mic', _('modern mic')),
        ('moon', _('moon')),
        ('mic', _('mic')),
        ('medal', _('medal')),
        ('mail', _('mail')),
        ('magnet', _('magnet')),
        ('mouse-pointer', _('mouse pointer')),
        ('mouse', _('mouse')),
        ('network', _('network')),
        ('palette', _('palette')),
        ('new-message', _('new message')),
        ('new', _('new')),
        ('newsletter', _('newsletter')),
        ('note', _('note')),
        ('paper-plane', _('paper plane')),
        ('phone', _('phone')),
        ('rocket', _('rocket')),
        ('radio', _('radio')),
        ('print', _('print')),
        ('price-tag', _('price tag')),
        ('shop', _('shop')),
        ('suitcase', _('suitcase')),
        ('tablet-mobile-combo', _('tablet mobile combo')),
        ('thunder-cloud', _('thunder cloud')),
        ('ticket', _('ticket')),
        ('time-slot', _('time slot')),
        ('tools', _('tools')),
        ('traffic-cone', _('traffic cone')),
        ('tree', _('tree')),
        ('tv', _('tv')),
        ('video-camera', _('video camera')),
        ('video', _('video')),
        ('vinyl', _('vinyl')),
        ('voicemail', _('voicemail')),
        ('wallet', _('wallet')),
        ('warning', _('warning')),
        ('water', _('water')),
    )

    icon = models.CharField(max_length=100, blank=True, choices=ICONS)

    TYPES = (
        ('O', _('Open')),
        ('P', _('Private')),
    )

    type = models.CharField(max_length=2, default='0', choices=TYPES,
                            verbose_name=_('Type of the blog'))

    JOIN_CONDITIONS = (
        ('A', _('Anyone can join')),
        ('K', _('Only users with high karma can join')),
        ('I', _('Manual approval required'))
    )

    join_condition = models.CharField(max_length=2, default='A',
                                      choices=JOIN_CONDITIONS,
                                      verbose_name=_('Who can join the blog'))

    join_karma_threshold = models.SmallIntegerField(default=0,
                                                    verbose_name=_(
                                                        'Join karma threshold'))

    POST_CONDITIONS = (
        ('A', _('Anyone can add post')),
        ('K', _('Only users with high karma can add post')),
    )

    post_condition = models.CharField(max_length=2, default='A',
                                      choices=POST_CONDITIONS,
                                      verbose_name=_('Who can add posts'))

    post_membership_required = models.BooleanField(
        default=False, verbose_name=_('Require membership to write posts'))

    post_karma_threshold = models.SmallIntegerField(
        default=0, verbose_name=_('Post karma threshold'))

    COMMENT_CONDITIONS = (
        ('A', _('Anyone can comment')),
        ('K', _('Only users with high karma can comment')),
    )

    comment_condition = models.CharField(max_length=2, default='A',
                                         choices=COMMENT_CONDITIONS,
                                         verbose_name=_(
                                             'Who can comment in the blog'))

    comment_membership_required = models.BooleanField(
        default=False, verbose_name=_('Require membership to write comments'))

    comment_karma_threshold = models.SmallIntegerField(
        default=0, verbose_name=_('Comment karma threshold'))

    members = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                     through='Membership',
                                     editable=False)

    def check_membership(self, user):
        return Membership.objects.filter(blog=self, user=user).first()

    def is_banned(self, membership):
        if membership is not None:
            return membership.is_banned()
        else:
            return False

    def check_can_change_settings(self, membership):
        if membership is not None:
            return membership.can_change_settings()
        else:
            return False

    def check_can_edit_posts(self, membership):
        if membership is not None:
            return membership.can_edit_posts()
        else:
            return False

    def check_can_delete_posts(self, membership):
        if membership is not None:
            return membership.can_delete_posts()
        else:
            return False

    def check_can_edit_comments(self, membership):
        if membership is not None:
            return membership.can_edit_comments()
        else:
            return False

    def check_can_delete_comments(self, membership):
        if membership is not None:
            return membership.can_delete_comments()
        else:
            return False

    def check_can_ban(self, membership):
        if membership is not None:
            return membership.can_ban()
        else:
            return False

    def check_can_join(self, user):
        """Checks if the user can join the blog

        Note that joining process should go through the special method.
        Makes database queries: `check_membership` and karma calculation.

        """
        if not user.is_active or user.is_anonymous():
            return False

        membership = self.check_membership(user)

        if membership is not None:
            return False  # Already joined

        if self.join_condition == 'A':
            return True
        elif self.join_condition == 'K':
            return (Karma.objects.filter(object=user).score()['score'] >=
                    self.join_karma_threshold)
        elif self.join_condition == 'I':
            return True  # Can send a request
        else:
            return False

    def join(self, user):
        """Add the user to the blog's membership

        :param user: User which wants to be a member.
        :return: Message
        :raises CantJoinException: If the user can't join the blog.

        """
        if self.check_can_join(user):
            if self.join_condition == 'I':
                Membership.objects.create(user=user, blog=self, role='W')
                return _("A request has been sent"), 1
            else:
                Membership.objects.create(user=user, blog=self, role='M')
                return _("Success"), 1
        else:
            raise CantJoinException(_("You can't join this blog"))

    def approve(self, membership, new_role='M', save=True):
        if membership.role == 'W':
            membership.role = new_role
            if save:
                membership.save()

    class Meta:
        verbose_name = _("Blog")
        verbose_name_plural = _("Blogs")
        ordering = ("name",)

    def __str__(self):
        return str(self.name)


class Membership(models.Model):
    """Members of blogs"""

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             models.CASCADE)
    blog = models.ForeignKey(Blog,
                             models.CASCADE)

    ROLES = (
        ('O', _('Owner')),
        ('M', _('Member')),
        ('B', _('Banned')),
        ('A', _('Administrator')),
        ('W', _('Waiting for approval'))
    )

    ban_expiration = models.DateTimeField(auto_now_add=True,
                                          editable=False)

    role = models.CharField(max_length=2, choices=ROLES, default='M')

    can_change_settings_flag = models.BooleanField(
        default=False, verbose_name=_("Can change blog's settings"))

    can_edit_posts_flag = models.BooleanField(
        default=False, verbose_name=_("Can edit posts"))
    can_delete_posts_flag = models.BooleanField(
        default=False, verbose_name=_("Can delete posts"))

    can_edit_comments_flag = models.BooleanField(
        default=False, verbose_name=_("Can edit comments"))
    can_delete_comments_flag = models.BooleanField(
        default=False, verbose_name=_("Can delete comments"))

    can_ban_flag = models.BooleanField(
        default=False, verbose_name=_("Can ban a member"))

    def can_be_banned(self):
        return self.role not in ['O', 'A']

    @classmethod
    def ban_permanently(cls, blog, user):
        membership = cls.objects.filter(user=user, blog=blog).first()

        if membership is None:
            membership = Membership(user=user, blog=blog)

        if membership.can_be_banned():
            membership.role = 'B'
            membership.save()

    @classmethod
    def ban(cls, blog, user, timedelta):
        membership = cls.objects.filter(user=user, blog=blog).first()

        if membership is None:
            membership = Membership(user=user, blog=blog)

        if membership.can_be_banned():
            membership.ban_expiration = datetime.now() + timedelta
            membership.save()

    def is_banned(self):
        return self.role != 'B' and self.ban_expiration < datetime.now()

    def _common_check(self, flag):
        """Check that the user can perform an action

        Here to reduce code duplication.

        """
        has_perms = self.user.is_active and self.is_staff and (
            self.user.has_perm('blog.change_membership') or
            self.user.has_perm('blog.change_blog'))
        return has_perms or (self.role in ['O', 'A'] and
                             not self.is_banned() and flag)

    def can_change_settings(self):
        return self._common_check(self.can_change_settings_flag)

    def can_edit_posts(self):
        return self._common_check(self.can_edit_posts_flag)

    def can_delete_posts(self):
        return self._common_check(self.can_delete_posts_flag)

    def can_edit_comments(self):
        return self._common_check(self.can_edit_comments_flag)

    def can_delete_comments(self):
        return self._common_check(self.can_delete_comments_flag)

    def can_ban(self):
        return self._common_check(self.can_ban_flag)

    class Meta:
        unique_together = ('user', 'blog')
