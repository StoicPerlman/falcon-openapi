#!/usr/bin/env python
import os
from setuptools import setup

readme_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'README.md')
try:
    from m2r import parse_from_file
    readme = parse_from_file(readme_file)
except ImportError:
    # m2r may not be installed in user environment
    with open(readme_file) as f:
        readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='falcon-openapi',
    python_requires='>3.5.0',
    version='0.1.5',
    description='Falcon router to map openapi spec to resources',
    long_description=readme,
    long_description_content_type="text/markdown",
    author='Sam Kleiner',
    author_email='sam@skleiner.com',
    license=license,
    url='https://github.com/StoicPerlman/falcon-openapi/',
    download_url = 'https://github.com/StoicPerlman/falcon-openapi/archive/0.1.5.tar.gz',
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
