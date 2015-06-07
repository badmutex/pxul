import subprocess


def git_version():
    try:
        revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'])
    except subprocess.CalledProcessError:
        revision = 'unknown'

    return revision.strip()


def write_version_module(version, path):
    from textwrap import dedent
    contents = dedent("""\
    # This file is generated from setup.py
    # DO NOT EDIT BY HAND

    version = "{version}"
    git_version = "{git}"
    full_version = "{version}-{git}"
    """.format(version=version, git=git_version()))

    with open(path, 'w') as fd:
        fd.write(contents)
