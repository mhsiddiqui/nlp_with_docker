# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from tts.models import EvaluationData


class EvaluationDataAdmin(admin.ModelAdmin):
    fields = ('text',)


admin.site.register(EvaluationData, EvaluationDataAdmin)
