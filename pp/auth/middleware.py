import logging
from collections import defaultdict

from repoze.what.middleware import setup_auth
# We need to set up the repoze.who components used by repoze.what for
# authentication
#from repoze.who.plugins.basicauth import BasicAuthPlugin

#from repoze.who.plugins.friendlyform import FriendlyFormPlugin
from repoze.who.plugins.form import RedirectingFormPlugin
from repoze.who.plugins.auth_tkt import AuthTktCookiePlugin

from plugins import plain

#from plu import PlainAuthenticatorMetadataProvider, get_plain_auth_from_config

def get_log():
    return logging.getLogger('pp.auth.middleware')


# Map plugins their builder methods
PLUGINS = {
    'authenticators' : {
        'plain' : plain.get_auth_from_config,   
    },
    'mdproviders' : {
        'plain' : plain.get_auth_from_config,    # TODO make these map to the same object 
    },
    'groups' : {
        'plain' : plain.get_groups_from_config,
    },
    'permissions' : {
        'plain' : plain.get_permissions_from_config,
    },
}


def add_auth_from_config(app, settings, prefix="repoze.who."):
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
    # Mandatory settings
    site_name = settings.get('%ssite_name' % prefix,'')
    cookie_name = settings['%scookie_name' % prefix]
    cookie_secret = settings['%scookie_secret' % prefix]
    login_url = settings.get('%slogin_url' % prefix, '/login')
    login_handler_url = settings.get('%slogin_handler_url' % prefix, '/login_handler')

    # Build plugins to pass into repoze
    plugins = defaultdict(list)
    for plugin_type in ('authenticators', 'mdproviders', 'groups', 'permissions'):
        ids = settings[prefix + plugin_type].split(',')
        for plugin_id in ids:
            if not plugin_id in PLUGINS[plugin_type]:
                raise ValueError("Unknown %s: %r" % (plugin_type, plugin_id))
            get_log().info("add_auth_from_config: loading %s plugin: %s" % (plugin_type, plugin_id))
            plugins[plugin_type].append((plugin_id, PLUGINS[plugin_type][plugin_id](settings)))

    return add_auth(app, site_name, cookie_name, cookie_secret,  login_url, login_handler_url,
                    **plugins)

def add_auth(app, site_name, cookie_name, cookie_secret, login_url, login_handler_url, 
             authenticators, mdproviders, groups, permissions):
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

    # If we ever change default behavior for challengers and identifiers, move these 
    # to the above function
    logout_handler = None
    form = RedirectingFormPlugin(
        login_url,
        login_handler_url,
        logout_handler,
        rememberer_name='cookie',
    )

    cookie = AuthTktCookiePlugin(cookie_secret, cookie_name)

    #identifiers = [('main_identifier', form), ('basicauth', basicauth), ('cookie', cookie)]
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
        app = app,
        group_adapters = dict(groups),  # why these are dicts where all the other are lists... 
        permission_adapters = dict(permissions), 
        identifiers = identifiers, 
        authenticators = authenticators,
        challengers = challengers, 
        mdproviders = mdproviders, 
        log_level = logging.DEBUG
    )

    get_log().info("add_auth: user/group/permission setup OK.")
        
    return app_with_auth
