import subprocess


def git_version():
    try:
        revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'])
    except subprocess.CalledProcessError:
        revision = 'unknown'

    return revision.strip()[:8]


def git_commit_timestamp():
    try:
        timestamp = subprocess.check_output(['git', 'show', '-s', '--format=%ct', 'HEAD'])
    except subprocess.CalledProcessError:
        timestamp = 'unknown'

    return timestamp.strip()


def write_version_module(version, path):
    from textwrap import dedent
    contents = dedent("""\
    # This file is generated from setup.py
    # DO NOT EDIT BY HAND

    version = "{version}"
    time_version = "{time}"
    git_version = "{git}"
    full_version = version + '-' + time_version + '-' + git_version
    """.format(version=version, time=git_commit_timestamp(), git=git_version()))

    with open(path, 'w') as fd:
        fd.write(contents)
