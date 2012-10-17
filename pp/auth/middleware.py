import logging
from collections import defaultdict

import importlib
from repoze.what.middleware import setup_auth
from repoze.who.plugins.form import RedirectingFormPlugin
from repoze.who.plugins.auth_tkt import AuthTktCookiePlugin
#from repoze.who.plugins.basicauth import BasicAuthPlugin
#from repoze.who.plugins.friendlyform import FriendlyFormPlugin


def get_log(extra=None):
    return logging.getLogger(
        "{}.{}".format(__name__, extra) if extra else __name__
    )


PLUGIN_TYPES = ('authenticators', 'mdproviders', 'groups', 'permissions')


def get_plugin_registry(settings, prefix="pp.auth."):
    """Get a registry of all the things that the configured plugins provide,
    mapping the plugin type to a method tha builds the plugin from the
    settings dict.

    The default response using the 'plain' plugin is this::

        plugin_registry = {
            'authenticators' : {
                'plain' : plain.get_auth_from_config,
            },
            'mdproviders' : {
                'plain' : plain.get_auth_from_config,
            },
            'groups' : {
                'plain' : plain.get_groups_from_config,
            },
            'permissions' : {
                'plain' : plain.get_permissions_from_config,
            },
        }
    """
    log = get_log("get_plugin_registry")
    res = {}

    # Find plugins we've been asked to configure:
    plugin_mods = settings.get('%splugins' % prefix, 'pp.auth.plugins')
    #print "plugin_mods: ", plugin_mods
    lines = plugin_mods.split('\n')

    def check(x):
        rc = False
        x = x.strip()
        # ignore top level 'pp.auth.plugins' which is present when no
        # plugins are. Debug why later...
        if x and x != "pp.auth.plugins":
            rc = True
        return rc

    plugin_mods = [p for p in lines if check(p)]
    log.debug("plugin_mods (newline separated): <%s>" % plugin_mods)

    for mod in [importlib.import_module(i.strip()) for i in plugin_mods]:
        # Use the last part of the plugin's module name as its ID.
        plugin_id = mod.__name__.split('.')[-1]
        log.info("found plugin %r: %r" % (
            plugin_id, mod
        ))
        provides = mod.register()
        for plugin_type in PLUGIN_TYPES:
            if provides[plugin_type]:
                res[plugin_type] = {plugin_id: provides[plugin_type]}
            else:
                log.info(
                    "not provided: '{}' by '{}'. Ignoring".format(
                        plugin_type,
                        mod.__name__,
                    )
                )

    return res


def build_plugins(settings, plugin_registry, prefix="pp.auth."):
    """
    Builds all the plugins we've been asked to configure in the settings
    """
    ids = []
    log = get_log("build_plugins")

    res = defaultdict(list)

    for plugin_type in PLUGIN_TYPES:
        plugid = "%s%s" % (prefix, plugin_type)
        if plugid in settings:
            ids = [i.strip() for i in settings[plugid].split(',')]

        for plugin_id in ids:
            if plugin_id not in plugin_registry:
                # this is not provided. Ignore and skip to next.
                continue

            if not plugin_id in plugin_registry[plugin_type]:
                raise ValueError("Unknown %s: %r" % (plugin_type, plugin_id))

            log.info("add_auth_from_config: loading %s plugin: %s" % (
                plugin_type, plugin_id
            ))

            res[plugin_type].append((
                plugin_id, plugin_registry[plugin_type][plugin_id](settings)
            ))

    return res


