from django.core.management.base import BaseCommand
from django.core import management
import importlib

from django_vue_generator.forms import generate_vue_form
from django_vue_generator.utils import (
    vuetify,
    cd_back,
    fail,
    replace_in_file,
    set_yarn_path,
)


class Command(BaseCommand):
    help = "Build frontend"

    def handle(self, *args, **options):
        set_yarn_path()
        with cd_back("frontend/"):
            fail("yarn build")
        management.call_command("collectstatic")
