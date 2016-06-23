"""Context processor that adds current site name to the template context"""

from collective_blog import settings


def sitename(request):
    """Add site_name variable to the template context

    :param request: Current request.
    :return: New variables to add.

    """
    return {
        'global_site_name': settings.SITE_NAME,
    }
