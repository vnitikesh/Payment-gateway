# Generated by Django 3.1.1 on 2020-09-17 17:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_loans'),
    ]

    operations = [
        migrations.RenameField(
            model_name='loans',
            old_name='data_taken',
            new_name='date_taken',
        ),
    ]