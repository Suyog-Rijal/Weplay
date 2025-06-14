# Generated by Django 5.2.1 on 2025-06-07 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('room', '0002_content_room_current_content'),
    ]

    operations = [
        migrations.AddField(
            model_name='content',
            name='image_url',
            field=models.URLField(blank=True, help_text='Optional image URL for the content', null=True),
        ),
    ]
