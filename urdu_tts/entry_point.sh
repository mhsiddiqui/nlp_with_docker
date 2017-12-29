#!/bin/sh
kill -KILL $(lsof -t -i tcp:8001)
python manage.py migrate
exec "$@"