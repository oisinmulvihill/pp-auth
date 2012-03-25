import mock 

from pp.auth import middleware
from pp.auth.plugins import plain

SETTINGS = {
        'pp.auth.site_name': 'BookingSys',
        'pp.auth.cookie_name': 'auth_cookie',
        'pp.auth.cookie_secret': '07cafeee-ef19-4a1c-aab2-61fefbad85f4',
        'pp.auth.login_url': ' /login',
        'pp.auth.login_handler_url' : '/login_handler',

        'pp.auth.plugins' : 'pp.auth.plugins.plain',
        'pp.auth.authenticators' : 'plain',
        'pp.auth.mdproviders' : 'plain',
        'pp.auth.groups' : 'plain',
        'pp.auth.permissions' : 'plain',
        }


def test_plugin_registry():
    """ Test the plugin registry mechanics using the default 'plain' plugin
    """
    assert middleware.get_plugin_registry(SETTINGS) == {
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

def test_build_plugins():
    """ Tests building plugins from a registry and settings config
    """
    auth1 = mock.Mock(return_value = 'auth1')
    auth2 = mock.Mock(return_value = 'auth2')
    md1 = mock.Mock(return_value = 'md1')
    md2 = mock.Mock(return_value = 'md2')
    groups1 = mock.Mock(return_value = 'groups1')
    groups2 = mock.Mock(return_value = 'groups2')
    perms1 = mock.Mock(return_value = 'perms1')
    perms2 = mock.Mock(return_value = 'perms2')

    registry = {
        'authenticators' : {
            'dummy1' : auth1,
            'dummy2' : auth2,
        },
        'mdproviders' : {
            'dummy1' : md1,
            'dummy2' : md2,
        },
        'groups' : {
            'dummy1' : groups1, 
            'dummy2' : groups2, 
        },
        'permissions' : {
            'dummy1' : perms1,
            'dummy2' : perms2,
        },
    }

    settings =  {
        'pp.auth.authenticators' : 'dummy1, dummy2',
        'pp.auth.mdproviders' : 'dummy1, dummy2',
        'pp.auth.groups' : 'dummy1, dummy2',
        'pp.auth.permissions' : 'dummy1, dummy2',
    }

    plugins = dict(middleware.build_plugins(settings, registry))
    assert plugins == {
        'authenticators' : [ ('dummy1', 'auth1'), ('dummy2', 'auth2') ],
        'mdproviders' :  [ ('dummy1', 'md1'), ('dummy2', 'md2') ],
        'groups' :  [ ('dummy1', 'groups1'), ('dummy2', 'groups2') ],
        'permissions' :  [ ('dummy1', 'perms1'), ('dummy2', 'perms2') ],
    }
    auth1.assert_called_once_with(settings)
    auth2.assert_called_once_with(settings)
    md1.assert_called_once_with(settings)
    md2.assert_called_once_with(settings)
    groups1.assert_called_once_with(settings)
    groups2.assert_called_once_with(settings)
    perms1.assert_called_once_with(settings)
    perms2.assert_called_once_with(settings)

