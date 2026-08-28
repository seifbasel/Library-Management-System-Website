from django.db import migrations


def dedupe_status_names(apps, schema_editor):
    """Merge any Status rows sharing the same name before name becomes unique.

    For each duplicate group, keep the lowest-pk row as canonical, repoint
    every Book referencing a duplicate to the canonical row, then delete
    the duplicates.
    """
    Status = apps.get_model('status', 'Status')
    Book = apps.get_model('books', 'Book')

    canonical_by_name = {}
    for status in Status.objects.order_by('id'):
        canonical_id = canonical_by_name.get(status.name)
        if canonical_id is None:
            canonical_by_name[status.name] = status.id
            continue
        Book.objects.filter(status_id=status.id).update(status_id=canonical_id)
        status.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('status', '0001_initial'),
        ('books', '0003_remove_book_borrow_fields'),
    ]

    operations = [
        migrations.RunPython(dedupe_status_names, reverse_code=migrations.RunPython.noop),
    ]
