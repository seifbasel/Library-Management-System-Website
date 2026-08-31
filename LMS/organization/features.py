"""A single, clean entry point for feature-flag checks.

Usage: `if features.is_enabled("enable_fines"): ...`

Flag names are exactly the boolean field names on LibrarySettings - no
separate registry to keep in sync, and no magic string-to-behavior mapping
to maintain. Enforcement happens server-side (see organization/access.py
for view-level gates); never rely on hiding a link in a template alone.
"""

from organization.models import LibrarySettings


def is_enabled(flag_name: str) -> bool:
    settings_obj = LibrarySettings.get_solo()
    if not hasattr(settings_obj, flag_name):
        raise ValueError(f"Unknown feature flag: {flag_name!r}")
    return bool(getattr(settings_obj, flag_name))
