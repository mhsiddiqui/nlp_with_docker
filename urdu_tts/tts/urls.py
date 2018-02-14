from django.conf.urls import url

from tts.views import GenerateVoiceJson, GenerateVoiceHTML, TTSPage, DemoPage, \
    EvaluateVoice, EvaluationResultView, APIView, DownloadView, EvaluationQuestionsView, EvaluationPage, \
    EvaluationQuestionsViewHTML, EvaluationFormSubmit, test_view

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
    url(r'^evaluation/questions/$', EvaluationQuestionsView.as_view(), name='evaluation_questions'),
    url(r'^evaluation/questions/html/$', EvaluationQuestionsViewHTML.as_view(), name='evaluation_questions_html'),
    url(r'^evaluation/form/(?P<form>[0-9a-zA-Z\-_]+)/submit/$', EvaluationFormSubmit.as_view(),
        name='evaluation_form'),
    url(r'^evaluation/result/$', EvaluationResultView.as_view(), name='evaluation_result'),
    # url(r'^evaluation/result/(?P<voice>[0-9a-zA-Z\-_]+)/$',
    #     EvaluationResult.as_view(), name='evaluation_result_by_voice'),
    url('^test/email/$', test_view)
]
