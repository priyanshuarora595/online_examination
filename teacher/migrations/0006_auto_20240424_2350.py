# Generated by Django 3.0.5 on 2024-04-24 23:50

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0005_auto_20240424_2349'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teacher',
            name='mobile',
            field=models.CharField(max_length=12, validators=[django.core.validators.MinLengthValidator(9), django.core.validators.MaxLengthValidator(12), django.core.validators.RegexValidator('^[+]?[0-9]{9,12}$')]),
        ),
    ]
