from django.core.mail import EmailMultiAlternatives
from django.db.models import Case, IntegerField
from django.db.models import Sum, Count, Avg
from django.db.models import When
from urdu_tts.celery import app
from tts.models import EvaluationRecord, EvaluationResult


@app.task
def evaluation_form_post_processing(*args, **kwargs):
    record = kwargs.get('record')
    results = EvaluationResult.objects.filter(record_id=record)
    for result in results:
        if result.question.type in [1, 2]:
            if result.answer.correct:
                result.correct = True
                result.save()
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
    mdrt = {
        'drt': float(drt_result.get('drt'))/float(drt_result.get('total')),
        'mrt': float(mrt_result.get('mrt'))/float(drt_result.get('total'))
    }
    record_obj.update(**mdrt)

@app.task
def send_test_mail(*args, **kwargs):
    html_content = '<html><body>%s</body></html>'
    tbl = '<table>'
    for i in range(1, 1000):
        tbl += '<tr><td>%s</td></tr>' % i
    tbl += '</table>'
    html_content = html_content % tbl
    msg = EmailMultiAlternatives('Subject here', html_content, 'mamoona.qayyum@fiveriverstech.com ',
                                 ['mhassan.eeng@gmail.com'], )
    msg.attach_alternative(html_content, "text/html")
    msg.send()
