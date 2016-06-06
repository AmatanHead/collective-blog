from django.core.urlresolvers import reverse
from django.http import HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView

from collective_blog.models import Blog


class BlogView(DetailView):
    model = Blog
    template_name = 'blog/blog.html'

    def dispatch(self, request, *args, **kwargs):
        self.blog_slug = kwargs.pop('blog_slug')

        if self.blog_slug != self.blog_slug.lower():
            return HttpResponsePermanentRedirect(
                reverse('view_post',
                        kwargs=dict(blog_slug=self.blog_slug.lower())))

        return super(BlogView, self).dispatch(request, *args, **kwargs)

    def get_object(self, *args, **kwargs):
        # TODO: select_related
        return get_object_or_404(Blog.objects,
                                 slug=self.blog_slug)
