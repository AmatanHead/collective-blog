from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from collective_blog.models import Post, Membership, Tag


class GenericFeedView(ListView):
    """This is the mixin for displaying a feed

    Overload `get_queryset` and `get_context_data` to alter the results.

    """

    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(GenericFeedView, self).get_context_data(**kwargs)

        if self.paginate_by:
            page_obj = context['page_obj']
            frm = max(1, page_obj.number - 5)
            to = min(page_obj.number + 5, page_obj.paginator.num_pages) + 1
            context['pages'] = range(frm, to)

        if self.request.user.is_anonymous():
            context['interesting_blogs'] = {}
        else:
            context['interesting_blogs'] = {
                m.blog.id: m for m in Membership.objects.filter(user=self.request.user)
            }

        return context

    def get_queryset(self):
        """Returns a queryset of posts that are visible to a user"""
        return (self._get_queryset()
                .filter(
                    Q(blog__type='O') | (
                        Q(blog__members=self.request.user) &
                        Q(blog__membership__role__in=['O', 'M', 'A'])
                    ) if not self.request.user.is_anonymous() else (
                        Q(blog__type='O')
                    ),
                    is_draft=False))

    def _get_queryset(self):
        return (Post.objects
                .select_related('author', 'blog')
                .prefetch_related('tags')
                .distinct())


class FeedView(GenericFeedView):
    """A view for displaying main feed (homepage and others)"""
    template_name = 'collective_blog/feed.html'
    type = 'homepage'

    def get_context_data(self, **kwargs):
        context = super(FeedView, self).get_context_data(**kwargs)
        context['type'] = self.type
        return context


class GenericBestFeedView(FeedView):
    """A view for displaying feed ordered by rating"""
    template_name = 'collective_blog/feed.html'
    time = None

    def get_queryset(self):
        query = (
            super(GenericBestFeedView, self).get_queryset()
            .order_by('-rating')
        )
        if self.time is not None:
            query = query.filter(created__gt=timezone.now() - self.time)
        return query


class DayBestFeedView(GenericBestFeedView):
    template_name = 'collective_blog/feed.html'
    time = timedelta(days=1)
    type = 'feed_day_best'


class MonthBestFeedView(GenericBestFeedView):
    template_name = 'collective_blog/feed.html'
    time = timedelta(days=30)
    type = 'feed_month_best'


class BestFeedView(GenericBestFeedView):
    template_name = 'collective_blog/feed.html'
    type = 'feed_best'


@method_decorator(login_required, 'dispatch')
class PersonalFeedView(FeedView):
    """A view for displaying personal feed ordered by time"""
    template_name = 'collective_blog/feed.html'
    type = 'feed_personal'

    def get_queryset(self):
        return (
            super(PersonalFeedView, self).get_queryset()
            .filter(blog__membership__role__in=['O', 'M', 'A'],
                    blog__members=self.request.user)
        )


@method_decorator(login_required, 'dispatch')
class MyPostsFeedView(GenericFeedView):
    """A view for displaying personal feed ordered by time"""
    template_name = 'collective_blog/feed_drafts.html'

    def get_queryset(self):
        return (self._get_queryset()
                .filter(author=self.request.user)
                .order_by('-is_draft', 'updated'))


class TagFeedView(FeedView):
    template_name = 'collective_blog/feed_tags.html'
    type = 'feed_tag'

    def dispatch(self, request, *args, **kwargs):
        self.tag_slug = kwargs.pop('tag_slug')

        if self.tag_slug != self.tag_slug.lower():
            return HttpResponsePermanentRedirect(
                reverse('feed_tag',
                        kwargs=dict(tag_slug=self.tag_slug.lower())))

        self.tag = get_object_or_404(Tag, slug=self.tag_slug)

        return super(TagFeedView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return (
            super(TagFeedView, self).get_queryset()
            .filter(tags=self.tag)
        )

    def get_context_data(self, **kwargs):
        context = super(TagFeedView, self).get_context_data(**kwargs)
        context['tag'] = self.tag
        context['interesting_tags'] = [self.tag]
        print(context)
        return context
