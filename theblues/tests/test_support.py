from unittest import TestCase

from httmock import HTTMock

from theblues.support import (
    Priority,
    Support,
)


class TestSupport(TestCase):

    def create_case(self, url, request):
        self.assertEqual('http://example.com/', url.geturl())

        self.assertEqual('POST', request.method)
        self.assertEqual({
            'priority': 'L1- Core functionality not available',
            'phone': '4325345345234',
            'orgid': 'someorgid',
            'recordType': 'somerecordtype',
            'external': 1,
            '00ND0000005lqBV': 'some businessImpact',
            'description': 'my description',
            'subject': 'My subject',
            'email': 'someone@email.com',
            'name': 'someone'
            }, request.original.data)
        return {
            'status_code': 200,
            'content': b'{"foo":"bar","baz":"bax"}',
        }

    def setUp(self):
        self.support = Support('http://example.com', 'someorgid',
                               'somerecordtype')

    def test_create_case(self):
        with HTTMock(self.create_case):
            self.support.create_case('someone',
                                     'someone@email.com',
                                     'My subject', 'my description',
                                     'some businessImpact', Priority.L1,
                                     '4325345345234')

    def test_create_case_empty_name(self):
        with self.assertRaises(ValueError) as ctx:
            self.support.create_case('',
                                     'someone@email.com',
                                     'My subject', 'my description',
                                     'some businessImpact', Priority.L1,
                                     '4325345345234')
        self.assertEqual('empty name', ctx.exception.args[0])

    def test_create_case_invalid_mail(self):
        with self.assertRaises(ValueError) as ctx:
            self.support.create_case('someone',
                                     'someoneatmaildotcom',
                                     'My subject', 'my description',
                                     'some businessImpact', Priority.L1,
                                     '4325345345234')
        self.assertEqual('invalid email: someoneatmaildotcom',
                         ctx.exception.args[0])
