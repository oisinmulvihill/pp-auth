# -*- coding: utf-8 -*-
"""
"""
import pytest

from pp.auth import apiaccesstoken


def test_apiaccesstoken():
    """Test the basic usage and calls of the manager.
    """
    username = 'fran'

    secret = apiaccesstoken.Manager.generate_secret()

    man = apiaccesstoken.Manager(secret)

    # Generate an access_token, this needs the master secret set so can't be
    # a class
    payload = dict(username=username, somevar=123)
    access_token = man.generate_access_token(payload)

    # Some time later...

    # Now verify the access token
    man1 = apiaccesstoken.Manager(secret)

    payload = man1.verify_access_token(access_token)

    #print "payload: ", payload

    assert payload['username'] == username
    # Hard coded for the moment as I'm forcing tokens not to expire.
    assert payload['expires'] == 10
    assert payload['somevar'] == 123

    # an invalid token will raise and exception
    with pytest.raises(apiaccesstoken.AccessTokenInvalid):
        man1.verify_access_token("some token I've just made up.")

    # the master secret needs to be the same as that generating secrets:
    with pytest.raises(apiaccesstoken.AccessTokenInvalid):
        man2 = apiaccesstoken.Manager("the wrong secret key")
        man2.verify_access_token(access_token)
