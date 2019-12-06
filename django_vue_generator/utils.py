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
        text = text.replace(placeholder, f"{placeholder}{new_data.strip()}")
        with open(path, "w") as f:
            f.write(text)


def overwrite(path):
    if os.path.exists(path) and input(f"File {path} exists. Overwrite y/n?") != "y":
        return open(os.devnull, "w")
    else:
        return open(path, "w")
