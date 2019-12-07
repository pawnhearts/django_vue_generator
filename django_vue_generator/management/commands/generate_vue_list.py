from django.core.management.base import BaseCommand
from django.core import management
import importlib

from django_vue_generator.lists import ListGenerator

TAG_PARAMS = ["table", "row", "column", "header"]


class Command(BaseCommand):
    help = "Generate vue list"

    def add_arguments(self, parser):
        parser.add_argument(
            "args",
            metavar="viewset",
            nargs="+",
            help="""ViewSet. 
            For example:
            ./manage.py generate_vue_form "app.views.BookViewSet" > frontend/src/components/BookList.vue""",
        )
        for k in TAG_PARAMS:
            parser.add_argument(f"--{k}-tag", type=str, default="")
        parser.add_argument(
            "--write", help="Write to file insted of stdout", action="store_true"
        )

    def handle(self, *args, **options):
        mod, cls = args[0].rsplit(".", 1)
        mod = importlib.import_module(mod)
        obj = getattr(mod, cls)
        kwargs = {
            f"{k}_tag": options[f"{k}-tag"]
            for k in TAG_PARAMS
            if options.get(f"{k}-tag", "")
        }
        generator = ListGenerator(obj, **kwargs)
        if options["write"]:
            with open(generator.filename, "w") as f:
                f.write(generator.render())
        else:
            print(generator.render())
