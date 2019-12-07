from contextlib import contextmanager
from subprocess import Popen, PIPE
import os


def vuetify(src):
    try:
        ps = Popen(["vue-beautify"], stdin=PIPE, stdout=PIPE)
        stdout, stderr = ps.communicate(src.encode("utf-8"))
        if ps.wait() == 0:
            return stdout.decode("utf-8")
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        return src


def run(cmd, silent=False):
    if silent:
        cmd = f"{cmd} >/dev/null 2>/dev/null"
    return os.system(cmd) == 0


def fail(cmd, silent=False, msg=None):
    if not run(cmd, silent):
        raise OSError("Failed to run {}".format(cmd) if msg is None else msg)
    return True


def which(cmd, msg=None):
    ps = Popen(["which", cmd], stdout=PIPE, stderr=PIPE)
    stdout, stderr = ps.communicate()
    if ps.wait() == 0:
        return stdout.read().decode("utf-8")
    raise OSError("Failed to run {}".format(cmd) if msg is None else msg)


@contextmanager
def cd_back(path="."):
    old_path = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(old_path)


def replace_in_file(path, placeholder, new_data):
    with open(path, "r") as f:
        text = f.read()
    if new_data not in text:
        text = text.replace(placeholder, f"{placeholder}{new_data}")
        with open(path, "w") as f:
            f.write(text)


def overwrite(path, force=False):
    if (
        not force
        and os.path.exists(path)
        and input(f"File {path} exists. Overwrite y/N? ").lower().strip() != "y"
    ):
        return open(os.devnull, "w")
    else:
        return open(path, "w")


def set_yarn_path():
    yarn_path = ":".join(os.popen("yarn global bin && yarn bin").read().splitlines())
    os.environ["PATH"] = f"{yarn_path}:{os.environ['PATH']}"


class Yarn:
    def __init__(self, use_sudo=False):
        self.use_sudo = use_sudo
        if not run("which vue", True):
            if not run("which yarn", True):
                fail(
                    "which npm", silent=True, msg="Please install yarn or at least npm"
                )
                print(
                    "Yarn not installed! Please install it first with your package-manager.\
                Trying to install it via sudo npm i -g yarn"
                )
                fail("sudo npm i -g yarn")
        yarn_path = ":".join(
            os.popen("yarn global bin && yarn bin").read().splitlines()
        )
        os.environ["PATH"] = f"{yarn_path}:{os.environ['PATH']}"

    def add(self, *packages, globally=False, fail_on_error=False):
        fail_on_error = fail if fail_on_error else run
        packages = " ".join(f'"{package}"' for package in packages)
        if not globally:
            fail_on_error(f"yarn add {packages}")
        else:
            if not run("yarn global list|grep vue-beautify", True):
                if not self.use_sudo:
                    run("mkdir -p ~/.yarn-global")
                    run("yarn config set prefix ~/.yarn-global")
                fail_on_error(
                    f"{'sudo ' if self.use_sudo else ''}yarn global add {packages}"
                )

    def build(self):
        fail("yarn build")
