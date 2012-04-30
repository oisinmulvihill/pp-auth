# -*- coding: utf-8 -*-
"""
pp-auth

pp.auth

PythonPro Limited
Created: 2012-02-16T16:14:38

"""


def commondb_setup():
    """
    Returns all the commondb modules and mappers this package provides
    """
    import orm.user_table
    return {'modules': [orm.user_table], 'mappers': []}
