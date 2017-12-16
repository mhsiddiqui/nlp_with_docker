from django.conf.urls import url

from tts.views import GenerateVoice, TTSPage, DemoPage, EvaluateVoice, EvaluationResult

urlpatterns = [
    # url(r'^$', IndexPage.as_view()),
    url(r'^$', TTSPage.as_view(), name='tts-page'),
    url(r'^demo/$', DemoPage.as_view(), name='tts-demo'),
    url(r'^generate/voice/$', GenerateVoice.as_view(), name='generate-tts-voice'),
    url(r'^evaluate/voice/$', EvaluateVoice.as_view(), name='evaluate-tts-voice'),
    url(r'^evaluation/result/$', EvaluationResult.as_view(), name='evaluation_result'),
    url(r'^evaluation/result/(?P<voice>[0-9a-zA-Z\-_]+)/$', EvaluationResult.as_view(), name='evaluation_result_by_voice'),
]
