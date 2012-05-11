# -*- coding: utf-8 -*-
"""
This tests the password tools
Edward Easton, Oisin Mulvihill
"""
from pp.auth import pwtools


# TODO: add tests with pre-canned results - these tests are mostly pretty meaningless


def test_hash_then_unhash():
    plain_password = "11amcoke"
    hashed_pw = pwtools.hash_password(plain_password)
    assert pwtools.validate_password(plain_password, hashed_pw)


def test_hash_then_unhash_leadingspace():
    plain_password = "  11amcoke"
    hashed_pw = pwtools.hash_password(plain_password)
    assert pwtools.validate_password(plain_password, hashed_pw)


def test_hash_then_unhash_leading_and_trailing_space():
    plain_password = "  11amcoke  "
    hashed_pw = pwtools.hash_password(plain_password)
    assert pwtools.validate_password(plain_password, hashed_pw)


def test_hash_then_unhash_unicode():
    plain_password = u"manÃna123"
    hashed_pw = pwtools.hash_password(plain_password)
    assert pwtools.validate_password(plain_password, hashed_pw)


def test_hash_then_unhash_fail_unicode():
    plain_password = u"manÃna123"
    hashed_pw = pwtools.hash_password(plain_password)
    assert not pwtools.validate_password(u"Àôøôò°", hashed_pw)


def test_hash_then_unhash_fail_unicode_other():
    plain_password = u"manÃna123"
    hashed_pw = pwtools.hash_password(plain_password)
    assert not pwtools.validate_password("not the password", hashed_pw)


def test_verify_hash():
    plain_password = u"manÃna123"
    hashed_pw = pwtools.hash_password(plain_password)
    assert pwtools.validate_password_hash(hashed_pw, hashed_pw)

    plain_password = u"manÃna123"
    hashed_pw = pwtools.hash_password(plain_password)
    assert not pwtools.validate_password_hash(
        pwtools.hash_password("should not validate"), hashed_pw
    )
