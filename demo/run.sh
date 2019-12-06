#!/usr/bin/env bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py start_frontend
python manage.py build_frontend
pytohn manage.py loaddata demo
python manage.py runserver
