#!/usr/bin/env python
from setuptools import setup

with open("README.md") as f:
    readme = f.read()

setup(
    name="falcon-openapi",
    python_requires=">3.5.0",
    version="0.5.1",
    description="Falcon router to map openapi spec to resources",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Sam Kleiner",
    author_email="sam@skleiner.com",
    license="MIT",
    url="https://github.com/StoicPerlman/falcon-openapi/",
    keywords=["falcon", "openapi", "api"],
    packages=["falcon_openapi"],
    install_requires=["falcon", "pyyaml"],
)
