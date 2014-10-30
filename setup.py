# -*- coding: utf-8 -*-
"""
"""
from setuptools import setup, find_packages

Name = 'pp-auth'
ProjectUrl = ""
Version = "1.0.2"
Author = 'Edward Easton, Oisin Mulvihill'
AuthorEmail = 'oisin mulvihill gmail '
Maintainer = ''
Summary = 'Authorization and Authentication modules.'
License = ''
Description = Summary
ShortDescription = Summary

needed = [
    "mock",
    "passlib",
    "pyparsing==1.5.7",
    "pp-db",
    "tokenlib",
    "repoze.who==1.0.19",
    "repoze.what==1.0.9",
    "repoze.what.plugins.ini==0.2.2",
]

test_needed = [
    "pytest-cov",
]

test_suite = 'pp.auth.tests'

EagerResources = [
    'pp',
]

ProjectScripts = [
]

PackageData = {
    '': ['*.*'],
}

EntryPoints = """
"""

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
        "Topic :: Software Development :: Libraries",
    ],
    keywords='python',
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

