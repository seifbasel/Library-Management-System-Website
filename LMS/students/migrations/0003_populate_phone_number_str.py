from django.db import migrations


def populate_phone_number_str(apps, schema_editor):
    Student = apps.get_model('students', 'Student')
    for student in Student.objects.exclude(phone_number__isnull=True):
        student.phone_number_str = str(student.phone_number)
        student.save(update_fields=['phone_number_str'])


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0002_add_phone_number_str'),
    ]

    operations = [
        migrations.RunPython(populate_phone_number_str, reverse_code=migrations.RunPython.noop),
    ]
