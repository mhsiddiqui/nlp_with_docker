import os
import subprocess

from django.db.models import Case, IntegerField
from django.db.models import Sum, Count, Avg
from django.db.models import When
from tts.models import EvaluationRecord, EvaluationResult

from rest_framework import pagination
from rest_framework.response import Response
from urdu_tts.settings import BASE_DIR


class CustomPagination(pagination.LimitOffsetPagination):
    def get_paginated_response(self, data):
        return Response({
            'offset': self.offset,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.count,
            'results': data
        })


class UtilMethods(object):
    @staticmethod
    def create_directory_by_path(path):
        if not os.path.exists(path):
            os.makedirs(path)

    @staticmethod
    def create_temp_directories_if_does_not_exist():
        UtilMethods.create_directory_by_path(os.path.join(BASE_DIR, 'tmp'))
        UtilMethods.create_directory_by_path(os.path.join(BASE_DIR, 'tmp', 'input'))
        UtilMethods.create_directory_by_path(os.path.join(BASE_DIR, 'tmp', 'output'))

    @staticmethod
    def run_shell_command(command):
        return subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).stdout.read()

    @staticmethod
    def evaluation_form_post_processing(*args, **kwargs):
        record = kwargs.get('record')
        results = EvaluationResult.objects.filter(record_id=record)
        for result in results:
            if result.question.type in [1, 2]:
                if result.answer.correct:
                    result.correct = True
                    result.save(add_task=False)
        mos_result = results.aggregate(
            intelligibility=Avg('intelligibility'),
            naturalness=Avg('naturalness'),
            overall=Avg('overall')
        )
        drt_result = results.filter(question__type=1).aggregate(
            total=Count('pk'),
            drt=Sum(Case(
                When(correct=True, then=1),
                default=0,
                output_field=IntegerField()
            ))
        )

        mrt_result = results.filter(question__type=2).aggregate(
            total=Count('pk'),
            mrt=Sum(Case(
                When(correct=True, then=1),
                default=0,
                output_field=IntegerField()
            ))
        )

        record_obj = EvaluationRecord.objects.filter(id=record)
        record_obj.update(**mos_result)
        drt_result = UtilMethods.format_data(drt_result)
        mrt_result = UtilMethods.format_data(mrt_result)
        mdrt = {
            'drt': float(drt_result.get('drt')) / float(drt_result.get('total')),
            'mrt': float(mrt_result.get('mrt')) / float(mrt_result.get('total'))
        }
        record_obj.update(**mdrt)
        record_obj.update(status=3)

    @staticmethod
    def format_data(data):
        tmp = dict()
        for key, val in data.items():
            if key == 'total':
                tmp[key] = val if val != 0 else 1
            else:
                tmp[key] = val if val else 0
        return tmp

