# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from tts.models import EvaluationQuestion, QuestionOption, GeneratedVoice, EvaluationRecord, EvaluationResult


class EvaluationQuestionAdmin(admin.ModelAdmin):
    filter_horizontal = ('option',)


class EvaluationRecordAdmin(admin.ModelAdmin):
    list_display = ['email', 'mrt', 'drt', 'intelligibility', 'naturalness', 'overall', 'status', 'timestamp']
    list_filter = ['gender', 'age']


class EvaluationResultAdmin(admin.ModelAdmin):
    list_display = ['record', 'question', 'intelligibility', 'naturalness', 'overall', 'answer', 'correct']
    list_filter = ['question__type', 'record']


class QuestionOptionAdmin(admin.ModelAdmin):
    list_display = ['text', 'correct']


admin.site.register(EvaluationQuestion, EvaluationQuestionAdmin)
admin.site.register(QuestionOption, QuestionOptionAdmin)
admin.site.register(GeneratedVoice)
admin.site.register(EvaluationRecord, EvaluationRecordAdmin)
admin.site.register(EvaluationResult, EvaluationResultAdmin)
# admin.site.register(EvaluationData, EvaluationDataAdmin)
