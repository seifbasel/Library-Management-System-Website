# Generated by Django 4.2.4 on 2023-08-23 23:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0010_book_return_date_alter_book_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='book',
            name='active',
        ),
    ]