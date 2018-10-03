from unittest import TestCase

from httmock import HTTMock
import mock

from theblues.errors import ServerError
from theblues.utils import make_request
from theblues.tests import helpers

URL = 'http://example.com/'


def patch_log_error():
    """Mock the error method of the error logger."""
    return mock.patch('theblues.utils.log.error')


class TestUtils(TestCase, helpers.TimeoutTestsMixin):

    def subscription_response(self, url, request):
        self.assertEqual('http://example.com/?uuid=foo', url.geturl())
        return {
            'status_code': 200,
            'content': b'{"foo":"bar","baz":"bax"}',
        }

    def empty_response(self, url, request):
        return {
            'status_code': 200,
            'content': ''
        }

    def failing_response(self, url, request):
        return {
            'status_code': 404,
            'content': b'not-found'
        }

    def failing_response_server(self, url, request):
        return {
            'status_code': 500,
            'content': b'server-failed'
        }

    def invalid_response(self, url, request):
        return {
            'status_code': 200,
            'content': b'{'
        }

    def test_make_request(self):
        with HTTMock(self.subscription_response):
            response = make_request(URL, query={'uuid': 'foo'})
        self.assertEqual({u'foo': u'bar', u'baz': u'bax'}, response)

    def test_make_request_with_macaroons(self):
        def handler(url, request):
            self.assertEqual(request.headers['Macaroons'], 'my-macaroons')
            return {'status_code': 200}
        # Test with a JSON decoded object.
        with HTTMock(handler):
            make_request(URL, macaroons='my-macaroons')

    def check_write_request(self, method):
        def handler(url, request):
            self.assertEqual('http://example.com/', url.geturl())
            self.assertEqual(method, request.method)
            self.assertEqual('{"uuid": "foo"}', request.body)
            self.assertEqual(
                'application/json', request.headers['Content-Type'])
            return {
                'status_code': 200,
                'content': b'{"foo":"bar","baz":"bax"}',
            }
        # Test with a JSON decoded object.
        with HTTMock(handler):
            response = make_request(URL, method=method, body={'uuid': 'foo'})
        self.assertEqual({u'foo': u'bar', u'baz': u'bax'}, response)
        # Test with a JSON encoded string.
        with HTTMock(handler):
            response = make_request(URL, method=method, body='{"uuid": "foo"}')
        self.assertEqual({u'foo': u'bar', u'baz': u'bax'}, response)

    def test_make_post_request(self):
        self.check_write_request('POST')

    def test_make_put_request(self):
        self.check_write_request('PUT')

    def test_make_request_empty_response(self):
        with HTTMock(self.empty_response):
            response = make_request(URL, method='POST', body={'uuid': 'foo'})
        self.assertEqual({}, response)

    def test_make_request_not_found_error(self):
        with HTTMock(self.failing_response):
            with patch_log_error() as mock_log_error:
                with self.assertRaises(ServerError) as ctx:
                    make_request(URL, query={'uuid': 'foo'})
        expected_error = (
            'Error during request: http://example.com/?uuid=foo '
            'message: not-found')
        self.assertEqual((404, expected_error), ctx.exception.args)
        mock_log_error.assert_called_once_with(expected_error)

    def test_make_request_server_error(self):
        with HTTMock(self.failing_response_server):
            with patch_log_error() as mock_log_error:
                with self.assertRaises(ServerError) as ctx:
                    make_request(URL, query={'uuid': 'foo'})
        expected_error = (
            'Error during request: http://example.com/?uuid=foo '
            'message: server-failed')
        self.assertEqual((500, expected_error), ctx.exception.args)
        mock_log_error.assert_called_once_with(expected_error)

    def test_make_request_unexpected_error(self):
        with mock.patch('theblues.utils.requests.get') as mock_get:
            mock_get.side_effect = ValueError('bad wolf')
            with patch_log_error() as mock_log_error:
                with self.assertRaises(ServerError) as ctx:
                    make_request(URL, query={'uuid': 'foo'})
        expected_error = (
            'Error during request: http://example.com/?uuid=foo '
            'message: bad wolf')
        self.assertEqual(expected_error, ctx.exception.args[0])
        mock_log_error.assert_called_once_with(expected_error)

    def test_make_request_invalid_json(self):
        with HTTMock(self.invalid_response):
            with self.assertRaises(ServerError) as ctx:
                make_request(URL, query={'uuid': 'foo'})
        self.assertIn('Error decoding JSON response', ctx.exception.args[0])

    def test_make_request_timeout(self):
        with self.assert_timeout('http://example.com/?uuid=foo', 42):
            make_request(URL, query={'uuid': 'foo'}, timeout=42)

    def test_make_request_invalid_method(self):
        with self.assertRaises(ValueError) as ctx:
            make_request('http://1.2.3.4', method='bad')
        self.assertEqual('invalid method bad', ctx.exception.args[0])
