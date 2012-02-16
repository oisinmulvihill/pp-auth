# -*- coding: utf-8 -*-
"""
:mod:`user` --- The API-level access for user entries.
==================================================================================

.. module:: pp.auth.user
   :synopsis:
.. moduleauthor:: Your Name Here
.. sectionauthor::  Your Name Here

.. versionadded::

The :mod:`pp.auth.user` module is the public access to the lower database level.

No access to the :mod:`pp.auth.orm.user` should be allowed outside of testing.
The majority / all of the business logic should be here and not in the database
module. Breaking this rule is bad and introduces tight coupling which degrades the
agility of the code. Don't do it or I'll find you...

"""
import logging

# TODO add more imports
from sqlalchemy import or_
from sqlalchemy.sql import select

from pp.common.db import session
from pp.common.db.utils import generic_has, generic_get, generic_find, generic_update, generic_add, generic_remove

from pp.auth.orm.user_table import UserTable


def get_log():
    return logging.getLogger('pp.auth.user')

# Simple case of all objects being  referenced by their ids
has = generic_has(UserTable)
get = generic_get(UserTable)
find = generic_find(UserTable)
update = generic_update(UserTable)
add = generic_add(UserTable)
remove = generic_remove(UserTable)


def count():
    """
    Example method showing session simple read handling
    """
    s = session()
    query = s.query(UserTable)
    return query.count()


def transform(attr_name, transformer):
    """
    Example method showing commits
    """
    s = session()
    query = s.query(UserTable)
    for item in query.all():
        # Recover an attribute
        attr = getattr(item, attr_name)

        # Transform it and set it back on the object
        setattr(item, attr_name, transformer(attr))

    # Commit the changes
    query.commit()

