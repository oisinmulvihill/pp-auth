"""
Exercise the plain module as much as I can.

Oisin Mulvihill, Ed Easton
2009-05-20

"""
import mock
from pp.auth import pwtools
from pp.auth.plugins import plain

MockValidatePassword = mock.Mock(spec=pwtools.validate_password)

user_data = """username, password, firstname, lastname, email
admin1, xxx, Admin, Istrator, admin@example.com
manager1, xxx, Bob, Wellington, bob@example.com
user1, xxx, Janet, Ganet, janet@example.com
"""

def test_empty_data_authenticate():
    """Test empty data doesn't cause any problems."""
    p = plain.PlainAuthenticatorMetadataProvider("")
    identity = dict(login='admin1', password='admin1')
    assert p.authenticate({}, identity) is None


def test_empty_data_add_metadata():
    """Test empty data doesn't cause any problems."""
    p = plain.PlainAuthenticatorMetadataProvider("")
    identity = dict(userid='admin1')
    assert p.add_metadata({}, identity) is None


@mock.patch('pp.auth.pwtools.validate_password', return_value=True)
def test_authenticate_valid(mock_validate):
    """ Ok, now test with valid data """
    p = plain.PlainAuthenticatorMetadataProvider(user_data)
    identity = dict(login='user1', password='user1')
    assert p.authenticate({}, identity) ==  'user1'


@mock.patch('pp.auth.pwtools.validate_password', return_value=True)
def test_authenticate_valid_other_user(mock_validate):
    """ Check another user """
    p = plain.PlainAuthenticatorMetadataProvider(user_data)
    identity = dict(login='admin1', password='admin1')
    assert p.authenticate({}, identity) ==  'admin1'


@mock.patch('pp.auth.pwtools.validate_password', return_value=False)
def test_authenticate_invalid(mock_validate):
    """ Invalid user """
    p = plain.PlainAuthenticatorMetadataProvider(user_data)
    identity = dict(login='admin1', password='admin1')
    assert p.authenticate({}, identity) is None

def test_add_metadata():
    p = plain.PlainAuthenticatorMetadataProvider(user_data)
    env = {}
    identity = {'repoze.who.userid':'admin1'}
    p.add_metadata(env, identity)    
    assert identity['firstname'] ==  'Admin'
    assert identity['lastname'] == 'Istrator'
    assert identity['name'] ==  'Admin Istrator'
    assert identity['email'] == 'admin@example.com'


def test_add_metadata_repeat():
    p = plain.PlainAuthenticatorMetadataProvider(user_data)
    env = {}
    identity = {'repoze.who.userid':'manager1'}
    p.add_metadata(env, identity)
    p.add_metadata(env, identity)
    assert identity['firstname'] == 'Bob'
    assert identity['lastname'] == 'Wellington'
    assert identity['name'] == 'Bob Wellington'
    assert identity['email'] == 'bob@example.com'
