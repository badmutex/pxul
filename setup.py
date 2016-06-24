# from ez_setup import use_setuptools
# use_setuptools()
from setuptools import setup, find_packages
from setup_util import write_version_module

VERSION = '3.0.0'

write_version_module(VERSION, 'pxul/version.py')

setup(
    name = 'pxul',
    version = VERSION,
    packages = find_packages(),
    author = "Badi' Abdul-Wahid",
    author_email = 'abdulwahidc@gmail.com',
    description = 'A collection of Python extras and utilities',
    license = 'GPLv2',
    url='https://github.com/badi/pxul'
    )
