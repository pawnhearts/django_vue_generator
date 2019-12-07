#!/usr/bin/env bash
echo "use ./run.sh --sudo to install vue/cli etc globally otherwise it would try to install it into ~/.yarn-global"
python -m venv venv &&
source venv/bin/activate &&
pip install -r requirements.txt &&
python manage.py migrate &&
python manage.py loaddata demo &&
python manage.py start_frontend $1 &&
(grep frontend demo/settings.py || echo "INSTALLED_APPS += ['frontend'] " >>demo/settings.py) &&
(grep frontend demo/urls.py || (echo "import frontend.urls" && echo "urlpatterns = frontend.urls.urlpatterns + urlpatterns") >>demo/urls.py) &&
cp DemoApp.vue frontend/src/App.vue &&
python manage.py build_frontend &&
python manage.py runserver
