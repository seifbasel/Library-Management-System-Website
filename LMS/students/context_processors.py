from django.conf import settings


def library_info(request):
    """Contact details and social links shown in the homepage and footer.

    Sourced from settings (with sensible defaults) so there is exactly one
    place to update them - not scattered across templates.
    """
    return {
        "LIBRARY_INFO": getattr(settings, "LIBRARY_INFO", {}),
        "SOCIAL_LINKS": getattr(settings, "SOCIAL_LINKS", []),
    }
