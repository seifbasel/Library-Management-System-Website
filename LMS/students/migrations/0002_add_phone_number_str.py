from django.db import migrations, models

import students.validators


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='phone_number_str',
            field=models.CharField(
                max_length=17,
                null=True,
                blank=True,
                validators=[students.validators.phone_regex],
            ),
        ),
    ]
