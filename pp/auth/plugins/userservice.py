"""

"""
import os
import logging
import StringIO

from repoze.what.plugins.ini import INIGroupAdapter
from repoze.what.plugins.ini import INIPermissionsAdapter

from pp.auth import pwtools
from pp.user.client import rest

def get_log(extra=None):
    m = "pp.auth.plugins.userservice"
    if extra:
        if isinstance(extra, basestring):
            m = "%s.%s" % (m, extra)
    return logging.getLogger(m)



def register():
    """
    Returns registration info for pp.auth
    """
    return {
        'authenticators': get_auth_from_config,
        'mdproviders': get_auth_from_config,
        'groups': get_groups_from_config,
        'permissions': get_permissions_from_config,
    }


class UserServiceAuthenticatorMetadataProvider(object):
    """
    """

    def __init__(self, user_service_uri):
        """Set up the UserService REST client library with the location
        to communicate with.
        """
        self.log = get_log("UserServiceAuthenticatorMetadataProvider")
        self.us = rest.UserService(user_service_uri)

    def authenticate(self, environ, identity):
        """
        Check the given auth details and if its ok return the
        userid for the given details.

        See: (IAuthenticatorPlugin)
            http://docs.repoze.org/who/narr.html#writing-an-authenticator-plugin

        :returns: None indicated auth failure.

        """
        login = identity['login']
        get_log().info("authenticate: %r" % login)
        password = identity['password']
        try:
            get_log().info("authenticate:  attempting to authenticate <%s>" % login)
            self.us.user.authenticate(login, password)

        except:
            get_log().exception("Authenticate comms error for <%s>: " % login)

        else:
            get_log().info("authenticate: <%s> authenticated OK." % login)
            return login

    def add_metadata(self, environ, identity):
        """
        Recover the display name and other details for the given user name

        See: (IMetadataProvider)
            http://docs.repoze.org/who/narr.html#writing-a-metadata-provider-plugin

        """
        userid = identity.get('repoze.who.userid')
        try:
            result = self.us.user.get(userid)

        except:
            get_log().exception("user recovery failured for <%s>: " % userid)

        else:
            get_log().debug("user metadata recovered: <%s>" % result)
            if result:
                identity.update(result)


def get_auth_from_config(settings, prefix="pp.auth.userservice."):
    """
    Return a `UserServiceAuthenticatorMetadataProvider` from a settings dict
    """
    user_service_uri = settings['%suri' % prefix]
    return UserServiceAuthenticatorMetadataProvider(user_service_uri)


def get_groups_from_config(settings, prefix="pp.auth.userservice."):
    """
    Return a groups `INIGroupAdapter` from a settings dict
    """
    groups_file = settings['%sgroups_file' % prefix]
    if not os.path.isfile(groups_file):
        raise ValueError("Unable to find groups file '%s'!" % groups_file)

    return INIGroupAdapter(groups_file)


def get_permissions_from_config(settings, prefix="pp.auth.userservice."):
    """
    Return a permissions `INIGroupAdapter` from a settings dict
    """
    permissions_file = settings['%spermissions_file' % prefix]
    if not os.path.isfile(permissions_file):
        raise ValueError("Unable to find permissions file '%s'!" % permissions_file)

    return INIPermissionsAdapter(permissions_file)

