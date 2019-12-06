#!/usr/bin/env bash
python -m venv venv &&
source venv/bin/activate &&
pip install -r requirements.txt &&
python manage.py migrate &&
pytohn manage.py loaddata demo &&
python manage.py start_frontend &&
echo "INSTALLED_APPS += ['frontend'] " >>demo/settings.py &&
echo "from frontend import urls" >>demo/urls.py &&
echo "urlpatterns += frontend.urlpatterns" >>demo/urls.py &&
python manage.py build_frontend &&
python manage.py runserver
