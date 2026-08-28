from django.db import migrations


def dedupe_genre_names(apps, schema_editor):
    """Merge any Genre rows sharing the same name before name becomes unique.

    For each duplicate group, keep the lowest-pk row as canonical, repoint
    every Book referencing a duplicate to the canonical row, then delete
    the duplicates.
    """
    Genre = apps.get_model('genre', 'Genre')
    Book = apps.get_model('books', 'Book')

    canonical_by_name = {}
    for genre in Genre.objects.order_by('id'):
        canonical_id = canonical_by_name.get(genre.name)
        if canonical_id is None:
            canonical_by_name[genre.name] = genre.id
            continue
        Book.objects.filter(genre_id=genre.id).update(genre_id=canonical_id)
        genre.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('genre', '0001_initial'),
        ('books', '0003_remove_book_borrow_fields'),
    ]

    operations = [
        migrations.RunPython(dedupe_genre_names, reverse_code=migrations.RunPython.noop),
    ]
