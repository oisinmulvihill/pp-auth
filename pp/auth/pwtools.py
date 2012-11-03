# -*- coding: utf-8 -*-
"""
This provides password hashing and validate functions which can be

This uses passlib.hash sha512_crypt to implement strong passord hashing rather
then some home brew approach.

"""
from passlib.hash import sha512_crypt


def hash_password(plaintext_password):
    """Securely hash the plain text password ready for storage.

    :param plain_password: This is a user meaningful string.

    """
    if isinstance(plaintext_password, unicode):
        password_8bit = plaintext_password.encode('UTF-8')
    else:
        password_8bit = plaintext_password

    # Use password lib strong hashing rather then home brew:
    hashed_password = sha512_crypt.encrypt(password_8bit)

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

    return sha512_crypt.verify(password_8bit, password_hash)
