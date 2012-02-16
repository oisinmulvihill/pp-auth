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
        dbsetup.init("sqlite:///testdata.db")
        #dbsetup.init("sqlite:///:memory:")
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
        print "hashed_pw: ", hashed_pw, type(hashed_pw)
        self.assertTrue(pwtools.validate_password(plain_password, hashed_pw))

        # Fail
        plain_password = u"manÃna123"
        hashed_pw = pwtools.hash_password(plain_password)
        self.assertTrue(pwtools.validate_password(u"Àôøôò°", hashed_pw))

        plain_password = u"manÃna123"
        hashed_pw = pwtools.hash_password(plain_password)
        self.assertTrue(pwtools.validate_password("not the password", hashed_pw))


    def testBasicCRUD(self):
        """Test the basic add and get method
        """
        self.assertEquals(user.count(), 0)

        self.assertEquals(user.find(username='bob.sprocket'), [])

        user_dict = dict(
            username='bob.sprocket',
            password='1234567890',
            display_name='Bob Sprocket',
            email='bob.sprocket@example.com',
            phone='9876543210'
        )
        item1 = user.add(**user_dict)

        self.assertRaises(utils.DBAddError, user.add, **user_dict)

        self.assertEquals(user.find(name='foobar'), [item1,])

        self.assertEquals(user.has(item1.id), True)

        self.assertEquals(user.count(), 1)

        user_bob = user.get(username='bob.sprocket')

        self.assertEquals(item2.username, user_dict['username'])
        self.assertEquals(item2.password_hash, user_dict[''])
        self.assertEquals(item2.display_name, user_dict[''])
        self.assertEquals(item2.email, user_dict[''])
        self.assertEquals(item2.phone, user_dict[''])

        user.remove(item2.id)    # remove just by id

        self.assertEquals(user.count(), 0)

        self.assertEquals(user.has(item2.id), False)

        self.assertRaises(utils.DBRemoveError, user.remove, item2.id)
