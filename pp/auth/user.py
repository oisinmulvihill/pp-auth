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


def get_log(fn=''):
    if fn:
        fn = ".%s" % fn
    return logging.getLogger('pp.auth.user%s' % fn)


# Username is unique and the common method of account recovery:
has = generic_has(UserTable, 'username')
get = generic_get(UserTable, 'username')

find = generic_find(UserTable)

update = generic_update(UserTable)

remove = generic_remove(UserTable)


class UserPresentError(Exception):
    """Raised by add when an existing username conflicts with the new one."""


# Used by add after performing checks:
g_add = generic_add(UserTable)


def add(**user):
    """Called to add a new user to the system.

    :param user: This is a dict of fields a user_table.UserTable() can accept.

    The username must not be present in the system already. if
    it is then UserPresentError will be raised.

    :returns: A new instance of user_table.UserTable.

    """
    log = get_log('add')

    log.debug("Given user <%s> to add." % user)
    username = user['username']

    if has(username):
        raise UserPresentError("The username <%s> is present and cannot be added again." % username)

    log.debug("The username <%s> is not present already. OK to add." % username)

    return g_add(**user)


def count():
    """Return the number of users on the system."""
    s = session()
    query = s.query(UserTable)
    return query.count()


# to remove
#
# def transform(attr_name, transformer):
#     """
#     Example method showing commits
#     """
#     s = session()
#     query = s.query(UserTable)
#     for item in query.all():
#         # Recover an attribute
#         attr = getattr(item, attr_name)

#         # Transform it and set it back on the object
#         setattr(item, attr_name, transformer(attr))

#     # Commit the changes
#     query.commit()

