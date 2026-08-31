from django.conf import settings
from django.shortcuts import render


class MaintenanceModeMiddleware:
    """Serves a plain maintenance page for every request when
    MAINTENANCE_MODE is set, without touching the database or exposing any
    technical detail. Deliberately an environment variable, not a
    LibrarySettings field - it needs to work even when the database itself
    is unavailable (e.g. mid-migration during an upgrade).

    The admin site stays reachable so staff can investigate/confirm the fix
    without needing to unset the flag first.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if getattr(settings, "MAINTENANCE_MODE", False) and not request.path.startswith("/admin/"):
            return render(request, "organization/maintenance.html", status=503)
        return self.get_response(request)
