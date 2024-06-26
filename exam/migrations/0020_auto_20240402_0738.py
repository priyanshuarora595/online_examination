# Generated by Django 3.0.5 on 2024-04-02 07:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0019_course_duration'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='exam_question_size',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='course',
            name='passing_percentage',
            field=models.PositiveIntegerField(default=75),
        ),
    ]
