# Generated by Django 3.0.5 on 2024-03-19 08:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0011_auto_20230418_0036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='answer',
            field=models.CharField(choices=[('Option1', 'Option1'), ('Option2', 'Option2'), ('Option3', 'Option3'), ('Option4', 'Option4')], max_length=200),
        ),
    ]
