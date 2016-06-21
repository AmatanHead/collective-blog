from datetime import timedelta

from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponsePermanentRedirect
from django.utils import timezone
from django.views.generic import ListView

from collective_blog.models import Post, Membership


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
            context['interesting_blogs'] = []
        else:
            context['interesting_blogs'] = {
                m.blog.id: m for m in Membership.objects.filter(user=self.request.user).filter(role__in=['O', 'M', 'A'])
            }

        return context

    def get_queryset(self):
        """Returns a queryset of posts that are visible to a user"""
        return (Post.objects
                .select_related('author', 'blog')
                .filter(
                    Q(blog__type='O') | (
                        Q(blog__members=self.request.user) &
                        Q(blog__membership__role__in=['O', 'M', 'A'])
                    ) if not self.request.user.is_anonymous() else (
                        Q(blog__type='O')
                    ),
                    is_draft=False)
                .distinct())


class FeedView(GenericFeedView):
    """A view for displaying main feed (homepage and others)"""
    template_name = 'blog/feed.html'
    type = 'homepage'

    def get_context_data(self, **kwargs):
        context = super(FeedView, self).get_context_data(**kwargs)
        context['type'] = self.type
        return context


class GenericBestFeedView(FeedView):
    """A view for displaying feed ordered by rating"""
    template_name = 'blog/feed.html'
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
    template_name = 'blog/feed.html'
    time = timedelta(days=1)
    type = 'feed_day_best'


class MonthBestFeedView(GenericBestFeedView):
    template_name = 'blog/feed.html'
    time = timedelta(days=30)
    type = 'feed_month_best'


class BestFeedView(GenericBestFeedView):
    template_name = 'blog/feed.html'
    type = 'feed_best'


class PersonalFeedView(FeedView):
    """A view for displaying personal feed ordered by time"""
    template_name = 'blog/feed.html'
    type = 'feed_personal'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_anonymous():
            return HttpResponsePermanentRedirect(
                reverse('homepage', kwargs=kwargs))
        return super(PersonalFeedView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        return (
            super(PersonalFeedView, self).get_queryset()
            .filter(blog__membership__role__in=['O', 'M', 'A'],
                    blog__members=self.request.user)
        )


class MyPostsFeedView(GenericFeedView):
    """A view for displaying personal feed ordered by time"""
    template_name = 'blog/feed_drafts.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_anonymous():
            return HttpResponsePermanentRedirect(
                reverse('homepage', kwargs=kwargs))
        return super(MyPostsFeedView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        return (
            Post.objects
                .select_related('author', 'blog')
                .filter(author=self.request.user)
                .distinct()
                .order_by('updated')
        )
