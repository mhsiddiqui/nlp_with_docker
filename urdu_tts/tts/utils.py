import os
import subprocess
from urdu_tts.settings import BASE_DIR, FESTIVALDIR


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
