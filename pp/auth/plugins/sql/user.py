# -*- coding: utf-8 -*-
"""
:mod:`user` --- The API-level access for user entries.
===============================================================================

.. module:: pp.auth.user
   :synopsis:
.. moduleauthor:: Your Name Here
.. sectionauthor::  Your Name Here

.. versionadded::

The :mod:`pp.auth.user` module is the public access to the lower database
level.

"""
import logging

# TODO add more imports
#from sqlalchemy import or_
#from sqlalchemy.sql import select

from pp.auth import pwtools
from pp.db import session
from pp.db.utils import generic_has, generic_get, generic_find
from pp.db.utils import generic_update, generic_add, generic_remove

from orm.user_table import UserTable


def get_log(extra=None):
    m = "pp.auth.plugins.sql.user"
    if extra:
        if isinstance(extra, basestring):
            m = "%s.%s" % (m, extra)
    return logging.getLogger(m)


# Username is unique and the common method of account recovery:
has = generic_has(UserTable, 'username')
get = generic_get(UserTable, 'username')

find = generic_find(UserTable)

g_update = generic_update(UserTable)

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
        raise UserPresentError(
            "The username <%s> is present and cannot be added." % username
        )

    log.debug("The username <%s> is not present. OK to add." % username)

    return g_add(**user)


def update(**user):
    """Called to update the details of an exiting user on the system.

    This handles the 'new_password' field before passing on to the
    generic update.

    Only password can be changed at the moment.

    """
    log = get_log('update')

    log.debug("Given user <%s> to update." % user)

    update_data = {}
    current = get(user['username'])

    if "new_password" in user:
        new_password = user['new_password']
        user.pop('new_password')
        # Set the new password hash to store, replacing the current one:
        new_password = pwtools.hash_password(new_password)
        update_data['password_hash'] = new_password

    if "display_name" in user:
        update_data['display_name'] = user['display_name']

    if "new_username" in user:
        new_username = user['new_username']
        if not has(user['new_username']):
            update_data['username'] = new_username
        else:
            raise UserPresentError(
                "Cannot rename to username <%s> as it is used." % new_username
            )

    if "password_hash" in user:
        update_data['password_hash'] = user['password_hash']

    if "email" in user:
        update_data['email'] = user['email']

    if "phone" in user:
        update_data['phone'] = user['phone']

    if "extra" in user:
        # I need to use the special extra property to correct handle conversion
        # to valid JSON that can be stored. Then set the raw field that the
        # low level update will set.
        current.extra = user['extra']
        # should be valid "{}" or "{..data..}" at this point:
        update_data['json_extra'] = current.json_extra

    # commits handled elsewhere:
    update_data['no_commit'] = True

    #print "\n\nupdate_data:\n%s\n\n" % update_data

    g_update(current, **update_data)
    log.debug("<%s> updated OK." % user['username'])

    # Return the updated user details:
    return get(user['username'])


def count():
    """Return the number of users on the system."""
    s = session()
    query = s.query(UserTable)
    return query.count()
