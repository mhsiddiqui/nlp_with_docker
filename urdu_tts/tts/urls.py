from django.conf.urls import url

from tts.views import GenerateVoiceJson, GenerateVoiceHTML, TTSPage, DemoPage, \
    EvaluateVoice, EvaluationResult, APIView, DownloadView, EvaluationQuestionsView, EvaluationPage

urlpatterns = [
    # url(r'^$', IndexPage.as_view()),
    url(r'^$', TTSPage.as_view(), name='tts-page'),
    url(r'^demo/$', DemoPage.as_view(), name='tts-demo'),
    url(r'^api/$', APIView.as_view(), name='tts-api'),
    url(r'^download/$', DownloadView.as_view(), name='tts-download'),
    url(r'^generate/voice/$', GenerateVoiceJson.as_view(), name='generate-tts-voice'),
    url(r'^generate/voice/html/$', GenerateVoiceHTML.as_view(), name='generate-tts-voice'),
    url(r'^evaluate/$', EvaluationPage.as_view(), name='evaluate-page'),
    url(r'^evaluation/start/$', EvaluateVoice.as_view(), name='evaluate-tts-voice'),
    url(r'^evaluation/questions/(?P<type>[0-9a-zA-Z\-_]+)/$', EvaluationQuestionsView.as_view(),
        name='evaluation_questions'),
    url(r'^evaluation/result/$', EvaluationResult.as_view(), name='evaluation_result'),
    url(r'^evaluation/result/(?P<voice>[0-9a-zA-Z\-_]+)/$',
        EvaluationResult.as_view(), name='evaluation_result_by_voice'),
]
