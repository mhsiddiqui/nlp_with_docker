# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-02-13 20:10
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tts', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='evaluationresult',
            old_name='understandability',
            new_name='intelligibility',
        ),
    ]
