# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-02-08 20:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import tts.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EvaluationQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=500)),
                ('type', models.IntegerField(choices=[(1, 'DRT'), (2, 'MRT'), (3, 'MOS')], default=1)),
            ],
        ),
        migrations.CreateModel(
            name='EvaluationRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=500)),
                ('email', models.EmailField(blank=True, default='no-email@email.com', max_length=500, null=True)),
                ('gender', models.IntegerField(choices=[(1, 'Male'), (2, 'Female')], default=1)),
                ('age', models.CharField(choices=[('1-15', '<15'), ('15-25', '15-25'), ('26-35', '26-35'), ('36-45', '36-45'), ('45+', '45+')], default='15-25', max_length=20)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('status', models.IntegerField(choices=[(1, 'Empty'), (2, 'Incomplete'), (3, 'Complete')], default=1)),
                ('mrt', models.FloatField(default=0.0)),
                ('drt', models.FloatField(default=0.0)),
                ('understandability', models.FloatField(default=0.0)),
                ('naturalness', models.FloatField(default=0.0)),
                ('overall', models.FloatField(default=0.0)),
            ],
        ),
        migrations.CreateModel(
            name='EvaluationResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('understandability', models.IntegerField(blank=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=1, null=True)),
                ('naturalness', models.IntegerField(blank=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=1, null=True)),
                ('overall', models.IntegerField(blank=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=1, null=True)),
                ('correct', models.BooleanField(default=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='GeneratedVoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to=tts.models.upload_file)),
                ('text', models.CharField(default='', max_length=1000)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('ip', models.CharField(default='', max_length=100)),
                ('voice', models.CharField(default='', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='QuestionOption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=200)),
                ('correct', models.BooleanField(default=False)),
            ],
        ),
        migrations.AddField(
            model_name='evaluationresult',
            name='answer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tts.QuestionOption'),
        ),
        migrations.AddField(
            model_name='evaluationresult',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='evaluation_question', to='tts.EvaluationQuestion'),
        ),
        migrations.AddField(
            model_name='evaluationresult',
            name='record',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='evaluation_record', to='tts.EvaluationRecord'),
        ),
        migrations.AddField(
            model_name='evaluationquestion',
            name='option',
            field=models.ManyToManyField(blank=True, related_name='question_options', to='tts.QuestionOption'),
        ),
    ]
