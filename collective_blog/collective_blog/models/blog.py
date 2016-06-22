from django.db import models
from django.db.models import Q, QuerySet, F
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from collective_blog import settings
from collective_blog.utils.errors import PermissionCheckFailed

from s_markdown.models import MarkdownField, HtmlCacheField
from s_markdown.datatype import Markdown
from s_markdown.renderer import BaseRenderer
from s_markdown.extensions import (FencedCodeExtension,
                                   EscapeHtmlExtension,
                                   SemiSaneListExtension,
                                   StrikethroughExtension,
                                   AutomailExtension,
                                   AutolinkExtension,
                                   CommentExtension)
from s_appearance.utils.icons import ICONS
from s_voting.models import VoteCacheField

from .post import PostVote

from uuslug import uuslug


class Blog(models.Model):
    name = models.CharField(max_length=100,
                            verbose_name=_('Name'),
                            unique=True)

    slug = models.SlugField(max_length=100,
                            db_index=True,
                            unique=True,
                            blank=True,
                            editable=False)

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
        ('A', _('Anyone can add posts')),
        ('K', _('Only users with high karma can add posts')),
    )

    post_condition = models.CharField(max_length=2, default='K',
                                      choices=POST_CONDITIONS,
                                      verbose_name=_('Who can add posts'))

    post_membership_required = models.BooleanField(
        default=True, verbose_name=_('Require membership to write posts'))

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

    # Common methods
    # --------------

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        self.slug = uuslug(self.name,
                           instance=self,
                           max_length=100,
                           start_no=2,
                           word_boundary=True,
                           save_order=True)

        self.slug = self.slug.lower()

        super(Blog, self).save(force_insert, force_update, using, update_fields)

    class Meta:
        verbose_name = _("Blog")
        verbose_name_plural = _("Blogs")
        ordering = ("name",)

    def __str__(self):
        return str(self.name)

    # Permissions control
    # -------------------

    def check_membership(self, user):
        """Check if the given user is a member of the blog"""
        if user.is_anonymous():
            return None
        return Membership.objects.filter(blog=self, user=user).with_rating().first()

    @staticmethod
    def can_be_moderated_by(user):
        """Check if the user is a moderator with profile editing rights"""
        return user.is_active and user.is_staff and (
            user.has_perm('blog.change_membership') or
            user.has_perm('blog.change_blog'))

    @staticmethod
    def is_banned(membership):
        """Check if the given user is banned in this blog

        No-members (membership==None) considered to be not banned.

        """
        if membership is not None and not membership.is_left():
            return membership.is_banned()
        else:
            return False

    @staticmethod
    def check_can_change_settings(membership):
        """Check if the given user has permissions to change settings

        No-members (membership==None) considered to have no rights.

        """
        if membership is not None and not membership.is_left():
            return membership.can_change_settings()
        else:
            return False

    @staticmethod
    def check_can_delete_posts(membership):
        """Check if the given user has permissions delete posts in the blog

        No-members (membership==None) considered to have no rights.

        """
        if membership is not None and not membership.is_left():
            return membership.can_delete_posts()
        else:
            return False

    @staticmethod
    def check_can_delete_comments(membership):
        """Check if the given user has permissions delete comments in the blog

        No-members (membership==None) considered to have no rights.

        """
        if membership is not None and not membership.is_left():
            return membership.can_delete_comments()
        else:
            return False

    @staticmethod
    def check_can_ban(membership):
        """Check if the given user has permissions to ban members of the blog

        No-members (membership==None) considered to have no rights.

        """
        if membership is not None and not membership.is_left():
            return membership.can_ban()
        else:
            return False

    @staticmethod
    def check_can_accept_new_users(membership):
        """Check if the given user has permissions to can accept new users

        No-members (membership==None) considered to have no rights.

        """
        if membership is not None and not membership.is_left():
            return membership.can_accept_new_users()
        else:
            return False

    @staticmethod
    def check_can_manage_permissions(membership):
        """Check if the given user has permissions to manage permissions
        of other users.

        No-members (membership==None) considered to have no rights.

        """
        if membership is not None and not membership.is_left():
            return membership.can_manage_permissions()
        else:
            return False

    def check_can_post(self, user):
        """Check if the given user has permissions to add posts to this blog"""
        if not user.is_active or user.is_anonymous():
            return False

        membership = self.check_membership(user)

        if ((self.type != 'O' or self.post_membership_required) and
                (membership is None or
                 membership.is_banned() or
                 membership.is_left())):
            return False
        elif (self.post_condition == 'K' and
                user.profile.karma < self.post_karma_threshold):
            return False
        else:
            return True

    def check_can_join(self, user):
        """Checks if the user can join the blog

        Note that joining process should go through the special method.
        Note also that this method returns `True` for blogs with manual
        approval required.

        Makes database queries: `check_membership` and karma calculation.

        """
        if not user.is_active or user.is_anonymous():
            return False

        membership = self.check_membership(user)

        if membership is not None and not membership.is_left():
            return False  # Already joined

        if self.join_condition == 'A':
            return True
        elif self.join_condition == 'K':
            return user.profile.karma >= self.join_karma_threshold
        elif self.join_condition == 'I':
            return True  # Can send a request
        else:
            return False

    # Actions
    # -------

    def join(self, user, role=None):
        """Add the user to the blog's membership

        :param user: User which wants to be a member.
        :param role: Force the role of the user. Ignore join conditions.
        Does change the role of the users who already joined.
        :return: Message or None if the role passed.
        :raises PermissionCheckFailed: If the user can't join the blog.

        """
        if self.check_can_join(user):
            membership, c = Membership.objects.get_or_create(user=user, blog=self)
            if role is not None:
                membership.role = role
                membership.save()
                return
            if membership.role == 'LB':
                membership.role = 'B'
                membership.color = 'gray'
                membership.save()
                return _("Success. You are still banned, though")
            elif membership.role != 'L':
                return _("You've already joined to the=is blog")
            elif self.join_condition == 'I':
                membership.role = 'W'
                membership.color = ''
                membership.save()
                return _("A request has been sent")
            else:
                membership.role = 'M'
                membership.color = 'gray'
                membership.save()
                return _("Success")
        else:
            raise PermissionCheckFailed(_("You can't join this blog"))

    def leave(self, user):
        """Remove the user to the blog's membership

        :param user: User which wants to leave.

        """
        membership = self.check_membership(user)
        if membership is not None and membership.role != 'O':
            if membership.role == 'B':
                membership.role = 'LB'
            else:
                membership.role = 'L'
            membership.color = ''
            membership.save()


