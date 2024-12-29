# status/migrations/0004_initial_statuses.py

from django.db import migrations

def create_initial_statuses(apps, schema_editor):
    Status = apps.get_model('status', 'Status')
    
    # Create default statuses
    default_statuses = ['Available', 'Borrowed']
    
    for status_name in default_statuses:
        Status.objects.get_or_create(name=status_name)

def reverse_initial_statuses(apps, schema_editor):
    Status = apps.get_model('status', 'Status')
    Status.objects.filter(name__in=['Available', 'Borrowed']).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('status', '0003_remove_status_desc'),
    ]

    operations = [
        migrations.RunPython(create_initial_statuses, reverse_initial_statuses),
    ]