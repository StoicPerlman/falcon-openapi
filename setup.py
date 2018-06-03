#!/usr/bin/env python
from setuptools import setup

setup(
    name='Falcon OpenApi',
    version='0.1.0',
    description='Falcon router to map openapi spec to resources',
    author='Sam Kleiner',
    author_email='sam@skleiner.com',
    url='https://github.com/StoicPerlman/falcon-openapi/',
    packages=['falcon_openapi'],
    install_requires=[
        'falcon',
        'pyyaml'
    ],
    extras_require={
        'dev': [
            'unittest'
        ]
    }
)
