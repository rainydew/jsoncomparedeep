#!/usr/bin/env python
# coding: utf-8
from distutils.core import setup
from os import path, chdir, system
from sys import argv

if "upload" in argv:
    chdir("json_compare")
    print("running test")
    assert system("python test_json_compare.py") == 0
    chdir("..")

this_directory = path.abspath(path.dirname(__file__))

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except:
    long_description = ""

setup(
    name='jsoncomparedeep',
    version='1.16',
    description='A recursive json comparison library that handles list orders and fuzzy types',
    author='Rainy Chan',
    author_email='rainydew@qq.com',
    url='https://github.com/rainydew/jsoncomparedeep',
    packages=['json_compare'],
    install_requires=['six>=1.12.0'],
    keywords='json comparison order unicode fuzzy',
    long_description=long_description,
    python_requires=">=2.6, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*"
)
