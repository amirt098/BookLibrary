#!/bin/bash

python manage.py collectstatic --noinput
gunicorn -b 0.0.0.0:8000 --workers 5 runner.wsgi
