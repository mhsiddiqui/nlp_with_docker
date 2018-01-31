import os
import re
import uuid

from ipware.ip import get_ip
from rest_framework import serializers, response, status
from tts.models import GeneratedVoice, EvaluationRecord, QuestionOption, EvaluationQuestion
from tts.utils import UtilMethods
from urdu_tts.settings import BASE_DIR, TTS_COMMAND, SOUND_OPTIONS
from tts.text_processor.processor import get_processed_data


class GenerateVoiceSerializer(serializers.Serializer):
    voice = serializers.ChoiceField(choices=SOUND_OPTIONS, required=True)
    text = serializers.CharField(max_length=1000, required=True)

    def is_valid(self, raise_exception=False):
        data = self.initial_data
        text = data.get('text')
        if re.search('[a-zA-Z]', text):
            raise serializers.ValidationError('No English Character Allowed')
        return super(GenerateVoiceSerializer, self).is_valid(raise_exception)

    def create(self, validated_data):
        try:
            uuid_str = str(uuid.uuid4())
            voice = validated_data.get('voice')
            text = validated_data.get('text')
            text_input_file = self.save_input_in_file(text, uuid_str)
            generated_voice = self.generate_voice(text_input_file, uuid_str, voice)
        except Exception as e:
            raise serializers.ValidationError(e)
        saved_obj = self.save_file_to_db(generated_voice, text, voice)
        self.delete_temp_files(text_input_file, generated_voice)
        return saved_obj

    def save_input_in_file(self, txt, uuid_str):
        file_with_path = os.path.join(BASE_DIR, 'tmp', 'input', 'input_%s.txt' % uuid_str)
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
        if 'error' in command_output.lower():
            raise serializers.ValidationError(command_output)
        return '%s/tmp/output/%s' % (BASE_DIR, output_file)

    def save_file_to_db(self, file_path, text, voice):
        request = self.context.get('request')
        _file = open(file_path)
        generated_voice = GeneratedVoice.objects.create(
            text=text,
            ip=get_ip(request),
            voice=voice
        )
        generated_voice.file.save('out.wav', _file)
        return generated_voice

    def delete_temp_files(self, input_file, output_file):
        os.remove(input_file)
        os.remove(output_file)


class GeneratedVoiceSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()

    def get_file(self, obj):
        return self.context.get('request').build_absolute_uri(obj.file.url)

    class Meta:
        model = GeneratedVoice
        fields = '__all__'


class EvaluationRecordSerializer(serializers.ModelSerializer):
    gender = serializers.CharField(allow_null=False, required=True)
    age = serializers.CharField(allow_null=False, required=True)

    class Meta:
        model = EvaluationRecord
        fields = ('id', 'name', 'email', 'gender', 'age')


class QuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ('text',)


class EvaluationQuestionSerializer(serializers.ModelSerializer):
    option = QuestionOptionSerializer(read_only=True, many=True)

    class Meta:
        model = EvaluationQuestion
        fields = '__all__'
