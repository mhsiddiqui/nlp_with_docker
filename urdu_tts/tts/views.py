# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.http import HttpResponse
from ipware.ip import get_ip
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, response, status, renderers

from tts.models import GeneratedVoice, QUESTION_TYPE, EvaluationQuestion
from tts.serializers import GeneratedVoiceSerializer, GenerateVoiceSerializer, EvaluationRecordSerializer, \
    EvaluationQuestionSerializer
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
        question_type = kwargs.get('type')
        if int(question_type) not in dict(QUESTION_TYPE).keys():
            return response.Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            questions = EvaluationQuestion.objects.filter(type=question_type).order_by('id')
            serializer = self.get_serializer(questions, many=True)
            return response.Response(data=serializer.data)


class EvaluationResult(View):

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(EvaluationResult, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        voice = kwargs.get('voice', 'voice_pucit_indic_ur_cg')
        data = self.get_evaluation_result_by_voice(voice)
        return render(request, template_name='tts/evaluation_result.html', context=data)

    def get_evaluation_result_by_voice(self, voice):
        data = {}
        # result = EvaluationData.objects.filter(evaluation_of_data__voice=voice).annotate(
        #     Avg('evaluation_of_data__understandability'), Avg('evaluation_of_data__naturalness'),
        #     Avg('evaluation_of_data__pleasantness'), Avg('evaluation_of_data__overall'))
        # if result:
        #     data.update({'result': result})
        # overall_avg = EvaluationData.objects.filter(evaluation_of_data__voice=voice).aggregate(
        #     Avg('evaluation_of_data__understandability'), Avg('evaluation_of_data__naturalness'),
        #     Avg('evaluation_of_data__pleasantness'), Avg('evaluation_of_data__overall'))
        # if overall_avg:
        #     data.update({'overall_result': overall_avg})
        # data.update({'voice': voice, 'subtab': 'result'})
        return data


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
