# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import subprocess
import os
import uuid

from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.http import HttpResponse
from ipware.ip import get_ip
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from tts.models import GeneratedVoice, EvaluationData, Evaluation
from nlp.settings import BASE_DIR, FESTIVALDIR
from django.shortcuts import render

# Create your views here.
from django.views import View
from django.views.generic import TemplateView

from tts.text_processor.processor import get_processed_data


def run_shell_command(command):
    return subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).stdout.read()

#
# class IndexPage(TemplateView):
#     template_name = 'tts/index.html'


class TTSPage(TemplateView):
    template_name = 'tts/introduction.html'

    def get_context_data(self, **kwargs):
        context = super(TTSPage, self).get_context_data(**kwargs)
        context.update({'subtab': 'intro', 'navlink': 'project'})
        return context


class DemoPage(TemplateView):
    template_name = 'tts/demo.html'

    def get_context_data(self, **kwargs):
        context = super(DemoPage, self).get_context_data(**kwargs)
        context.update({'subtab': 'demo', 'navlink': 'project'})
        return context


class GenerateVoice(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(GenerateVoice, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.create_direcories_if_does_not_exist()
        uuid_str = str(uuid.uuid4())
        voice = request.POST.get('voice')
        self.delete_old_generated_voice()
        text_input_file = self.save_input_in_file(request.POST.get('text'), uuid_str)
        generated_voice = self.generate_voice(text_input_file, uuid_str, voice)
        saved_obj = self.save_file_to_db(generated_voice, request.POST.get('text'))
        self.delete_temp_files(text_input_file, generated_voice)
        return render(request, template_name='tts/voice_demo.html', context={'generated': saved_obj})

    def create_direcories_if_does_not_exist(self):
        self.create_directory_by_path(os.path.join(BASE_DIR, 'tmp'))
        self.create_directory_by_path(os.path.join(BASE_DIR, 'tmp', 'input'))
        self.create_directory_by_path(os.path.join(BASE_DIR, 'tmp', 'output'))

    def create_directory_by_path(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    def save_input_in_file(self, txt, uuid_str):
        file_with_path = '%s/input/input_%s.txt' % (os.path.join(BASE_DIR, 'tmp'), uuid_str)
        with open(file_with_path, 'w+') as f:
            txt = get_processed_data(txt)
            f.write(txt.encode('utf8'))
        return file_with_path

    def generate_voice(self, file_with_path, uuid_str, voice):
        output_file = 'out_%s.wav' % uuid_str
        command_data = {
            'path': BASE_DIR,
            'output_file': output_file,
            'input_file': file_with_path,
            'voice': voice
        }
        command = FESTIVALDIR + '/bin/text2wave -o {path}/tmp/output/{output_file} -eval "({voice})" {input_file}'.format(**command_data)
        command_output = run_shell_command(command)
        return '%s/tmp/output/%s' % (BASE_DIR, output_file)

    def save_file_to_db(self, file_path, text):
        file = open(file_path)
        generated_voice = GeneratedVoice.objects.create(
            text=text,
            ip=get_ip(self.request)
        )
        generated_voice.file.save('out.wav', file)
        return generated_voice

    def delete_temp_files(self, input_file, output_file):
        os.remove(input_file)
        os.remove(output_file)

    def delete_old_generated_voice(self):
        GeneratedVoice.objects.filter(ip=get_ip(self.request)).delete()


class EvaluateVoice(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(EvaluateVoice, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        sentences = EvaluationData.objects.all()[:10]
        data = {
            'sentences': sentences,
            'marks': range(1, 6),
            'properties': ['Understandability', 'Naturalness', 'Pleasantness', 'Overall'],
            'subtab': 'evaluate'
        }
        return render(request, template_name='tts/evaluation_form.html', context=data)

    def post(self, request, *args, **kwargs):
        json_data = json.loads(request.POST.get('form'))
        for feedback in json_data:
            feedback.update({'data_id': feedback.get('data')})
            feedback.pop('data', None)
            Evaluation.objects.create(**feedback)
        return HttpResponse("Thanks for evaluating.")


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
        result = EvaluationData.objects.filter(evaluation_of_data__voice=voice).annotate(
            Avg('evaluation_of_data__understandability'), Avg('evaluation_of_data__naturalness'),
            Avg('evaluation_of_data__pleasantness'), Avg('evaluation_of_data__overall'))
        if result:
            data.update({'result': result})
        overall_avg = EvaluationData.objects.filter(evaluation_of_data__voice=voice).aggregate(
            Avg('evaluation_of_data__understandability'), Avg('evaluation_of_data__naturalness'),
            Avg('evaluation_of_data__pleasantness'), Avg('evaluation_of_data__overall'))
        if overall_avg:
            data.update({'overall_result': overall_avg})
        data.update({'voice': voice, 'subtab': 'result'})
        return data

