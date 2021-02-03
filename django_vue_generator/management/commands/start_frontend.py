import os

from django.core.management.base import BaseCommand
from django.core import management
from django.conf import settings

from django_vue_generator.lists import ListGenerator
from django_vue_generator.utils import (
    vuetify,
    run,
    fail,
    cd_back,
    replace_in_file,
    overwrite,
    set_yarn_path,
)
from django_vue_generator.forms import VueForm

ESLINT_CONFIG = """{
    "env": {
        "browser": true,
        "es6": true
    },
    "extends": [
        "eslint:recommended",
        "plugin:vue/essential"
    ],
    "globals": {
        "Atomics": "readonly",
        "SharedArrayBuffer": "readonly"
    },
    "parserOptions": {
        "ecmaVersion": 2018,
        "sourceType": "module"
    },
    "plugins": [
        "vue"
    ],
    "rules": {
        "no-unused-vars": "off"
    }
}"""

URLS = """from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='frontend/index.html'), name='frontend-index'),
]
"""

WEBPACK_CONFIG = """import webpack from 'webpack';

// Try the environment variable, otherwise use static
const ASSET_PATH = process.env.ASSET_PATH || '/static/frontend/';

export default {
  output: {
    publicPath: ASSET_PATH,
  },

  plugins: [
    // This makes it possible for us to safely use env vars on our code
    new webpack.DefinePlugin({
      'process.env.ASSET_PATH': JSON.stringify(ASSET_PATH),
    }),
  ],
};"""


def prepare(force=False, sudo=False):
    with cd_back():
        if not run("which vue", True) and not run("which yarn", True):
            fail(
                "which npm", silent=True, msg="Please install yarn or at least npm"
            )
            print(
                "Yarn not installed! Please install it first with your package-manager.\
                Trying to install it via sudo npm i -g yarn"
            )
            fail("sudo npm i -g yarn")
        if not run(r"yarn global list|grep vue\/cli", True):
            if not sudo:
                run("mkdir -p ~/.yarn-global")
                run("yarn config set prefix ~/.yarn-global")
            fail(f"{'sudo ' if sudo else ''}yarn global add @vue/cli")
        if not run("yarn global list|grep vue-beautify", True):
            if not sudo:
                run("mkdir -p ~/.yarn-global")
                run("yarn config set prefix ~/.yarn-global")
            run(f"{'sudo ' if sudo else ''}yarn global add vue-beautify js-beautify")
        set_yarn_path()
        fail(f"vue create -m yarn -n -p default frontend{' -f' if force else ''}")
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
            "vue-cli-service build",
            r""" && (rm -rf static/frontend/ 2>/dev/null || true) && sed 's/=\\//=\\/static\\/frontend\\//g' dist/index.html > templates/frontend/index.html && mv dist static/frontend""",
        )
        run("touch __init__.py")
        run("mkdir -p templates/frontend")
        run("mkdir -p static/frontend")
        with overwrite(".eslintrc.json", force) as f:
            f.write(ESLINT_CONFIG)
        # with overwrite('webpack.config.js', force) as f:
        #     f.write(WEBPACK_CONFIG)
        with overwrite("templates/index.html", force) as f:
            f.write("""Please run ./manage.py build_frontend""")
        with overwrite("urls.py", force) as f:
            f.write(URLS)
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

    def add_arguments(self, parser):
        parser.add_argument("--force", help="Overwrite everything", action="store_true")
        parser.add_argument(
            "--sudo",
            help="Use sudo to install global packages(like vue-cli).\
            Otherwise it would try to install them into ~/.yarn-global/",
            action="store_true",
        )

    def handle(self, *args, **options):
        prepare(options["force"], options["sudo"])
        from rest_framework.viewsets import ModelViewSet

        for viewset in ModelViewSet.__subclasses__():
            name = viewset().get_serializer_class().Meta.model._meta.model_name.title()
            for GeneratorClass in [VueForm, ListGenerator]:
                generator = GeneratorClass(viewset)
                with overwrite(generator.filename) as f:
                    f.write(generator.render())
