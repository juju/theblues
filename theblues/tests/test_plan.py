import datetime
import json

from jujubundlelib import references
from mock import patch
from unittest import TestCase

from macaroonbakery import httpbakery

from theblues.plans import (
    Plan,
    Plans,
)
from theblues.errors import ServerError
from theblues.utils import DEFAULT_TIMEOUT


class TestPlans(TestCase):

    def setUp(self):
        self.client = httpbakery.Client()
        self.plans = Plans('http://example.com', client=self.client)
        self.ref = references.Reference.from_string(
            'cs:trusty/landscape-mock-0')

    def test_init(self):
        self.assertEqual(self.plans.url, 'http://example.com/v2/')

    @patch('theblues.plans.make_request')
    def test_get_plans(self, mocked):
        now = datetime.datetime.now()
        now = now.replace(microsecond=0)
        mocked.return_value = json.loads(
            '['
            '{"url":"canonical-landscape/24-7","plan":"full plan",'
            '"created-on":"' + now.strftime("%Y-%m-%dT%H:%M:%SZ") + '",'
            '"description":"some description1",'
            '"price":"$0.10/managed machine/hour"'
            '},'
            '{"url":"canonical-landscape/8-5","plan":"half plan",'
            '"created-on":"' + now.strftime("%Y-%m-%dT%H:%M:%SZ") + '",'
            '"description":"some description2",'
            '"price":"$0.01/managed machine/hour"'
            '},'
            '{"url":"canonical-landscape/free","plan":"free plan",'
            '"created-on":"' + now.strftime("%Y-%m-%dT%H:%M:%SZ") + '",'
            '"description":"some description3",'
            '"price":"Free"'
            '}'
            ']')
        resp = self.plans.get_plans(self.ref)
        self.assertEqual((
            Plan(url='canonical-landscape/24-7',
                 plan='full plan',
                 created_on=now,
                 description='some description1',
                 price='$0.10/managed machine/hour'),
            Plan(url='canonical-landscape/8-5',
                 plan='half plan',
                 created_on=now,
                 description='some description2',
                 price='$0.01/managed machine/hour'),
            Plan(url='canonical-landscape/free',
                 plan='free plan',
                 created_on=now,
                 description='some description3',
                 price='Free'),
        ), resp)
        mocked.assert_called_once_with(
            'http://example.com/v2/charm?charm-url=cs:trusty/landscape-mock-0',
            timeout=DEFAULT_TIMEOUT,
            client=self.client
        )

    @patch('theblues.plans.make_request')
    def test_get_plans_exception(self, mocked):
        mocked.side_effect = ServerError()
        with self.assertRaises(ServerError):
            self.plans.get_plans(self.ref)

    @patch('theblues.plans.make_request')
    def test_get_plans_invalid_data(self, mocked):
        now = datetime.datetime.now()
        now = now.replace(microsecond=0)
        mocked.return_value = json.loads(
            '['
            '{"wrongurl":"canonical-landscape/24-7","plan":"full plan",'
            '"created-on":"' + now.strftime("%Y-%m-%dT%H:%M:%SZ") + '",'
            '"description":"some description1",'
            '"price":"$0.10/managed machine/hour"'
            '}]')
        with self.assertRaises(ServerError):
            self.plans.get_plans(self.ref)

    @patch('theblues.plans.make_request')
    def test_get_plans_invalid_date_format(self, mocked):
        mocked.return_value = json.loads(
            '['
            '{"wrongurl":"canonical-landscape/24-7","plan":"full plan",'
            '"created-on":"2009-12-09",'
            '"description":"some description1",'
            '"price":"$0.10/managed machine/hour"'
            '}]')
        with self.assertRaises(ServerError):
            self.plans.get_plans(self.ref)

    @patch('theblues.plans.make_request')
    def test_list_wallets(self, mocked):
        mocked.return_value = {
            'wallets': [
                {
                    'owner': 'rose',
                    'wallet': 'default',
                    'limit': '100',
                    'budgeted': '0',
        			'unallocated': '100',
        			'available': '100.00',
        			'consumed': '0.00',
        			'default': True,
                }
            ],
            'total': {
                'limit': '100',
        		'budgeted': '0',
        		'available': '100.00',
        		'unallocated': '100',
        		'usage': '0%',
        		'consumed': '0.00',
            },
            'credit': '10000',
        }
        result = self.plans.list_wallets()
        self.assertEqual(result, '')

    @patch('theblues.plans.make_request')
    def test_list_wallets_exception(self, mocked):
        pass

    @patch('theblues.plans.make_request')
    def test_get_wallet(self, mocked):
        mocked.return_value = {
            'limit': '100',
            'total': {
                'limit': '100',
        		'budgeted': '0',
        		'available': '100.00',
        		'unallocated': '100',
        		'usage': '0%',
        		'consumed': '0.00',
            },
            'credit': '10000',
        }
        result = self.plans.get_wallet('default')
        self.assertEqual(result, '')

    @patch('theblues.plans.make_request')
    def test_get_wallet_exception(self, mocked):
        pass
