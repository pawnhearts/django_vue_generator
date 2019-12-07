add "django_vue_generator" to INSTALLED_APPS.

run "./manage.py start_frontend" that would create "frontend" directory with vue stuff and also urls.py, static/ templates/ folders. So it also acts as a django app.

run "./manage.py build_frontend" to build vue project and create template.

Add "frontend" to INSTALLED_APPS and include frontend.urls.urlpatterns to your urls.

tl;dr - see demo django project in demo/ directory and it's run.sh