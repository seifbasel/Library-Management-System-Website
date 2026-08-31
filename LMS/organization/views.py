from django.conf import settings as django_settings
from django.db import connection
from django.db.utils import OperationalError
from django.http import HttpResponse, JsonResponse
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET

from organization.models import LibrarySettings


def get_version() -> str:
    """The deployed application version, e.g. for support/troubleshooting.
    Deliberately just a version string - no build/commit/environment
    details, which could otherwise leak infrastructure information.
    """
    version_file = django_settings.BASE_DIR / "VERSION"
    try:
        return version_file.read_text().strip()
    except OSError:
        return "unknown"


@require_GET
def health_check(request):
    """A minimal, unauthenticated health check for load balancers/uptime
    monitors. Confirms the app can reach its database; nothing more -
    no stack traces, connection strings, or other internal detail.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except OperationalError:
        return JsonResponse({"status": "error"}, status=503)
    return JsonResponse({"status": "ok", "version": get_version()})


def _darken(hex_color: str, amount: float) -> str:
    """Darken a #rrggbb color by scaling each channel down (amount in [0, 1])."""
    r, g, b = _to_rgb(hex_color)
    factor = 1 - amount
    return _to_hex(r * factor, g * factor, b * factor)


def _tint(hex_color: str, amount: float) -> str:
    """Mix a #rrggbb color toward white (amount in [0, 1]) for a soft pastel background."""
    r, g, b = _to_rgb(hex_color)
    return _to_hex(
        r + (255 - r) * amount,
        g + (255 - g) * amount,
        b + (255 - b) * amount,
    )


def _to_rgb(hex_color: str):
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        hex_color = "3c4b9e"  # fall back to the default primary on a malformed value
    return (int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def _to_hex(r: float, g: float, b: float) -> str:
    r, g, b = (min(255, max(0, round(c))) for c in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"


@cache_control(max_age=300)
def branding_css(request):
    """Overrides the design-token color variables with this deployment's
    brand colors. Loaded after components.css in base.html, so every
    component that already consumes var(--color-primary) etc. - buttons,
    the nav active state, badges, the brand gradient - repaints in the
    customer's brand without any component needing to know branding exists.
    """
    settings_obj = LibrarySettings.get_solo()
    primary = settings_obj.primary_color
    secondary = settings_obj.secondary_color
    accent = settings_obj.accent_color

    css = f"""
:root {{
  --color-primary: {primary};
  --color-primary-hover: {_darken(primary, 0.15)};
  --color-primary-soft: {_tint(primary, 0.88)};
  --color-secondary: {secondary};
  --color-secondary-hover: {_darken(secondary, 0.15)};
  --color-accent: {accent};
  --color-accent-soft: {_tint(accent, 0.76)};
  --gradient-brand: linear-gradient(135deg, {primary} 0%, {accent} 55%, {secondary} 100%);
}}
""".strip()
    return HttpResponse(css, content_type="text/css")
