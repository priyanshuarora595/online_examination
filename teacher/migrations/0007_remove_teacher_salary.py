# Generated by Django 3.0.5 on 2024-04-25 18:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0006_auto_20240424_2350'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='teacher',
            name='salary',
        ),
    ]
