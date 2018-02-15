# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from collections import OrderedDict
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from django.http import HttpResponse
from django.views.generic import ListView
from ipware.ip import get_ip
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, response, status, renderers

from tts.models import GeneratedVoice, QUESTION_TYPE, EvaluationQuestion, AGE, EvaluationRecord, EvaluationResult
from tts.serializers import GeneratedVoiceSerializer, GenerateVoiceSerializer, EvaluationRecordSerializer, \
    EvaluationQuestionSerializer, EvaluationResultSerializer
from tts.utils import UtilMethods
from urdu_tts.settings import SOUND_OPTIONS
from django.shortcuts import render

# Create your views here.
from django.views import View
from django.views.generic import TemplateView


class TTSPage(TemplateView):
    template_name = 'tts/introduction.html'

    def get_context_data(self, **kwargs):
        context = super(TTSPage, self).get_context_data(**kwargs)
        context.update({'navlink': 'main'})
        return context


class DemoPage(TemplateView):
    template_name = 'tts/demo.html'

    def get_context_data(self, **kwargs):
        context = super(DemoPage, self).get_context_data(**kwargs)
        context.update({'navlink': 'demo', 'sounds': dict(SOUND_OPTIONS)})
        return context


class GenerateVoiceJson(generics.GenericAPIView):

    serializer_class = GenerateVoiceSerializer
    authentication_classes = ()
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        UtilMethods.create_temp_directories_if_does_not_exist()
        self.delete_old_generated_voice()
        serialized = self.get_serializer(data=request.data)
        if serialized.is_valid(raise_exception=True):
            generated_obj = serialized.save()
            serialized_gen_obj = GeneratedVoiceSerializer(generated_obj, context={'request': request})
            return response.Response(data=serialized_gen_obj.data)
        return response.Response(status=status.HTTP_400_BAD_REQUEST)

    def delete_old_generated_voice(self):
        GeneratedVoice.objects.filter(ip=get_ip(self.request)).delete()


class GenerateVoiceHTML(GenerateVoiceJson):
    renderer_classes = [renderers.TemplateHTMLRenderer]
    template_name = 'tts/voice_demo.html'


class EvaluateVoice(generics.GenericAPIView):
    serializer_class = EvaluationRecordSerializer
    authentication_classes = ()
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return response.Response(data=serializer.data)
        else:
            return response.Response(status=status.HTTP_400_BAD_REQUEST)


class EvaluationQuestionsView(generics.GenericAPIView):
    serializer_class = EvaluationQuestionSerializer
    authentication_classes = ()
    permission_classes = ()

    def get(self, request, *args, **kwargs):
        questions = EvaluationQuestion.objects.all().order_by('type', 'id')
        page_data = self.paginate_queryset(questions)
        if page_data:
            serializer = self.get_serializer(page_data, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            return response.Response(status=status.HTTP_404_NOT_FOUND)

    def get_paginated_data(self, page):
        question_type = 1
        page_data = None
        if not page:
            question_type = 1
        while question_type <= dict(QUESTION_TYPE).keys()[-1]:
            questions = EvaluationQuestion.objects.all().order_by('id')
            page_data = self.paginate_queryset(questions)
            if not page_data:
                question_type += 1
            else:
                break
        return page_data, question_type


class EvaluationQuestionsViewHTML(EvaluationQuestionsView):
    renderer_classes = [renderers.TemplateHTMLRenderer]
    template_name = 'tts/evaluation_form.html'


class EvaluationPage(TemplateView):
    template_name = 'tts/evaluation.html'

    def get_context_data(self, **kwargs):
        context = super(EvaluationPage, self).get_context_data(**kwargs)
        context.update({'navlink': 'evaluate', 'age_range': OrderedDict(AGE), 'section': 'Personal Information'})
        return context


class EvaluationFormSubmit(generics.GenericAPIView):
    serializer_class = EvaluationResultSerializer
    authentication_classes = ()
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        form = kwargs.get('form')
        record = EvaluationRecord.objects.filter(id=form)
        if record.exists():
            EvaluationResult.objects.filter(record=record.first()).delete()
            serializer = self.serializer_class(data=request.data, context={'record': record.first()}, many=True)
            if serializer.is_valid():
                serializer.save()
                UtilMethods.add_task_in_queue('evaluation_form_post_processing', countdown=0, record=form)
                return response.Response(status=status.HTTP_200_OK)
            return response.Response(status=status.HTTP_404_NOT_FOUND)
        else:
            return response.Response(status=status.HTTP_404_NOT_FOUND)


class EvaluationResultView(ListView):
    paginate_by = 10
    template_name = 'tts/evaluation_result.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(EvaluationResultView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return EvaluationRecord.objects.filter(status=3).order_by('-timestamp')

    def get_context_data(self, **kwargs):
        context = super(EvaluationResultView, self).get_context_data(**kwargs)
        overall = EvaluationRecord.objects.filter(status=3).aggregate(
            mrt_avg=Avg('mrt'),
            drt_avg=Avg('drt'),
            intelligibility_avg=Avg('intelligibility'),
            naturalness_avg=Avg('naturalness'),
            overall_avg=Avg('overall'),
            total=Count('pk')
        )
        context.update({'overall': overall})
        context.update({'navlink': 'evaluation_result'})
        return context


class APIView(TemplateView):
    template_name = 'tts/api.html'

    def get_context_data(self, **kwargs):
        context = super(APIView, self).get_context_data(**kwargs)
        context.update({'navlink': 'api', 'sounds': dict(SOUND_OPTIONS), 'host': self.request.get_host()})
        return context


class DownloadView(TemplateView):
    template_name = 'tts/download.html'

    def get_context_data(self, **kwargs):
        context = super(DownloadView, self).get_context_data(**kwargs)
        context.update({'navlink': 'download'})
        return context


def test_view(request):
    UtilMethods.add_task_in_queue('send_test_mail', countdown=0)
    return HttpResponse('Sent')