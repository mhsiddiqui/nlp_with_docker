# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

from django.db import models
from django.dispatch import receiver

VOICE_PROPERTIES = (
    (1, 'Understandability'),
    (2, 'Naturalness'),
    (3, 'Overall')
)

QUESTION_TYPE = (
    (1, 'DRT/MRT'),
    (2, 'MOS')
)


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
    voice = models.CharField(default='', max_length=200)


class QuestionOption(models.Model):
    text = models.CharField(max_length=200)
    correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text.encode('utf-8')


class EvaluationQuestion(models.Model):
    text = models.CharField(max_length=500)
    type = models.IntegerField(choices=QUESTION_TYPE, default=1)
    option = models.ManyToManyField(to=QuestionOption, related_name='question_options', blank=True)

    def __str__(self):
        return '%s -- %s' % (self.text.encode('utf-8'), dict(QUESTION_TYPE).get(self.type))


class EvaluationRecord(models.Model):
    STATUS_CHOICES = (
        (1, 'Empty'),
        (2, 'Incomplete'),
        (3, 'Complete')
    )

    name = models.CharField(max_length=500)
    email = models.EmailField(max_length=500, default='no-email@email.com', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    mdrt = models.FloatField(default=0.0)
    mos = models.FloatField(default=0.0)

    def __str__(self):
        return '%s -- %s -- %s' % (self.name, self.email, self.ip)


class EvaluationResult(models.Model):
    RATING = tuple((x, x) for x in range(1, 6))

    record = models.ForeignKey(to=EvaluationRecord, related_name='evaluation_record')
    question = models.ForeignKey(to=EvaluationQuestion, related_name='evaluation_question')

    understandability = models.IntegerField(default=1, choices=RATING)
    naturalness = models.IntegerField(default=1, choices=RATING)
    overall = models.IntegerField(default=1, choices=RATING)

    answer = models.ForeignKey(to=QuestionOption, blank=True, null=True)
    correct = models.BooleanField(default=False)

    timestamp = models.DateTimeField(auto_now_add=True)


@receiver(models.signals.pre_delete, sender=GeneratedVoice)
def remove_media_from_storage(sender, instance, **kwargs):
    instance.file.delete(save=False)
