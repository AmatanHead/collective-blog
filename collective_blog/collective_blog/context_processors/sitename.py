from collective_blog import settings

def sitename(request):
    """Add site_name variable to template context"""
    return {
        'global_site_name': settings.SITE_NAME,
    }
