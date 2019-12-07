from django.core.management.base import BaseCommand
from django.core import management
import importlib

from django_vue_generator.forms import FormGenerator
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
        parser.add_argument(
            "--write", help="Write to file insted of stdout", action="store_true"
        )

    def handle(self, *args, **options):
        mod, cls = args[0].rsplit(".", 1)
        mod = importlib.import_module(mod)
        obj = getattr(mod, cls)
        generator = FormGenerator(obj)
        if options["write"]:
            with open(generator.filename, "w") as f:
                f.write(generator.render())
        else:
            print(generator.render())
