"""
This uses the pp-user-model and provides the repoze.who plugin for
authentication and metadata recovery. I want to reuse the current mongo code
in an attempt to improve the userservice as a whole.

Oisin Mulvihill
2012-11-21

"""
import logging

from repoze.what.adapters import BaseSourceAdapter
from repoze.what.plugins.ini import INIGroupAdapter


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


class USMBMetadataProvider(object):
    """User Service Mongo Backend Metadata and Authentication provider.
    """
    def __init__(self, config):
        """Set up the UserService REST client library with the location
        to communicate with.

        :param config: The mongodb config.

        E.g::

            cfg = dict(
                dbname="everyone",
                port=27017,
                host="127.0.0.1",
            )


        """
        self.log = get_log("{}.USMBMetadataProvider".format(__name__))

        from pp.user.model import db

        cfg = dict(
            db_name=config.get("dbname", "pptestdb"),
            port=int(config.get("port", 27017)),
            host=config.get("host", "127.0.0.1"),
        )
        self.log.debug("MongoDB config<{:s}>".format(cfg))
        db.init(cfg)

    def authenticate(self, environ, identity):
        """
        Check the given auth details and if its ok return the
        userid for the given details.

        See: (IAuthenticatorPlugin)
            http://docs.repoze.org/who/narr.html\
                #writing-an-authenticator-plugin

        :returns: None indicated auth failure.

        """
        from pp.user.model import user

        login = identity['login']
        if not login:
            get_log().info(
                "authenticate: No login name given <{!r}>".format(login)
            )
            return

        #get_log().info("authenticate: %r" % login)
        password = identity['password']
        try:
            # get_log().info(
            #     "authenticate:  attempting to authenticate <{!r}>".format(
            #         login
            #     )
            # )
            user.validate_password(login, password)

        except:
            get_log().exception(
                "Authenticate comms error for <{!r}>: ".format(login)
            )

        else:
            get_log().info(
                "authenticate: <{!r}> authenticated OK.".format(login)
            )
            return login

    def add_metadata(self, environ, identity):
        """
        Recover the display name and other details for the given user name

        See: (IMetadataProvider)
            http://docs.repoze.org/who/narr.html#\
                writing-a-metadata-provider-plugin

        """
        from pp.user.model import user

        userid = identity.get('repoze.who.userid')
        #get_log().debug("add_metadata for userid <{!r}>".format(userid))

        if not userid:
            get_log().info(
                "No userid to get details for <{!r}>".format(userid)
            )
            return

        try:
            result = user.get(userid)

        except:
            get_log().exception(
                "user recovery failured for <{!r}>: ".format(userid)
            )

        else:
            #get_log().debug("user metadata recovered: <{!r}>".format(result))
            if result:
                identity.update(result)


def get_auth_from_config(settings, prefix="mongodb."):
    """Return a `USMBMetadataProvider` from a settings dict.
    """
    cfg = dict(
        dbname=settings['%sdbname' % prefix],
        port=int(settings['%sport' % prefix]),
        host=settings['%shost' % prefix],
    )
    return USMBMetadataProvider(cfg)


def get_groups_from_config(settings, prefix="pp.auth.userservice."):
    """Return a groups `INIGroupAdapter` from a settings dict.
    """
    return DummyINIAdapter()


def get_permissions_from_config(settings, prefix="pp.auth.userservice."):
    """Return a permissions `INIGroupAdapter` from a settings dict.
    """
    return DummyINIAdapter()
