#!/usr/bin/env python
# coding: utf-8
from distutils.core import setup
from os import path
this_directory = path.abspath(path.dirname(__file__))

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except:
    long_description = ""

setup(
    name='jsoncomparedeep',
    version='1.15',
    description='A recursive json comparison library that handles list orders and fuzzy types',
    author='Rainy Chan',
    author_email='rainydew@qq.com',
    url='https://rainydew.blog.csdn.net/article/details/93904318',
    packages=['json_compare'],
    install_requires=['six>=1.12.0'],
    keywords='json comparison order unicode fuzzy',
    long_description=long_description,
    python_requires=">=2.6, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*"
)
