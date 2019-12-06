from django.core.management.base import BaseCommand
from django.core import management
import importlib

from django_vue_generator.forms import generate_vue_form
from django_vue_generator.utils import vuetify, cd_back, fail, replace_in_file


class Command(BaseCommand):
    help = "Build frontend"

    def add_arguments(self, parser):
        parser.add_argument('--noinput', help="Do not ask for user input", action='store_true')

    def handle(self, *args, **options):
        with cd_back("frontend/"):
            fail("yarn build")
        management.call_command("collectstatic", **options)
