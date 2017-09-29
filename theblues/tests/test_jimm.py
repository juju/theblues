from mock import (
    patch
    )
from unittest import TestCase

from theblues.jimm import JIMM


class TestJIMM(TestCase):

    def setUp(self):
        self.jimm = JIMM('http://example.com')

    def test_init(self):
        self.assertEqual(self.jimm.url, 'http://example.com/')

    @patch('theblues.jimm.make_request')
    def test_list_models(self, mocked):
        mocked.return_value = '42'
        resp = self.jimm.list_models('macaroons!')
        self.assertEqual('42', resp)
        mocked.called_once_with(
            'http://example.com/env', macaroons='macaroons!')
