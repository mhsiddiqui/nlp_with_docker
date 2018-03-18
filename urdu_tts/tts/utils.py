import os
import subprocess

from django.db import transaction
from rest_framework import pagination
from rest_framework.response import Response
from urdu_tts.settings import BASE_DIR, DEBUG
import tts.tasks as tasks


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
    def add_task_in_queue(task_name, countdown=30, *args, **kwargs):
        """
        Start a background task. If local env, then run it in normal way for debugging
        You should import tasks first in tasks/__init__.py
        :param task_name: task name in string
        :param countdown: delay in execution of task
        :param args:
        :param kwargs:
        """
        task_function = getattr(tasks, task_name)
        return task_function(*args, **kwargs)
        # if DEBUG:
        #     return task_function(*args, **kwargs)
        # else:
        #     transaction.on_commit(
        #         lambda: getattr(task_function, 'apply_async')(args=args, kwargs=kwargs, countdown=countdown))
        #     return 'Task Added'
        # transaction.on_commit(
        #         lambda: getattr(task_function, 'apply_async')(args=args, kwargs=kwargs, countdown=countdown))
        # return 'Task Added'
