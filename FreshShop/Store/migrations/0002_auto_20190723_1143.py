# Generated by Django 2.2.1 on 2019-07-23 03:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Store', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='storetype',
            old_name='store_address',
            new_name='store_description',
        ),
    ]
