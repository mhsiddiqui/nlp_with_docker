import os
import django
from random import randint, uniform

os.environ["DJANGO_SETTINGS_MODULE"] = "urdu_tts.settings"
django.setup()

from tts.models import EvaluationRecord, AGE
from django.contrib.auth.models import User


def create_dummy_data():
    for i in range(1, 50):
        data = {
            'name': 'User Number %s' % i,
            'email': 'user_%s_email@gmail.com' % i,
            'gender': randint(1, 2),
            'age': dict(AGE).keys()[randint(0, len(dict(AGE).keys()) - 1)],
            'status': 3,
            'mrt': uniform(1, 10),
            'drt': uniform(1, 10),
            'intelligibility': uniform(1, 5),
            'naturalness': uniform(1, 5),
            'overall': uniform(1, 5)
        }
        EvaluationRecord.objects.create(**data)


def create_super_user():
    print 'creating new user'
    if not User.objects.filter(username='admin').exists():
        user = User.objects.create(
            username='admin',
            first_name='admin',
            last_name='user',
            is_staff=True,
            email='admin_user@tts.com',
            is_superuser=True)
        user.set_password('asdf1234')
        user.save()


if __name__ == '__main__':
    create_super_user()
