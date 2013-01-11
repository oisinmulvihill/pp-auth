# -*- coding: utf-8 -*-
"""
Setuptools script for pp-auth (pp.auth)

"""
from setuptools import setup, find_packages

Name = 'pp-auth'
ProjectUrl = ""
Version = "1.0.2dev"
Author = ''
AuthorEmail = 'everyone at pythonpro dot co dot uk'
Maintainer = ''
Summary = ' pp-auth '
License = ''
Description = Summary
ShortDescription = Summary

needed = [
    "mock",
    'passlib',
    "pp-db",
    "repoze.who==1.0.19",
    "repoze.what==1.0.9",
    "repoze.what.plugins.ini==0.2.2",
]

test_needed = [
]

test_suite = 'pp.auth.tests'

EagerResources = [
    'pp',
]

# Example including shell script out of scripts dir
ProjectScripts = [
]

PackageData = {
    '': ['*.*'],
}

# Example console script and paster template integration:
EntryPoints = {
}


setup(
    url=ProjectUrl,
    name=Name,
    zip_safe=False,
    version=Version,
    author=Author,
    author_email=AuthorEmail,
    description=ShortDescription,
    long_description=Description,
    classifiers=[
        "Programming Language :: Python",
    ],
    license=License,
    scripts=ProjectScripts,
    install_requires=needed,
    tests_require=test_needed,
    test_suite=test_suite,
    include_package_data=True,
    packages=find_packages(),
    package_data=PackageData,
    eager_resources=EagerResources,
    entry_points=EntryPoints,
    namespace_packages=['pp'],
)
