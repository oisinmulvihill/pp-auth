# -*- coding: utf-8 -*-
"""
This provides password hashing and validate functions which can be

"""
import os
import hashlib

from passlib.hash import sha512_crypt


SHA1_SALT_LENGTH = len(hashlib.sha1().hexdigest())


def hash_password(plaintext_password):
    """Securely hash the plain text password ready for storage.

    :param plain_password: This is a user meaningful string.

    """
    if isinstance(plaintext_password, unicode):
        password_8bit = plaintext_password.encode('UTF-8')
    else:
        password_8bit = plaintext_password

    #print "hash_password password_8bit: ", password_8bit, type(password_8bit)

    # Salt is ok as sha1 but much stronger sha is going to be used for
    # the actual password.
    salt = hashlib.sha1()
    salt.update(os.urandom(60))

    # hashed = hashlib.sha512()
    # hashed.update(password_8bit + salt.hexdigest())
    # hashed_password = salt.hexdigest() + hashed.hexdigest()

    hashed_password = sha512_crypt.encrypt(password_8bit)

    # Make sure the hased password is an UTF-8 object at the end of the
    # process because SQLAlchemy _wants_ a unicode object for Unicode
    # fields
    if not isinstance(hashed_password, unicode):
        hashed_password = hashed_password.decode('UTF-8')

    return hashed_password


def validate_password(plaintext_password, password_hash):
    """Check the password against existing credentials.

    :param plaintext_password: the password that was provided by the user to
        try and authenticate. This is the clear text version that we will
        need to match against the hashed one in the database.

    :param password_hash: The result of a stored hash_password() to compare to.

    :return: Whether the password is valid.

    """
    if isinstance(plaintext_password, unicode):
        password_8bit = plaintext_password.encode('UTF-8')
    else:
        password_8bit = plaintext_password

    if isinstance(password_hash, unicode):
        password_hash = password_hash.encode('UTF-8')

    #print "validate_password: password_8bit: ", password_8bit, type(password_8bit)

    #hashed = hashlib.sha512()
    #hashed.update(password_8bit + password_hash[:SHA1_SALT_LENGTH])
    #return password_hash[SHA1_SALT_LENGTH:] == hashed.hexdigest()

    return sha512_crypt.verify(password_8bit, password_hash)


def validate_password_hash(pass_hash_one, pass_hash_two):
    """Checks that the first password hash equals the second.

    :returns: True, password ok i.e. one == two (after salt removed).

    """
    if isinstance(pass_hash_one, unicode):
        password_one_8bit = pass_hash_one.encode('UTF-8')
    else:
        password_one_8bit = pass_hash_one

    if isinstance(pass_hash_two, unicode):
        password_two_8bit = pass_hash_two.encode('UTF-8')
    else:
        password_two_8bit = pass_hash_two

    #print "validate_password_hash: password_8bit: ", password_one_8bit, password_two_8bit

    one = password_one_8bit[SHA1_SALT_LENGTH:]
    two = password_two_8bit[SHA1_SALT_LENGTH:]

    #print "Hashes minus salt Equal? %s" % (one == two)

    return (one == two)
