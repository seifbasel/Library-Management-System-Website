# Generated by Django 4.2.4 on 2023-08-22 14:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('status', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='status',
            name='desc',
            field=models.TextField(null=True),
        ),
    ]