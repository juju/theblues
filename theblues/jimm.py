from macaroonbakery import httpbakery

from theblues.utils import (
    ensure_trailing_slash,
    make_request,
    DEFAULT_TIMEOUT,
)


class JIMM(object):

    def __init__(self, url, timeout=DEFAULT_TIMEOUT, client=None,
                 cookies=None):
        """Initializer.

        @param url The url to the JIMM API.
        @param timeout How long to wait before timing out a request in seconds;
            a value of None means no timeout.
        @param client (httpbakery.Client) holds a context for making http
        requests with macaroons.
        @param cookies (which act as dict) holds cookies to be sent with the
        requests.
        """
        self.url = ensure_trailing_slash(url)
        self.timeout = timeout
        self.cookies = cookies
        if client is None:
            client = httpbakery.Client()
        self._client = client

    def list_models(self, macaroons):
        """ Get the logged in user's models from the JIMM controller.

        @param macaroons The discharged JIMM macaroons.
        @return The json decoded list of environments.
        """
        return make_request("{}model".format(self.url), timeout=self.timeout,
                            client=self._client, cookies=self.cookies)
