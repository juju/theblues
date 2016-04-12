from contextlib import contextmanager

from httmock import HTTMock
import mock
import requests

from theblues.errors import ServerError


def timeout_response(url, request):
    """Callback used to simulate a timeout response."""
    raise requests.exceptions.Timeout


class TimeoutTestsMixin(object):

    @contextmanager
    def assert_timeout(self, url, timeout):
        """Ensure the request in the context block times out."""
        with HTTMock(timeout_response):
            with mock.patch('theblues.errors.log.warning') as mock_warn:
                with self.assertRaises(ServerError) as ctx:
                    yield ctx
        expected_message = 'Request timed out: {} timeout: {}s'.format(
            url, timeout)
        self.assertEqual(expected_message, ctx.exception.args[0])
        mock_warn.assert_called_once_with(expected_message)
