from django.core.management.base import BaseCommand
from django.core import management
import importlib

from django_vue_generator.forms import generate_vue_form
from django_vue_generator.utils import vuetify


class Command(BaseCommand):
    help = "Generate vue form"

    def add_arguments(self, parser):
        parser.add_argument(
            "args",
            metavar="viewset",
            nargs="+",
            help="""ViewSet or serializer class. 
            For example:
            ./manage.py generate_vue_form "myapp.serializers.BookSerializer" > frontend/src/components/BookForm.vue""",
        )

    def handle(self, *args, **options):
        mod, cls = args[0].rsplit(".", 1)
        mod = importlib.import_module(mod)
        obj = getattr(mod, cls)

        res = vuetify(generate_vue_form(obj))
        print(res)