def add_auth_from_config(app, settings, prefix="pp.auth."):
    """
    Call add_auth, using settings gathered from a settings dictionary
    :param app: The WSGI application.
    :param settings: Settings dict
    :param prefix: Settings variable prefix

    Example settings file::

        # Repoze plugin config
        repoze.who.authenticators = plain
        repoze.who.mdproviders = plain
        repoze.who.groups = plain
        repoze.who.permissions = plain

        # Plain auth plugin
        pp.auth.plain.password_file = %(here)s/auth/passwd.csv
        pp.auth.plain.groups_file = %(here)s/auth/groups.ini
        pp.auth.plain.permissions_file = %(here)s/auth/permissions.ini

        # Cookies and login handlers
        pp.auth.cookie_name = auth_cookie
        pp.auth.cookie_secret = 07cafeee-ef19-4a1c-aab2-61fefbad85f4
        pp.auth.login_url = /login
        pp.auth.login_handler_url = /login_handler

    """
    log = get_log("add_auth_from_config")

    returned = None

    # Mandatory settings
    site_name = settings.get('%ssite_name' % prefix, '')
    cookie_name = settings['%scookie_name' % prefix]
    cookie_secret = settings['%scookie_secret' % prefix]
    login_url = settings.get('%slogin_url' % prefix, '/login')
    login_handler_url = settings.get(
        '%slogin_handler_url' % prefix, '/login_handler'
    )

    # This is a registry of all the things that the configured plugins provide
    plugin_registry = get_plugin_registry(settings, prefix)

    # These are all the built plugins that we'e been configured to use
    plugins = build_plugins(settings, plugin_registry, prefix)
    if plugins:
        returned = add_auth(
            app,
            site_name,
            cookie_name,
            cookie_secret,
            login_url,
            login_handler_url,
            **plugins
        )

    else:
        # No auth configured, return app unchanged:
        log.warn("No auth configuration was found! Returning app unmodified.")
        returned = app

    return returned


def add_auth(app, site_name, cookie_name, cookie_secret, login_url,
             login_handler_url, authenticators, mdproviders, groups,
             permissions):
    """
    Add authentication and authorization middleware to the ``app``.

    :param app: The WSGI application.
    :param site_name: the site name used in basic auth box.
    :param cookie_name: basic auth name and cookie name.
    :param cookie_secret: unique secret string used to protect sessions.
    :param login_url: the url for the login page
    :param login_handler_url: the url for the login handler
    :param authenticators: list of authenticator plugins
    :param mdproviders: list of mdprovider plugins
    :param groups: list of groups plugins
    :param permissions: list of permissions plugins
    :return: The same WSGI application, with authentication and
        authorization middleware.

    """

    get_log().info("add_auth: intialising Repoze")

    if not authenticators:
        raise ValueError("No authenticators provided")
    if not mdproviders:
        raise ValueError("No mdproviders provided")
    if not groups:
        raise ValueError("No groups provided")
    if not permissions:
        raise ValueError("No permissions provided")

    # If we ever change default behavior for challengers and identifiers,
    # move these to the above function
    logout_handler = None
    form = RedirectingFormPlugin(
        login_url,
        login_handler_url,
        logout_handler,
        rememberer_name='cookie',
    )

    cookie = AuthTktCookiePlugin(cookie_secret, cookie_name)

    #identifiers = [('main_identifier', form), ('basicauth', basicauth),\
    #   ('cookie', cookie)]
    #identifiers = [('basicauth', basicauth), ('cookie', cookie)]
    identifiers = [('form', form), ('cookie', cookie)]

    #challengers = [('form', form), ('basicauth', basicauth)]
    #challengers = [('basicauth', basicauth)]
    challengers = [('form', form)]

    #get_log().info(dict(groups))
    #get_log().info(    dict(permissions))
    #get_log().info(    identifiers)
    #get_log().info(    authenticators)
    #get_log().info(    challengers )
    #get_log().info(    mdproviders)
    app_with_auth = setup_auth(
        app=app,
        # # why these are dicts where all the other are lists...
        group_adapters=dict(groups),
        permission_adapters=dict(permissions),
        identifiers=identifiers,
        authenticators=authenticators,
        challengers=challengers,
        mdproviders=mdproviders,
        log_level=logging.DEBUG
    )

    get_log().info("add_auth: user/group/permission setup OK.")

    return app_with_auth
