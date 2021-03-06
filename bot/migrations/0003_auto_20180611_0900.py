# Generated by Django 2.0.5 on 2018-06-11 09:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0002_auto_20180611_0821'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='employees',
            unique_together={('employee_id', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='logtimes',
            unique_together={('project_id', 'user_id', 'log_date')},
        ),
        migrations.AlterUniqueTogether(
            name='projects',
            unique_together={('project_id', 'name')},
        ),
    ]
