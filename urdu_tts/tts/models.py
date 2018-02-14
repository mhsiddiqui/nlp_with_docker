from __future__ import unicode_literals

import re

from django.db import models
from django.dispatch import receiver

VOICE_PROPERTIES = (
    ('intelligibility', 'Intelligibility'),
    ('naturalness', 'Naturalness'),
    ('overall', 'Overall')
)

QUESTION_TYPE = (
    (1, 'DRT'),
    (2, 'MRT'),
    (3, 'MOS')
)

AGE = (
        ('1-15', '<15'),
        ('15-25', '15-25'),
        ('26-35', '26-35'),
        ('36-45', '36-45'),
        ('45+', '45+')
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

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.text = self.text.encode('utf-8', 'ignore').decode('utf-8')
        return super(QuestionOption, self).save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.text.encode('utf-8', 'ignore').decode('utf-8')

    def __unicode__(self):
        return self.text.encode('utf-8', 'ignore').decode('utf-8')


class EvaluationQuestion(models.Model):
    text = models.CharField(max_length=500)
    type = models.IntegerField(choices=QUESTION_TYPE, default=1)
    option = models.ManyToManyField(to=QuestionOption, related_name='question_options', blank=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.text = self.text.encode('utf-8', 'ignore').decode('utf-8')
        return super(EvaluationQuestion, self).save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return '%s -- %s' % (self.text.encode('utf-8', 'ignore').decode('utf-8'), dict(QUESTION_TYPE).get(self.type))

    def __unicode__(self):
        return '%s -- %s' % (self.text.encode('utf-8', 'ignore').decode('utf-8'), dict(QUESTION_TYPE).get(self.type))


class EvaluationRecord(models.Model):
    STATUS_CHOICES = (
        (1, 'Empty'),
        (2, 'Incomplete'),
        (3, 'Complete')
    )

    GENDER = (
        (1, 'Male'),
        (2, 'Female')
    )

    name = models.CharField(max_length=500)
    email = models.EmailField(max_length=500, default='no-email@email.com', blank=True, null=True)
    gender = models.IntegerField(default=1, choices=GENDER)
    age = models.CharField(max_length=20, default='15-25', choices=AGE)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    mrt = models.FloatField(default=0.0)
    drt = models.FloatField(default=0.0)
    intelligibility = models.FloatField(default=0.0)
    naturalness = models.FloatField(default=0.0)
    overall = models.FloatField(default=0.0)

    def __str__(self):
        return '%s -- %s' % (self.name, self.email)


class EvaluationResult(models.Model):
    RATING = tuple((x, x) for x in range(1, 6))

    record = models.ForeignKey(to=EvaluationRecord, related_name='evaluation_record')
    question = models.ForeignKey(to=EvaluationQuestion, related_name='evaluation_question')

    intelligibility = models.IntegerField(default=1, choices=RATING, null=True, blank=True)
    naturalness = models.IntegerField(default=1, choices=RATING, null=True, blank=True)
    overall = models.IntegerField(default=1, choices=RATING, null=True, blank=True)

    answer = models.ForeignKey(to=QuestionOption, blank=True, null=True)
    correct = models.BooleanField(default=False)

    timestamp = models.DateTimeField(auto_now_add=True)


@receiver(models.signals.pre_delete, sender=GeneratedVoice)
def remove_media_from_storage(sender, instance, **kwargs):
    instance.file.delete(save=False)
