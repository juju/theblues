from mock import (
    Mock,
    patch
    )
from unittest import TestCase

from theblues.jem import JEM


class TestJEM(TestCase):

    def setUp(self):
        self.jem = JEM('http://example.com')

    def test_init(self):
        self.assertEqual(self.jem.url, 'http://example.com/')

    @patch('requests.get')
    def test_fetch_macaroon(self, mocked):

        class MockResponse(object):

            def json(self):
                return {
                    'Info': {
                        'Macaroon': {'foo': 'bar'}
                    }
                }

        mocked.return_value = MockResponse()
        resp = self.jem.fetch_macaroon()
        self.assertEqual('{"foo": "bar"}', resp)

    @patch('requests.get')
    def test_fetch_macaroon_fails_gracefully(self, mocked):
        def boom():
            raise ValueError
        mocked.side_effect = boom
        resp = self.jem.fetch_macaroon()
        self.assertIsNone(resp)

    @patch('requests.get')
    def test_fetch_macaroon_fails_gracefully_json(self, mocked):
        def boom():
            raise ValueError
        mock_response = Mock()
        mock_response.json = Mock()
        mock_response.json.side_effect = boom
        mocked.return_value = mock_response
        resp = self.jem.fetch_macaroon()
        self.assertIsNone(resp)

    @patch('requests.get')
    def test_fetch_macaroon_fails_gracefully_macaroon(self, mocked):
        mock_response = Mock()
        mock_response.json = Mock()
        mock_response.json.return_value = {
            'boom': "this fails"
        }
        mocked.return_value = mock_response
        resp = self.jem.fetch_macaroon()
        self.assertIsNone(resp)

    @patch('theblues.jem.make_request')
    def test_get_user_models(self, mocked):
        mocked.return_value = '42'
        resp = self.jem.get_users_models('macaroons!')
        self.assertEqual('42', resp)
        mocked.called_once_with(
            'http://example.com/env', macaroons='macaroons!')

    @patch('theblues.jem.make_request')
    def test_get_model(self, mocked):
        mocked.return_value = '42'
        resp = self.jem.get_model('macaroons!', 'dalek', 'exterminate')
        self.assertEqual('42', resp)
        mocked.called_once_with(
            'http://example.com/models/dalek/exterminate',
            macaroons='macaroons!')
