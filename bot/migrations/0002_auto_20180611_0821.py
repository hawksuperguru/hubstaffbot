# Generated by Django 2.0.5 on 2018-06-11 08:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='organizations',
            unique_together={('organization_id', 'name')},
        ),
    ]