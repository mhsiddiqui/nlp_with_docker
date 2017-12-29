import os
import uuid

from ipware.ip import get_ip
from rest_framework import serializers
from tts.models import GeneratedVoice
from tts.utils import UtilMethods
from urdu_tts.settings import BASE_DIR, FESTIVALDIR, TTS_COMMAND
from tts.text_processor.processor import get_processed_data


class GeneratedVoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedVoice
        fields = '__all__'

    def is_valid(self, raise_exception=False):
        return super(GeneratedVoiceSerializer, self).is_valid(raise_exception)

    def create(self, validated_data):
        uuid_str = str(uuid.uuid4())
        voice = validated_data.get('voice')
        text = validated_data.get('text')
        text_input_file = self.save_input_in_file(text, uuid_str)
        generated_voice = self.generate_voice(text_input_file, uuid_str, voice)
        saved_obj = self.save_file_to_db(generated_voice, text)
        self.delete_temp_files(text_input_file, generated_voice)
        return saved_obj

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
        command = TTS_COMMAND.format(**command_data)
        command_output = UtilMethods.run_shell_command(command)
        return '%s/tmp/output/%s' % (BASE_DIR, output_file)

    def save_file_to_db(self, file_path, text):
        _file = open(file_path)
        generated_voice = GeneratedVoice.objects.create(
            text=text,
            ip=get_ip(self.request)
        )
        generated_voice.file.save('out.wav', _file)
        return generated_voice

    def delete_temp_files(self, input_file, output_file):
        os.remove(input_file)
        os.remove(output_file)
