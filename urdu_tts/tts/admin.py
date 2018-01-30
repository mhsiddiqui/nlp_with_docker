# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from tts.models import EvaluationQuestion, QuestionOption


class EvaluationQuestionAdmin(admin.ModelAdmin):
    filter_horizontal = ('option',)


admin.site.register(EvaluationQuestion, EvaluationQuestionAdmin)
admin.site.register(QuestionOption)
# admin.site.register(EvaluationData, EvaluationDataAdmin)
