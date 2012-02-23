# -*- coding: utf-8 -*-
"""
This tests the product table methods
Edward Easton, Oisin Mulvihill
"""
import pprint
import unittest
import datetime

from pp.common.db import session, dbsetup
from pp.common.db import utils

from pp.auth import user
from pp.auth import pwtools


class UserTC(unittest.TestCase):

    def setUp(self):
        """Set up the schema clean ready to load test data into for each test.
        """
        # This needs to be autogenerate or manage not to interfere with other
        # test runs that may occur simultaneously.
        #
        #dbsetup.init("sqlite:///testdata.db")
        #
        # Stick with in memory for the moment:
        dbsetup.init("sqlite:///:memory:")

        dbsetup.create()

        # Used so I can manipulate object returned from api,
        # binding them to my session. Otherwise the internal
        # session used is closed, and normally this would be
        # ok.
        self.session = session()


    def tearDown(self):
        """I don't really bother cleaning up after a test as it useful to aid test debugging,
        if you use a real database and need to check state after a single test run.
        """
        self.session.close()


    def test_password_tools(self):
        """Test the password tools available in pwtools module.
        """
        # Success
        plain_password = "11amcoke"
        hashed_pw = pwtools.hash_password(plain_password)
        self.assertTrue(pwtools.validate_password(plain_password, hashed_pw))

        plain_password = "  11amcoke"
        hashed_pw = pwtools.hash_password(plain_password)
        self.assertTrue(pwtools.validate_password(plain_password, hashed_pw))

        plain_password = "  11amcoke  "
        hashed_pw = pwtools.hash_password(plain_password)
        self.assertTrue(pwtools.validate_password(plain_password, hashed_pw))

        plain_password = u"manÃna123"
        hashed_pw = pwtools.hash_password(plain_password)
        self.assertTrue(pwtools.validate_password(plain_password, hashed_pw))

        # Fail
        plain_password = u"manÃna123"
        hashed_pw = pwtools.hash_password(plain_password)
        self.assertFalse(pwtools.validate_password(u"Àôøôò°", hashed_pw))

        plain_password = u"manÃna123"
        hashed_pw = pwtools.hash_password(plain_password)
        self.assertFalse(pwtools.validate_password("not the password", hashed_pw))


    def testBasicCRUD(self):
        """Test the basic add and get method
        """
        username = 'bob.sprocket'

        self.assertEquals(user.count(), 0)

        self.assertEquals(user.find(username=username), [])

        # Test I cannot add a user if I don't provide either a
        # password or a password_hash
        #
        user_dict = dict(
            username=username,
            # Not provied password or password hash
            #password='1234567890',
        )
        self.assertRaises(ValueError, user.add, **user_dict)

        plain_pw = '1234567890'

        user_dict = dict(
            username=username,
            password=plain_pw,
            display_name='Bob Sprocket',
            email='bob.sprocket@example.com',
            phone='9876543210'
        )
        item1 = user.add(**user_dict)

        # Check the password is converted into a hashed password correctly:
        is_validate = pwtools.validate_password(plain_pw, item1.password_hash)
        self.assertTrue(is_validate)

        # Check the convenience method on the user instance:
        is_validate = item1.validate_password(plain_pw)
        self.assertTrue(is_validate)

        # Make sure I cannot add the same username again:
        self.assertRaises(user.UserPresentError, user.add, **user_dict)

        self.assertEquals(user.find(username=username), [item1,])
        self.assertEquals(user.has(username), True)
        self.assertEquals(user.count(), 1)

        item2 = user.get(username)

        self.assertEquals(item2.username, user_dict['username'])
        self.assertEquals(item2.display_name, user_dict['display_name'])
        self.assertEquals(item2.email, user_dict['email'])
        self.assertEquals(item2.phone, user_dict['phone'])

        user.remove(item2.id)    # remove just by id

        self.assertEquals(user.count(), 0)

        self.assertEquals(user.has(item2.id), False)

        self.assertRaises(utils.DBRemoveError, user.remove, item2.id)

