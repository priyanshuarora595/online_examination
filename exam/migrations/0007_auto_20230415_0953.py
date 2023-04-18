# Generated by Django 3.0.5 on 2023-04-15 04:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0006_question_question_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='option5',
            field=models.CharField(default='op5', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='question',
            name='option6',
            field=models.CharField(default='op6', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='result',
            name='correct_answers',
            field=models.PositiveIntegerField(default='2'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='question',
            name='answer',
            field=models.CharField(choices=[('Option1', 'Option1'), ('Option2', 'Option2'), ('Option3', 'Option3'), ('Option4', 'Option4'), ('Option5', 'Option5'), ('Option6', 'Option6')], max_length=200),
        ),
        migrations.AlterField(
            model_name='question',
            name='question_image',
            field=models.ImageField(blank=True, null=True, upload_to='image/Exam/'),
        ),
    ]
