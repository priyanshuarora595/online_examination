# Generated by Django 3.0.5 on 2024-03-22 07:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0015_auto_20240322_0605'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='answer',
        ),
        migrations.RemoveField(
            model_name='question',
            name='option1',
        ),
        migrations.RemoveField(
            model_name='question',
            name='option2',
        ),
        migrations.RemoveField(
            model_name='question',
            name='option3',
        ),
        migrations.RemoveField(
            model_name='question',
            name='option4',
        ),
        migrations.RemoveField(
            model_name='question',
            name='option5',
        ),
        migrations.RemoveField(
            model_name='question',
            name='option6',
        ),
    ]
