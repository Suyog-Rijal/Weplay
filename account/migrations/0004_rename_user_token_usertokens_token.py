# Generated by Django 5.2.1 on 2025-05-27 10:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_usertokens'),
    ]

    operations = [
        migrations.RenameField(
            model_name='usertokens',
            old_name='user_token',
            new_name='token',
        ),
    ]
