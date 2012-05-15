# -*- coding: utf-8 -*-
"""
pp.auth database model: User

"""
import logging

import sqlalchemy
from sqlalchemy import Column

from pp.common.db import guid
from pp.common.db import Base
from pp.auth import pwtools


def get_log():
    return logging.getLogger('pp.auth.plugins.sql.orm.user_table')


class UserTable(Base):
    """This represents a user stored on the system.
    """
    __tablename__ = 'user'

    id = Column(sqlalchemy.types.String(36), primary_key=True, nullable=False, unique=True)
    username = Column(sqlalchemy.types.String(200), nullable=False, unique=True)
    password_hash = Column(sqlalchemy.types.String(), nullable=False, index=False)
    display_name = Column(sqlalchemy.types.String(), nullable=True, index=True)
    email = Column(sqlalchemy.types.String(), nullable=True, index=False)
    phone = Column(sqlalchemy.types.String(), nullable=True, index=False)

    def __init__(self, username, password=None, password_hash=None, display_name='', email='', phone=''):
        """Create a User instance in the database.

        :param username: This is the user's unique name used to log into the system.

        :param password: This is the plain text password, which will be hashed and stored.

        The plain password is NOT stored.

        :param password_hash: This is the prehashed password to be stored.

        If no password and password_hash is given ValueError will be raised as
        one of the fields must be used.

        :param display_name: The text used instead of the unique username (empty by default).

        :param email: An email address for the user (empty by default).

        :param phone: A phone number the user (empty by default).

        """
        self.id = guid()
        self.username = username

        # One of these must be provided:
        if not password and not password_hash:
            raise ValueError("No password or password_hash provided!")

        # A handy conversion saving the end user from having to do this:
        if password:
            self.password_hash = pwtools.hash_password(password)
        else:
            self.password_hash = password_hash

        self.display_name = display_name
        self.email = email
        self.phone = phone

    def to_dict(self):
        """Convert into a transportable dict.

        :returns: a dict which could be json encoded.

        E.g::

            returned = dict(
                id=self.id,
                username=self.username,
                display_name=self.display_name,
                email=self.email,
                phone=self.phone,
            )

        """
        return dict(
            id=self.id,
            username=self.username,
            display_name=self.display_name,
            password_hash=self.password_hash,
            email=self.email,
            phone=self.phone,
        )

    def validate_password(self, plain_text):
        """Called to validate the given password.

        :param password: This is plain text of the user.

        The password will be hashed and the result compared against
        the stored password_hash.

        This is a convenience wrapper around pwtools.validate_password.

        :returns: True for password is valid.

        """
        return pwtools.validate_password(plain_text, self.password_hash)

    def __repr__(self):
        return "'UserTable <%s>: %s'" % (self.id, self.username)


def init():
    """Called to do the initial metadata set up.
       Returns a list of the tables, mappers and declarative base classes this module implements
    """
    get_log().info("init: begin.")
    declarative_bases = [UserTable]
    tables = []
    mappers = []
    get_log().info("init: done.")
    return (declarative_bases, tables, mappers)


def create():
    """Called to do the table schema creation.
    """
    get_log().info("create: begin.")

    from pp.common.db import session

    user_dict = dict(
        username="admin",
        display_name=u'Andrés Plácido Bolívar',
        email=u'andrés.bolívar@example.com',
        phone="123",
        password="password",
    )

    s = session()
    admin_user = s.add(UserTable(**user_dict))

    # Call any custom creating hooks here
    get_log().info("create: Initial admin user <%s> created OK." % admin_user)


def destroy():
    """Called to do the table schema removeall.
    """
    get_log().warn("destroy: begin.")
    # Call any custom destroy hooks here
    get_log().warn("destroy: done.")


def dump():
    """
    Called to dump the table to the WidgetStore intermediate format so it
    can be translated to another format or backed up.

    """
    # TODO  FinishMe


def load(fieldnames, data):
    """
    Called to load the UserTable intermediate data format into the
    user table.

    Attempt to load all the given data in one go unless there is an
    error, in which case don't load anything and abandon the attempt.

    :params data: This is a list of dicts which are to be loaded into
    the database user table.

    :returns: None

    """
    # TODO FinishMe