class MembershipQuerySet(QuerySet):
    """Queryset of votes

    Allows for routine operations like getting overall rating etc.

    """
    def with_rating(self):
        """Annotate rating of the member"""
        return self.annotate(
            rating=F('overall_posts_rating') * 10
        )


class MembershipManager(models.Manager):
    """Wrap objects to the `MembershipQuerySet`"""

    def get_queryset(self):
        return MembershipQuerySet(self.model)


def _overall_posts_rating_cache_query(v):
    return (Q(user__pk=v.object.author.pk) & Q(blog__pk=v.object.blog.pk) & ~Q(
        role__in=['L', 'LB']))


class Membership(models.Model):
    """Members of blogs"""

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             models.CASCADE)
    blog = models.ForeignKey(Blog,
                             models.CASCADE)

    COLORS = (
        ('gray', _('Gray')),
        ('black', _('Black')),
        ('blue', _('Blue')),
        ('orange', _('Orange')),
        ('purple', _('Purple')),
        ('marshy', _('Marshy')),
        ('turquoise', _('Turquoise')),
        ('red', _('Red')),
        ('yellow', _('Yellow')),
        ('green', _('Green')),
    )

    color = models.CharField(max_length=10, choices=COLORS, default='gray')

    ROLES = (
        ('O', _('Owner')),
        ('M', _('Member')),
        ('B', _('Banned')),
        ('A', _('Administrator')),
        ('W', _('Waiting for approval')),
        ('L', _('Left the blog')),
        ('LB', _('Left the blog (banned)')),
    )

    ROLE_ORDERING = dict(O=0, A=2, W=3, M=4, B=5, LB=5, L=6)

    role = models.CharField(max_length=2, choices=ROLES, default='L')

    ban_expiration = models.DateTimeField(default=timezone.now)

    can_change_settings_flag = models.BooleanField(
        default=False, verbose_name=_("Can change blog's settings"))

    can_delete_posts_flag = models.BooleanField(
        default=False, verbose_name=_("Can delete posts"))

    can_delete_comments_flag = models.BooleanField(
        default=False, verbose_name=_("Can delete comments"))

    can_ban_flag = models.BooleanField(
        default=False, verbose_name=_("Can ban a member"))

    can_accept_new_users_flag = models.BooleanField(
        default=False, verbose_name=_("Can accept new users"))

    can_manage_permissions_flag = models.BooleanField(
        default=False, verbose_name=_("Can manage permissions"))

    overall_posts_rating = VoteCacheField(PostVote, _overall_posts_rating_cache_query)

    # Common methods
    # --------------

    objects = MembershipManager()

    class Meta:
        unique_together = ('user', 'blog')

    def __str__(self):
        return str(self.user) + ' in ' + str(self.blog)

    # Permissions control
    # -------------------

    def can_be_banned(self):
        return self.role in ['M', 'B', 'LB']

    def ban(self, time=None):
        if self.can_be_banned():
            if time is None:
                self.role = 'B'
            else:
                self.ban_expiration = timezone.now() + time
            self.save()

    def unban(self):
        if self.can_be_banned():
            self.role = 'M'
            self.ban_expiration = timezone.now()
            self.save()

    def is_banned(self):
        return self.role == 'B' or self.ban_expiration >= timezone.now()

    def ban_is_permanent(self):
        return self.role == 'B'

    def is_left(self):
        return self.role in ['L', 'LB']

    def _common_check(self, flag):
        """Check that the member can perform an action

        Here to reduce code duplication.

        """
        has_perms = self.user.is_active and self.user.is_staff and (
            self.user.has_perm('blog.change_membership') or
            self.user.has_perm('blog.change_blog'))
        return has_perms or (self.role in ['O', 'A'] and
                             not self.is_left() and
                             not self.is_banned() and
                             (flag or self.role == 'O'))

    def can_change_settings(self):
        return self._common_check(self.can_change_settings_flag)

    def can_delete_posts(self):
        return self._common_check(self.can_delete_posts_flag)

    def can_delete_comments(self):
        return self._common_check(self.can_delete_comments_flag)

    def can_ban(self):
        return self._common_check(self.can_ban_flag)

    def can_accept_new_users(self):
        return self._common_check(self.can_accept_new_users_flag)

    def can_manage_permissions(self):
        return self._common_check(self.can_manage_permissions_flag)
