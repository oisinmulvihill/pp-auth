"""
:mod:`sql` --- SQL authenticators for repoze.who
================================================

This provides the Authentication and Metadata but not groups and permissions.
The groups and permissions reuse the plain.get_groups_from_config() and
plain.get_permissions_from_config().

.. module:: sql

"""
import logging

from pp.auth import user

import plain


def get_log(extra=None):
    m = 'pp.auth.plugins.plain'
    if extra:
        m = "%s.%s" % (m, extra)
    return logging.getLogger(m)


def register():
    """
    Returns registration info for pp.auth
    """
    return {
        'authenticators': get_auth_from_config,
        'mdproviders': get_auth_from_config,
        'groups': plain.get_groups_from_config,
        'permissions': plain.get_permissions_from_config,
    }


class SQLAuthenticatorMetadataProvider(object):
    """
    This implements a combination of the repose.who IAuthenticatorPlugin
    and IMetadataProvider. It doesn't implement the group and permissions
    which will need to be provided elsewhere.

    """
    def __init__(self):
        """
        """
        self.log = get_log("SQLAuthenticatorMetadataProvider")

    def authenticate(self, environ, identity):
        """
        Check the given auth details and if its ok return the
        userid for the given details.

        See: (IAuthenticatorPlugin)
            http://docs.repoze.org/who/narr.html#writing-an-authenticator-plugin

        :returns: None indicated auth failure.

        """
        self.log.info("authenticate: %r" % identity)
        returned = None

        login = identity['login']
        password = identity['password']

        self.log.info("authenticate: looking for user <%r>" % login)
        u = user.find(username=login)
        if u:
            self.log.info("authenticate: validating password for <%r>" % login)
            #print "user '%s' hpw '%s'" % (user,user['password'])
            if u[0].validate_password(password):
                returned = u[0].username
                self.log.info("authenticate: validated OK <%r>" % returned)
            else:
                self.log.info("authenticate: FAILED")

        else:
            self.log.info("authenticate: no mathcing user")

        return returned

    def add_metadata(self, environ, identity):
        """
        Add the firstname, lastname, name to the identity from
        the user details we recovered from the CSV data.

        See: (IMetadataProvider)
            http://docs.repoze.org/who/narr.html#writing-a-metadata-provider-plugin

        """
        userid = identity.get('repoze.who.userid')
        u = user.find(username=userid)
        if u[0]:
            identity.update(u[0].to_dict())


def get_auth_from_config(settings, prefix="pp.auth.sql."):
    """
    Return a `SQLAuthenticatorMetadataProvider` from a settings dict
    """
    return SQLAuthenticatorMetadataProvider()
