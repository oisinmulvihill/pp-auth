"""

"""
import logging

from repoze.what.adapters import BaseSourceAdapter
from repoze.what.plugins.ini import INIGroupAdapter

from pp.user.client import rest


def get_log(extra=None):
    m = "{}.{}".format(__name__, extra) if extra else __name__
    return logging.getLogger(m)


class DummyINIAdapter(INIGroupAdapter):
    def __init__(self):
        BaseSourceAdapter.__init__(self)
        self.info = {}

    def _find_sections(self, hint):
        return set()


def register():
    """
    Returns registration info for pp.auth
    """
    return {
        'authenticators': get_auth_from_config,
        'mdproviders': get_auth_from_config,
        'groups': get_groups_from_config,
        'permissions': get_permissions_from_config
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
            http://docs.repoze.org/who/narr.html\
                #writing-an-authenticator-plugin

        :returns: None indicated auth failure.

        """
        login = identity['login']
        if not login:
            get_log().info("No login name given <%s>" % login)
            return

        get_log().info("authenticate: %r" % login)
        password = identity['password']
        try:
            # get_log().info(
            #     "authenticate:  attempting to authenticate <%s>" % login
            # )
            self.us.user.authenticate(login, password)

        except:
            get_log().exception("Authenticate comms error for <%s>: " % login)

        else:
            # get_log().info("authenticate: <%s> authenticated OK." % login)
            return login

    def add_metadata(self, environ, identity):
        """
        Recover the display name and other details for the given user name

        See: (IMetadataProvider)
            http://docs.repoze.org/who/narr.html\
                #writing-a-metadata-provider-plugin

        """
        userid = identity.get('repoze.who.userid')
        # get_log().debug("add_metadata for userid <%s>" % userid)

        if not userid:
            get_log().info("No userid to get details for <%s>" % userid)
            return

        try:
            result = self.us.user.get(userid)

        except:
            get_log().exception("user recovery failured for <%s>: " % userid)

        else:
            # get_log().debug("user metadata recovered: <%s>" % result)
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
    return DummyINIAdapter()


def get_permissions_from_config(settings, prefix="pp.auth.userservice."):
    """
    Return a permissions `INIGroupAdapter` from a settings dict
    """
    return DummyINIAdapter()
