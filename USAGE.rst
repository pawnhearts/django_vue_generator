add "django_vue_generator" to INSTALLED_APPS.

run "./manage.py start_frontend" that would create "frontend" directory with vue stuff and also urls.py, static/ templates/ folders. So it also acts as a django app.

run "./manage.py build_frontend" to build vue project and create template.
(same result could be achieved by running "yarn build" in frontend directory and then "./manage.py collectstatic").

Add "frontend" to INSTALLED_APPS and include frontend.urls.urlpatterns to your urls.

There are also generate_vue_form generate_vue_list management commands.

tl;dr - see demo django project in demo/ directory and it's run.sh