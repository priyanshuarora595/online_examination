# Generated by Django 3.0.5 on 2023-04-13 19:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0002_teacher_salary'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='teacher',
            name='profile_pic',
        ),
    ]
