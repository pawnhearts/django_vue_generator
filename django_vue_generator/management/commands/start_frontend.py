import os

from django.core.management.base import BaseCommand
from django.core import management
from django.conf import settings

from django_vue_generator.utils import (
    vuetify,
    run,
    fail,
    cd_back,
    replace_in_file,
    overwrite,
)
from django_vue_generator.forms import generate_vue_form


def prepare():
    with cd_back():
        if not run("which vue", True):
            if not run("which yarn", True):
                fail(
                    "which npm", silent=True, msg="Please install yarn or at least npm"
                )
                fail("npm i -g yarn")
        fail(r"yarn global list|grep vue\/cli || yarn global add @vue/cli")
        run("yarn global list|grep vue-beautify || yarn global add vue-beautify js-beautify")
        yarn_path = ':'.join(os.popen('yarn global bin && yarn bin').read().splitlines())
        os.environ['PATH'] = f"{yarn_path}:{os.environ['PATH']}"
        fail("vue create -m yarn -n -p default frontend")
    with cd_back("frontend/"):
        run("yarn add vuelidate")
        run("yarn add vue-resource")
        replace_in_file(
            "src/main.js",
            "import Vue from 'vue'",
            """\nimport Vuelidate from 'vuelidate'\nVue.use(Vuelidate)\n""",
        )
        replace_in_file(
            "src/main.js",
            "import Vue from 'vue'",
            """\nimport VueResource from 'vue-resource'\nVue.use(VueResource)\n""",
        )
        replace_in_file(
            "package.json",
            'vue-cli-service build',
            r""" && (rm -rf static/frontend/ 2>/dev/null || true) && sed 's/href=\//href=\/static\//g' dist/index.html > templates/frontend/index.html && mv dist static/frontend""",
        )
        run("touch __init__.py")
        run("mkdir -p templates/frontend")
        run("mkdir -p static/frontend")
        with overwrite("templates/index.html") as f:
            f.write("""Please run ./manage.py build_frontend""")
        with overwrite("urls.py") as f:
            f.write(
                """from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='frontend/index.html'), name='frontend-index'),
]
"""
            )
    print(
        "don't forget to add 'frontend' to INSTALLED_APPS and include frontend.urls to your urlpatterns"
    )
    print("next you should run ./manage.py build_frontend")
    print("or 'cd frontend && yarn build && cd .. && ./manage.py collectstatic'")


# def apis():
#     yield ''
#     from django.urls import get_resolver
#     for func, url in get_resolver().reverse_dict.items():
#         try:
#             func = func
#             url = url[0][0][0]
#             for method, action in getattr(func, 'actions', {}).items():
#                 params = func.cls.lookup_field if action == 'retrieve' else 'params'
#
#                 yield f"""{func.initkwargs['basename']}_{action}: ({params}) => {{
#                     this.$http.{method}('{url}').then(r => {{
#                        alert(r)
#                     }},
#                     """
#         except:
#             pass
class Command(BaseCommand):
    help = "Generate vue frontend"

    def handle(self, *args, **options):
        prepare()
        from rest_framework.viewsets import ModelViewSet

        for viewset in ModelViewSet.__subclasses__():
            name = viewset().get_serializer_class().Meta.model._meta.model_name.title()
            code = vuetify(generate_vue_form(viewset))
            path = f"frontend/src/components/{name}.vue"
            with overwrite(path) as f:
                f.write(code)
