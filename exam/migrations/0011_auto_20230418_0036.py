# Generated by Django 3.0.5 on 2023-04-18 00:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0010_auto_20230417_0142'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='option3',
            field=models.CharField(default='None', max_length=200),
        ),
        migrations.AlterField(
            model_name='question',
            name='option4',
            field=models.CharField(default='None', max_length=200),
        ),
        migrations.AlterField(
            model_name='question',
            name='option5',
            field=models.CharField(default='None Of the Above', max_length=200),
        ),
        migrations.AlterField(
            model_name='question',
            name='option6',
            field=models.CharField(default="Can't be determined", max_length=200),
        ),
    ]
