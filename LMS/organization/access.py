"""View-level enforcement of feature flags.

These are decorators, not template conditionals, so a disabled feature is
actually inaccessible - not just hidden from navigation.
"""

from functools import wraps

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from organization import features


def catalog_view(view_func):
    """Allow anonymous access only while the public catalog is enabled.

    When disabled, falls back to requiring login - the catalog becomes
    members-only instead of being taken down entirely.
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if features.is_enabled("enable_public_catalog") or request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        return login_required(view_func)(request, *args, **kwargs)

    return wrapper


def member_portal_view(view_func):
    """Gate a self-service member page behind the member-portal flag."""

    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not features.is_enabled("enable_member_portal"):
            return render(request, "organization/feature_disabled.html", status=403)
        return view_func(request, *args, **kwargs)

    return wrapper
