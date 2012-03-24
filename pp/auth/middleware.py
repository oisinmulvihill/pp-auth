import os
import os.path
import logging

from repoze.what.middleware import setup_auth
# We need to set up the repoze.who components used by repoze.what for
# authentication
from repoze.who.plugins.basicauth import BasicAuthPlugin

# We'll use group and permission based exclusively on INI files
from repoze.what.plugins.ini import INIGroupAdapter
from repoze.what.plugins.ini import INIPermissionsAdapter
#from repoze.who.plugins.friendlyform import FriendlyFormPlugin
from repoze.who.plugins.form import RedirectingFormPlugin
from repoze.who.plugins.auth_tkt import AuthTktCookiePlugin

from authenticators import PlainAuthenticatorMetadataProvider


def get_log():
    return logging.getLogger('pp.auth.middleware')


def add_auth_from_config(app, config, settings, prefix="commonauth."):
    """ 
    Call add_auth, using settings gathered from a settings dictionary
    :param app: The WSGI application.
    :param config: Pyramid Configurator
    :param settings: Settings dict
    :param prefix: Settings variable prefix
    """
    site_name = settings.get('%ssite_name' % prefix,'')
    cookie_name = settings['%scookie_name' % prefix]
    cookie_secret = settings['%scookie_secret' % prefix]
    password_file = settings['%spassword_file' % prefix]
    groups_file = settings['%sgroups_file' % prefix]
    permissions_file = settings['%spermissions_file' % prefix]
    login_url = settings.get('%slogin_url' % prefix, '/login')
    login_handler_url = settings.get('%slogin_handler_url' % prefix, '/login_handler')

    return add_auth(app, config, site_name, cookie_name, cookie_secret, password_file, 
             groups_file, permissions_file, login_url, login_handler_url)


def add_auth(app, config, site_name, cookie_name, cookie_secret, password_file, 
             groups_file, permissions_file, login_url='login', 
             login_handler_url='login_handler'):
    """
    Add authentication and authorization middleware to the ``app``.

    :param app: The WSGI application.
    :param config: Pyramid Configurator
    :param site_name: the site name used in basic auth box.
    :param cookie_name: basic auth name and cookie name.
    :param cookie_secret: unique secret string used to protect sessions.
    :param groups_file: the ini file source for the groups information.
    :param passwd_file: the ini file source for the permission information.
    :param login_url: the url for the login page
    :param login_handler_url: the url for the login handler
    :return: The same WSGI application, with authentication and
        authorization middleware.
        
    """

    get_log().info("add_auth: adding user/group/permission file based setup.")

    if not os.path.isfile(password_file):
        raise ValueError("Unable to find password file '%s'!" % password_file)
    else:
        user_data_file = os.path.abspath(password_file)

    if not os.path.isfile(groups_file):
        raise ValueError("Unable to find groups file '%s'!" % groups_file)
    else:
        groups = os.path.abspath(groups_file)
        
    if not os.path.isfile(permissions_file):
        raise ValueError("Unable to find password file '%s'!" % permissions_file)
    else:
        permissions = os.path.abspath(permissions_file)
    
    basicauth = BasicAuthPlugin(site_name)

    # Recover the User details and load it for the CSV repoze plugin to handle:
    fd = open(user_data_file, 'r')
    user_data = fd.read()
    fd.close()
    plain_auth = PlainAuthenticatorMetadataProvider(user_data)
                   
    # Build web form plugin
               
    #post_login_url = None
    #logout_handler = None
    #post_logout_url = None
    #login_counter_name = None
    #form = FriendlyFormPlugin(
    #    login_url,
    #    login_handler_url,
    #    post_login_url,
    #    logout_handler,
    #    post_logout_url,
    #    login_counter_name=login_counter_name,
    #    rememberer_name='cookie',
    #    charset='utf-8',
    #)

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

    authenticators = [('htpasswd', plain_auth)]

    mdproviders = [('simplemeta', plain_auth)]

    groups = {'all_groups': INIGroupAdapter(groups)}
    permissions = {'all_perms': INIPermissionsAdapter(permissions)}

    app_with_auth = setup_auth(
        app = app,
        group_adapters = groups,
        permission_adapters = permissions, 
        identifiers = identifiers, 
        authenticators = authenticators,
        challengers = challengers, 
        mdproviders = mdproviders, 
        log_level = logging.DEBUG
    )

    get_log().info("add_auth: user/group/permission setup OK.")
        
    return app_with_auth
