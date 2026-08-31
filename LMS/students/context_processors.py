from organization.models import LibrarySettings


def library_info(request):
    """Contact details, branding, and social links for the homepage/footer.

    Sourced from the LibrarySettings singleton - admin-editable per
    deployment - not from Django settings, so a customer's own staff can
    change their address/hours/social links without a redeploy.
    """
    settings_obj = LibrarySettings.get_solo()
    social_links = [
        {"label": "Instagram", "url": settings_obj.instagram_url, "icon": "instagram"},
        {"label": "X (Twitter)", "url": settings_obj.twitter_url, "icon": "twitter"},
        {"label": "Facebook", "url": settings_obj.facebook_url, "icon": "facebook"},
    ]
    return {
        "LIBRARY_INFO": {
            "name": settings_obj.organization_name,
            "address": settings_obj.address,
            "hours": settings_obj.opening_hours,
            "phone": settings_obj.support_phone,
            "email": settings_obj.support_email,
            "logo_url": settings_obj.logo.url if settings_obj.logo else "",
            "favicon_url": settings_obj.favicon.url if settings_obj.favicon else "",
        },
        "SOCIAL_LINKS": [link for link in social_links if link["url"]],
    }
