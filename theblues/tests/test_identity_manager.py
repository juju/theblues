import base64
import json
from unittest import TestCase

from httmock import (
    HTTMock,
    urlmatch,
)
import macaroons
from mock import patch

from private_blues.errors import (
    InvalidMacaroon,
    ServerError,
)
from private_blues.identity_manager import IdentityManager
from private_blues.tests import helpers


_called = None


LOGIN_PATH = '.*/v1/u/.*'
DISCHARGE_PATH = '.*/discharge'
EXTRA_INFO_PATH = '.*/extra-info'


@urlmatch(path=LOGIN_PATH)
def entity_200(url, request):
    global _called
    _called = True
    return {
        'status_code': 200,
        'content': {},
    }


@urlmatch(path=LOGIN_PATH)
def entity_403(url, request):
    global _called
    _called = True
    return {
        'status_code': 403,
        'content': {},
    }


@urlmatch(path=DISCHARGE_PATH)
def discharge_macaroon_200(url, request):
    return {
        'status_code': 200,
        'content': {'Macaroon': 'something'},
    }


@urlmatch(path=DISCHARGE_PATH)
def discharge_macaroon_404(url, request):
    return {
        'status_code': 404,
        'content': {},
    }


@urlmatch(path=EXTRA_INFO_PATH)
def extra(url, request):
    response = {'status_code': 200}
    if request.method == 'GET':
        response['content'] = {'foo': 1}
    if request.method == 'PUT':
        assert request.body == '{"foo": 1}'
    return response


def patch_make_request(return_value=None):
    """Patch the "private_blues.utils.make_request" helper function."""
    return patch(
        'private_blues.identity_manager.make_request',
        return_value=return_value)


class TestIdentityManager(TestCase, helpers.TimeoutTestsMixin):

    def setUp(self):
        global _called
        _called = False
        self.idm = IdentityManager('http://example.com/v1', 'user', 'password')

    def test_login_success(self):
        with HTTMock(entity_200):
            self.idm.login('fabrice', {})
        self.assertTrue(_called)

    def test_login_success_url(self):
        user = 'fabrice'

        class FakeResponse:
            status_code = 200

            def raise_for_status(self):
                pass

        with patch_make_request(return_value=FakeResponse()) as mocked:
            self.idm.login(user, 'body')
        self.assertTrue(mocked.called)
        expected_url = 'http://example.com/v1/u/{}'.format(user)
        mocked.assert_called_once_with(
            expected_url,
            method='PUT',
            body='body',
            auth=('user', 'password'),
            timeout=3.05,
        )

    def test_login_error_forbidden(self):
        with HTTMock(entity_403):
            with self.assertRaises(ServerError) as ctx:
                    self.idm.login('fabrice', {})
        self.assertEqual(403, ctx.exception.args[0])
        self.assertTrue(_called)

    def test_login_error_timeout(self):
        with self.assert_timeout('http://example.com/v1/u/who', 3.05):
            self.idm.login('who', {})

    def test_discharge_successful(self):
        macaroon = macaroons.create("location", "secret", "public")
        macaroon = macaroon.add_third_party_caveat(
            'http://example.com/', "caveat_key", "identifier")
        with HTTMock(discharge_macaroon_200):
            results = self.idm.discharge('Brad', macaroon)
        self.assertEqual(base64.urlsafe_b64encode('"something"'), results)

    def test_discharge_error_invalid_macaroon(self):
        macaroon = macaroons.create("location", "secret", "public")
        with HTTMock(discharge_macaroon_200):
            self.assertRaises(
                InvalidMacaroon, self.idm.discharge, 'Brad', macaroon)

    def test_discharge_error_wrong_status(self):
        macaroon = macaroons.create("location", "secret", "public")
        macaroon = macaroon.add_third_party_caveat(
            'http://example.com/', "caveat_key", "identifier")
        with HTTMock(discharge_macaroon_404):
            with self.assertRaises(ServerError) as ctx:
                self.idm.discharge('Brad', macaroon)
        self.assertEqual(404, ctx.exception.args[0])

    def test_discharge_error_timeout(self):
        macaroon = macaroons.create("location", "secret", "public")
        macaroon = macaroon.add_third_party_caveat(
            'http://example.com/', "caveat_key", "identifier")
        expected_url = (
            'http://example.com/v1/discharger/discharge'
            '?discharge-for-user=who&id=identifier')
        with self.assert_timeout(expected_url, 3.05):
            self.idm.discharge('who', macaroon)

    @patch('private_blues.identity_manager.make_request')
    def test_discharge_username_quoted(self, make_request_mock):
        # When discharging the macaroon for the identity, the user name is
        # properly quoted.
        make_request_mock.return_value = {'Macaroon': 'macaroon'}
        macaroon = macaroons.create("location", "secret", "public")
        macaroon = macaroon.add_third_party_caveat(
            'http://example.com/', "caveat_key", "identifier")
        base64_macaroon = self.idm.discharge('my.user+name', macaroon)
        expected_macaroon = base64.urlsafe_b64encode(json.dumps('macaroon'))
        self.assertEqual(expected_macaroon, base64_macaroon)
        make_request_mock.assert_called_once_with(
            'http://example.com/v1/discharger/discharge'
            '?discharge-for-user=my.user%2Bname&id=identifier',
            auth=('user', 'password'),
            timeout=3.05,
            method='POST')


class TestIDMClass(TestCase, helpers.TimeoutTestsMixin):

    def setUp(self):
        self.idm = IdentityManager('http://example.com:8082/v1', 'user',
                                   'password')

    def test_init(self):
        self.assertEqual(self.idm.url, 'http://example.com:8082/v1/')
        self.assertEqual(self.idm.auth, ('user', 'password'))

    @patch('private_blues.identity_manager.make_request')
    def test_debug(self, mock):
        self.idm.debug()
        mock.assert_called_once_with(
            'http://example.com:8082/v1/debug/status', timeout=3.05)

    @patch('private_blues.identity_manager.make_request')
    def test_debug_fail(self, mock):
        mock.side_effect = ServerError('abc')
        val = self.idm.debug()
        self.assertEquals(val, {'error': 'abc'})

    @patch('private_blues.identity_manager.make_request')
    def test_get_user(self, make_request_mock):
        self.idm.get_user('jeffspinach')
        make_request_mock.assert_called_once_with(
            'http://example.com:8082/v1/u/jeffspinach',
            auth=('user', 'password'))

    def test_get_extra_info_ok(self):
        with HTTMock(extra):
            info = self.idm.get_extra_info('frobnar')
            self.assertEqual(info.get('foo'), 1)

    def test_get_extra_info_error_timeout(self):
        expected_url = 'http://example.com:8082/v1/u/who/extra-info'
        with self.assert_timeout(expected_url, 3.05):
            self.idm.get_extra_info('who')

    def test_set_extra_info_ok(self):
        with HTTMock(extra):
            # This will blow up if set_extra_info isn't passing the data along
            # correctly--see the assert in extra above.
            self.idm.set_extra_info('frobnar', {'foo': 1})

    def test_set_extra_info_error_timeout(self):
        expected_url = 'http://example.com:8082/v1/u/who/extra-info'
        with self.assert_timeout(expected_url, 3.05):
            self.idm.set_extra_info('who', {})
