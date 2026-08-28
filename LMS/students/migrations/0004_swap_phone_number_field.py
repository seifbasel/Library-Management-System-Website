from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0003_populate_phone_number_str'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='phone_number',
        ),
        migrations.RenameField(
            model_name='student',
            old_name='phone_number_str',
            new_name='phone_number',
        ),
        # Meaningless leftover kwarg on a DateField - max_length has no
        # effect there and was always silently ignored by Django.
        migrations.AlterField(
            model_name='student',
            name='birthdate',
            field=models.DateField(null=True, blank=True),
        ),
    ]
