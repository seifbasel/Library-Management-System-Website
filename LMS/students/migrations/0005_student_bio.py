# Generated by Django 4.2.4 on 2023-08-21 23:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0004_alter_student_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='bio',
            field=models.CharField(default='23r', max_length=255),
        ),
    ]
