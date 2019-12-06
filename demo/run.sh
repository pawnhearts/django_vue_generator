#!/usr/bin/env bash
python -m venv venv &&
source venv/bin/activate &&
pip install -r requirements.txt &&
python manage.py migrate &&
python manage.py loaddata demo &&
python manage.py start_frontend &&
grep frontend demo/settings.py || echo "INSTALLED_APPS += ['frontend'] " >>demo/settings.py &&
grep frontend demo/urls.py || (echo "import frontend.urls" && echo "urlpatterns += frontend.urls.urlpatterns") >>demo/urls.py &&
python manage.py build_frontend &&
python manage.py runserver
