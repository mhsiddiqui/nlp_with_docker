# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
from django.db import models

# Create your models here.
from django.dispatch import receiver


def upload_file(instance, filename):
    timestamp = re.sub('[^A-Za-z0-9]+', '', str(instance.time))
    return 'voice/{ip}/{timestamp}/{filename}'.format(**{
        "ip": instance.ip, "timestamp": timestamp, "filename": "voice.wav"
    })


class GeneratedVoice(models.Model):
    file = models.FileField(upload_to=upload_file)
    text = models.CharField(default='', max_length=1000)
    time = models.DateTimeField(auto_now_add=True)
    ip = models.CharField(default='', max_length=100)


class EvaluationData(models.Model):

    text = models.CharField(default='', max_length=500)

    def __str__(self):
        return self.text.encode('utf-8')


class Evaluation(models.Model):
    RATING = tuple((x, x) for x in range(1, 6))

    data = models.ForeignKey(to=EvaluationData, related_name='evaluation_of_data')
    understandability = models.IntegerField(default=1, choices=RATING)
    naturalness = models.IntegerField(default=1, choices=RATING)
    pleasantness = models.IntegerField(default=1, choices=RATING)
    overall = models.IntegerField(default=1, choices=RATING)
    voice = models.CharField(default='', max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)


@receiver(models.signals.pre_delete, sender=GeneratedVoice)
def remove_chat_media_from_s3(sender, instance, **kwargs):
    instance.file.delete(save=False)
