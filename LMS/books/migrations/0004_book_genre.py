# Generated by Django 4.2.4 on 2023-08-19 11:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('genre', '0001_initial'),
        ('books', '0003_book_pages'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='genre',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='books', to='genre.genre'),
        ),
    ]
