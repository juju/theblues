import datetime
import json
from mock import patch
from unittest import TestCase

from macaroonbakery import httpbakery

from theblues.terms import (
    Term,
    Terms,
)
from theblues.errors import ServerError
from theblues.utils import DEFAULT_TIMEOUT


class TestTerms(TestCase):

    def setUp(self):
        self.client = httpbakery.Client()
        self.terms = Terms('http://example.com', client=self.client)

    def test_init(self):
        self.assertEqual(self.terms.url, 'http://example.com/v1/')

    @patch('theblues.terms.make_request')
    def test_get_terms(self, mocked):
        now = datetime.datetime.now()
        now = now.replace(microsecond=0)
        mocked.return_value = json.loads(
            '[{"name":"canonical","title":"some title","revision":4,'
            '"created-on":"' + now.strftime("%Y-%m-%dT%H:%M:%SZ") + '",'
            '"content":"some content"}]')
        resp = self.terms.get_terms('name_of_terms', 3)
        self.assertEqual(Term(name='canonical',
                              content='some content',
                              title='some title',
                              created_on=now,
                              revision=4), resp)
        mocked.assert_called_once_with(
            'http://example.com/v1/terms/name_of_terms?revision=3',
            timeout=DEFAULT_TIMEOUT,
            client=self.client
        )

    @patch('theblues.terms.make_request')
    def test_get_terms_exception(self, mocked):
        mocked.side_effect = ServerError()
        with self.assertRaises(ServerError):
            self.terms.get_terms('name_of_terms', 3)

    @patch('theblues.terms.make_request')
    def test_get_terms_invalid_data(self, mocked):
        now = datetime.datetime.now()
        now = now.replace(microsecond=0)
        mocked.return_value = json.loads(
            '[{"wrongname":"canonical","title":"some title","revision":4,'
            '"created-on":"' + now.strftime("%Y-%m-%dT%H:%M:%SZ") + '",'
            '"content":"some content"}]')
        with self.assertRaises(ServerError):
            self.terms.get_terms('name_of_terms', 3)

    @patch('theblues.terms.make_request')
    def test_get_terms_invalid_date_format(self, mocked):
        mocked.return_value = json.loads(
            '[{"name":"canonical","title":"some title","revision":4,'
            '"created-on": "2019-03-12", "content":"some content"}]')
        with self.assertRaises(ServerError):
            self.terms.get_terms('name_of_terms', 3)
