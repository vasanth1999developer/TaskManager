# Generated by Django 5.1.3 on 2024-11-28 09:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mytask', '0004_task_taskhistory'),
    ]

    operations = [
        migrations.RenameField(
            model_name='task',
            old_name='current_Assignee',
            new_name='current_assignee',
        ),
    ]
