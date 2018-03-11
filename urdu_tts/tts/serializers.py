import os
import re
import uuid

from django.urls import reverse
from ipware.ip import get_ip
from rest_framework import serializers, response, status
from tts.models import GeneratedVoice, EvaluationRecord, QuestionOption, EvaluationQuestion, VOICE_PROPERTIES, \
    EvaluationResult
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
    email = serializers.CharField(allow_null=False, required=True)
    gender = serializers.CharField(allow_null=False, required=True)
    age = serializers.CharField(allow_null=False, required=True)
    next_url = serializers.SerializerMethodField(read_only=True)

    def get_next_url(self, instance):
        return reverse('evaluation_questions_html')

    def create(self, validated_data):
        record = EvaluationRecord.objects.filter(
            name__iexact=validated_data.get('name'),
            email__iexact=validated_data.get('email'),
            status=1)
        if record.exists():
            record.update(**validated_data)
            record = record.first()
        else:
            record = super(EvaluationRecordSerializer, self).create(validated_data)
        return record

    class Meta:
        model = EvaluationRecord
        fields = ('id', 'name', 'email', 'gender', 'age', 'next_url')


class QuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ('id', 'text',)


class EvaluationQuestionSerializer(serializers.ModelSerializer):
    option = serializers.SerializerMethodField(read_only=True)

    def get_option(self, instance):
        if instance.type in [1, 2]:
            return QuestionOptionSerializer(instance.option.all(), many=True).data
        else:
            final_response = []
            for key, value in dict(VOICE_PROPERTIES).items():
                tmp = {
                    'key': key,
                    'name': value,
                    'options': range(1, 6)
                }
                final_response.append(tmp)
            return final_response

    class Meta:
        model = EvaluationQuestion
        fields = '__all__'


class EvaluationResultBulkCreateSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        record = self.context.get('record')
        form_data = []
        already_processed = []
        for question in validated_data:
            tmp = {
                'record': record,
                'question': question.get('question'),
                'intelligibility': self.get_property_rating('intelligibility', question),
                'naturalness': self.get_property_rating('naturalness', question),
                'overall': self.get_property_rating('overall', question),
                'answer_id': question.get('answer')
            }
            if question.get('question') not in already_processed:
                already_processed.append(question.get('question'))
                form_data.append(EvaluationResult(**tmp))
        return EvaluationResult.objects.bulk_create(form_data)

    def get_property_rating(self, prp, question):
        if int(question.get('type')) == 3:
            req_prop = None
            for prop in question.get('answers'):
                if prop.get('property') == prp:
                    req_prop = prop.get('value')
                    break
            return req_prop
        else:
            return None


class PropertySerializer(serializers.Serializer):
    property = serializers.CharField(max_length=100, allow_null=True, allow_blank=True)
    value = serializers.CharField(max_length=100, allow_null=True, allow_blank=True)


class EvaluationResultSerializer(serializers.ModelSerializer):
    answers = PropertySerializer(many=True)
    answer = serializers.CharField(allow_null=True, allow_blank=True)
    type = serializers.CharField(allow_null=True, allow_blank=True)

    class Meta:
        model = EvaluationResult
        list_serializer_class = EvaluationResultBulkCreateSerializer
        fields = ('question', 'answer', 'answers', 'type')
