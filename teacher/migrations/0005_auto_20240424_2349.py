# Generated by Django 3.0.5 on 2024-04-24 23:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0004_teacher_organization'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teacher',
            name='salary',
            field=models.PositiveIntegerField(default=0, null=True),
        ),
    ]
