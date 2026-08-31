from django.db import migrations

# Librarians get full CRUD over the catalog/circulation domain via Django
# admin. They deliberately do NOT get permissions on User, Group,
# Permission, or LibrarySettings - organization/user administration stays
# superuser-only. This is real, server-side-enforced role separation
# (Django admin checks these permissions itself), not a UI convenience.
LIBRARIAN_MODELS = [
    ("books", "book"),
    ("genre", "genre"),
    ("status", "status"),
    ("loans", "loan"),
    ("loans", "fine"),
    ("students", "student"),
]
PERMISSION_ACTIONS = ["view", "add", "change", "delete"]


def create_librarian_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")

    group, _ = Group.objects.get_or_create(name="Librarians")

    permissions = []
    for app_label, model_name in LIBRARIAN_MODELS:
        try:
            content_type = ContentType.objects.get(app_label=app_label, model=model_name)
        except ContentType.DoesNotExist:
            continue
        for action in PERMISSION_ACTIONS:
            try:
                permissions.append(
                    Permission.objects.get(content_type=content_type, codename=f"{action}_{model_name}")
                )
            except Permission.DoesNotExist:
                continue

    group.permissions.set(permissions)


def remove_librarian_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name="Librarians").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("organization", "0001_initial"),
        ("books", "0005_alter_book_options_book_created_at"),
        ("genre", "0003_alter_genre_options_alter_genre_name"),
        ("status", "0003_alter_status_options_alter_status_name"),
        ("loans", "0002_fine"),
        ("students", "0004_swap_phone_number_field"),
    ]

    operations = [
        migrations.RunPython(create_librarian_group, reverse_code=remove_librarian_group),
    ]
