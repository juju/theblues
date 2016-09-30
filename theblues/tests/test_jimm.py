from mock import (
    Mock,
    patch
    )
from unittest import TestCase

from theblues.jimm import JIMM


class TestJIMM(TestCase):

    def setUp(self):
        self.jimm = JIMM('http://example.com')

    def test_init(self):
        self.assertEqual(self.jimm.url, 'http://example.com/')

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
        resp = self.jimm.fetch_macaroon()
        self.assertEqual('{"foo": "bar"}', resp)

    @patch('requests.get')
    def test_fetch_macaroon_fails_gracefully(self, mocked):
        def boom():
            raise ValueError
        mocked.side_effect = boom
        resp = self.jimm.fetch_macaroon()
        self.assertIsNone(resp)

    @patch('requests.get')
    def test_fetch_macaroon_fails_gracefully_json(self, mocked):
        def boom():
            raise ValueError
        mock_response = Mock()
        mock_response.json = Mock()
        mock_response.json.side_effect = boom
        mocked.return_value = mock_response
        resp = self.jimm.fetch_macaroon()
        self.assertIsNone(resp)

    @patch('requests.get')
    def test_fetch_macaroon_fails_gracefully_macaroon(self, mocked):
        mock_response = Mock()
        mock_response.json = Mock()
        mock_response.json.return_value = {
            'boom': "this fails"
        }
        mocked.return_value = mock_response
        resp = self.jimm.fetch_macaroon()
        self.assertIsNone(resp)

    @patch('theblues.jimm.make_request')
    def test_list_models(self, mocked):
        mocked.return_value = '42'
        resp = self.jimm.list_models('macaroons!')
        self.assertEqual('42', resp)
        mocked.called_once_with(
            'http://example.com/env', macaroons='macaroons!')
