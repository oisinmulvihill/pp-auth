# -*- coding: utf-8 -*-
"""
pp.auth database model: User

"""
import pprint
import logging
import sys

import sqlalchemy
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy.orm import backref
from sqlalchemy.orm import relation
from sqlalchemy.types import String
from sqlalchemy.types import Integer
from sqlalchemy.ext.declarative import declarative_base

from pp.common.db import guid
from pp.common.db import Base
from pp.common.db import session
from pp.auth import pwtools


def get_log():
    return logging.getLogger("pp.auth.orm.user")


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


    def __repr__(self):
        return "'UserTable <%s>: %s'" % (self.id, self.name)



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
    # Call any custom creating hooks here
    get_log().info("create: done.")


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





