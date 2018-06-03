#!/usr/bin/env python
from setuptools import setup

setup(
    name='falcon-openapi',
    python_requires='>3.5.0',
    version='0.1.0',
    description='Falcon router to map openapi spec to resources',
    author='Sam Kleiner',
    author_email='sam@skleiner.com',
    url='https://github.com/StoicPerlman/falcon-openapi/',
    download_url = 'https://github.com/StoicPerlman/falcon-openapi/archive/0.1.0.tar.gz',
    keywords = ['falcon', 'openapi', 'api'],
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
