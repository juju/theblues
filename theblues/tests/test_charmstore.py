from unittest import TestCase

from httmock import (
    HTTMock,
    urlmatch,
    )
from mock import patch

from theblues.charmstore import (
    CharmStore,

    # We need to import the exceptions that come up in testing from charmstore
    # rather than errors so that assertRaises doesn't get confused by
    # namespaces.
    EntityNotFound,
    ServerError,
    )


SAMPLE_CHARM = 'precise/mysql-1'
SAMPLE_BUNDLE = 'mongodb-cluster'
SAMPLE_FILE = 'README.md'
CONFIG_PATH = '/%s/meta/charm-config' % SAMPLE_CHARM
MANIFEST_PATH = '/%s/meta/manifest' % SAMPLE_CHARM
FILE_PATH = '/%s/archive/%s' % (SAMPLE_CHARM, SAMPLE_FILE)
ID_PATH = '.*/meta/any'
README_PATH = '/%s/readme' % SAMPLE_CHARM
SEARCH_PATH = '^/search.*'
DEBUG_PATH = '/debug/status'
MACAROON_PATH = '/macaroon'
ICON_PATH = '/%s/icon.svg' % SAMPLE_CHARM
DIAGRAM_PATH = '/%s/diagram.svg' % SAMPLE_BUNDLE


@urlmatch(path=ID_PATH)
def entity_200(url, request):
    return {
        'status_code': 200,
        'content': {'Meta': {'charm-metadata': {'exists': True}}}
        }


@urlmatch(path=ID_PATH)
def entity_404(url, request):
    return {'status_code': 404}


@urlmatch(path=ID_PATH)
def entity_407(url, request):
    return {'status_code': 407}


@urlmatch(path=CONFIG_PATH)
def config_200(url, request):
    return {'status_code': 200, 'content': {'exists': True}}


@urlmatch(path=CONFIG_PATH)
def config_404(url, request):
    return {'status_code': 404}


@urlmatch(path=MANIFEST_PATH)
def manifest_200(url, request):
    return {
        'status_code': 200,
        'content': b'[{"Name": "README.md"}, {"Name": "icon.svg"}]'
        }


@urlmatch(path=MANIFEST_PATH)
def manifest_404(url, request):
    return {'status_code': 404}


@urlmatch(path=FILE_PATH)
def file_200(url, request):
    return {'status_code': 200, 'content': b'This is a file.'}


@urlmatch(path=FILE_PATH)
def file_404(url, request):
    return {'status_code': 404}


@urlmatch(path=ID_PATH)
def id_200(url, request):
    return {'status_code': 200, 'content': {'Id': 'foo/bar'}}


@urlmatch(path=ID_PATH)
def id_404(url, request):
    return {'status_code': 404}


@urlmatch(path=DEBUG_PATH)
def debug_200(url, request):
    return {'status_code': 200, 'content': {'status': 'all clear'}}


@urlmatch(path=SEARCH_PATH)
def search_200(url, request):
    expected = 'text=foo'
    if url.query != expected:
        raise AssertionError(
            'Got wrong query string: %s vs %s' % (url.query, expected))
    return {
        'status_code': 200,
        'content': b'{"Results": [{"Id": "cs:foo/bar-0"}]}'
        }


@urlmatch(path=SEARCH_PATH)
def search_200_escaped(url, request):
    expected = 'text=%26foo'
    if url.query != expected:
        raise AssertionError(
            'Got wrong query string: %s vs %s' % (url.query, expected))
    return {
        'status_code': 200,
        'content': b'{"Results": [{"Id": "cs:foo/bar-0"}]}'
        }


@urlmatch(path=SEARCH_PATH)
def search_200_with_macaroon(url, request):
    expected = "[macaroon1, macaroon2]"
    macaroons = request._cookies.get('macaroon-storefront')

    if expected != macaroons:
        raise AssertionError(
            'Macaroon not set correctly: %s vs %s' % (macaroons, expected))

    return {
        'status_code': 200,
        'content': b'{"Results": [{"Id": "cs:foo/bar-0"}]}'
        }


@urlmatch(path=SEARCH_PATH)
def search_400(url, request):
    return {
        'status_code': 400,
        'content': (b'{"Message": "invalid parameter: user", '
                    b'"Code": "bad request"}')
        }


@urlmatch(path=SEARCH_PATH)
def search_limit_200(url, request):
    expected = 'text=foo&limit=1'
    if url.query != expected:
        raise AssertionError(
            'Got wrong query string: %s vs %s' % (url.query, expected))
    return {
        'status_code': 200,
        'content': b'{"Results": [{"Id": "cs:foo/bar-0"}]}'
        }


@urlmatch(path=SEARCH_PATH)
def search_includes_200(url, request):
    expected = 'text=foo&include=archive-size&include=charm-metadata'
    if url.query != expected:
        raise AssertionError(
            'Got wrong query string: %s vs %s' % (url.query, expected))
    return {
        'status_code': 200,
        'content': b'{"Results": [{"Id": "cs:foo/bar-0"}]}'
        }


@urlmatch(path=SEARCH_PATH)
def search_tags_200(url, request):
    expected = 'text=foo&tags=databases'
    if url.query != expected:
        raise AssertionError(
            'Got wrong query string: %s vs %s' % (url.query, expected))
    return {
        'status_code': 200,
        'content': b'{"Results": [{"Id": "cs:foo/bar-0"}]}'
        }


@urlmatch(path=SEARCH_PATH)
def search_multiple_tags_200(url, request):
    expected = 'text=foo&tags=databases,applications'
    if url.query != expected:
        raise AssertionError(
            'Got wrong query string: %s vs %s' % (url.query, expected))
    return {
        'status_code': 200,
        'content': b'{"Results": [{"Id": "cs:foo/bar-0"}]}'
        }


@urlmatch(path=SEARCH_PATH)
def search_autocomplete_200(url, request):
    expected = 'text=foo&autocomplete=1'
    if url.query != expected:
        raise AssertionError(
            'Got wrong query string: %s vs %s' % (url.query, expected))
    return {
        'status_code': 200,
        'content': b'{"Results": [{"Id": "cs:foo/bar-0"}]}'
        }


@urlmatch(path=SEARCH_PATH)
def search_owner_200(url, request):
    expected = 'text=&owner=hatch'
    if url.query != expected:
        raise AssertionError(
            'Got wrong query string: %s vs %s' % (url.query, expected))
    return {
        'status_code': 200,
        'content': b'{"Results": [{"Id": "cs:foo/bar-0"}]}'
    }


@urlmatch(path=README_PATH)
def readme_404(url, request):
    return {'status_code': 404}


@urlmatch(path=README_PATH)
def readme_200(url, request):
    return {
        'status_code': 200,
        'content': b'This is the readme'
    }


@urlmatch(path=MACAROON_PATH)
def fetch_macaroon_200(url, request):
    return {
        'status_code': 200,
        'content': b'{"mymacaroon": "something"}'
        }


@urlmatch(path=MACAROON_PATH)
def fetch_macaroon_404(url, request):
    return {'status_code': 404}


@urlmatch(path=ICON_PATH)
def icon_200(url, request):
    return {
        'status_code': 200,
        'content': 'icon'
        }


@urlmatch(path=ICON_PATH)
def icon_404(url, request):
    return {'status_code': 404}


@urlmatch(path=DIAGRAM_PATH)
def diagram_200(url, request):
    return {
        'status_code': 200,
        'content': 'diagram'
        }


@urlmatch(path=DIAGRAM_PATH)
def diagram_404(url, request):
    return {'status_code': 404}


class TestCharmStore(TestCase):

    def entities_response(self, url, request):
        self.assertEqual(
            url.geturl(), 'http://example.com/meta/' +
            'any?include=id&id=wordpress&id=mysql')
        return {
            'status_code': 200,
            'content': b'{"wordpress":"wordpress","mysql":"mysql"}'}

    def setUp(self):
        self.cs = CharmStore('http://example.com')

    def test_init(self):
        self.assertEqual(self.cs.url, 'http://example.com')

    def test_entity(self):
        with HTTMock(entity_200):
            data = self.cs.charm(SAMPLE_CHARM)
        self.assertEqual({'Meta': {'charm-metadata': {'exists': True}}}, data)

    def test_entities(self):
        with HTTMock(self.entities_response):
            response = self.cs.entities(['wordpress', 'mysql'])
        self.assertEqual(
            {u'wordpress': u'wordpress', u'mysql': u'mysql'}, response)

    def test_entities_error(self):
        with HTTMock(entity_404):
            with self.assertRaises(EntityNotFound) as cm:
                self.cs.entities(['not-found'])
            self.assertEqual(
                'http://example.com/meta/any?include=id&id=not-found',
                cm.exception.args[0]
            )

    def test_charm_error(self):
        with HTTMock(entity_404):
            with self.assertRaises(EntityNotFound):
                self.cs.charm(SAMPLE_CHARM)

    def test_charm_error_407(self):
        with HTTMock(entity_407):
            with self.assertRaises(EntityNotFound):
                self.cs.charm(SAMPLE_CHARM)

    def test_config(self):
        with HTTMock(config_200):
            data = self.cs.config(SAMPLE_CHARM)
        self.assertEqual({'exists': True}, data)

    def test_config_error(self):
        with HTTMock(config_404):
            with self.assertRaises(EntityNotFound):
                self.cs.config(SAMPLE_CHARM)

    def test_archive_url(self):
        with HTTMock(manifest_200):
            data = self.cs.archive_url(SAMPLE_CHARM)
        self.assertEqual(u'http://example.com/precise/mysql-1/archive', data)

    def test_file_good(self):
        with HTTMock(manifest_200):
            data = self.cs.files(SAMPLE_CHARM)
        self.assertEqual({
            u'icon.svg':
            u'http://example.com/precise/mysql-1/archive/icon.svg',
            u'README.md':
            u'http://example.com/precise/mysql-1/archive/README.md'
            },
            data)

    def test_file_error(self):
        with HTTMock(manifest_404):
            with self.assertRaises(EntityNotFound):
                self.cs.files(SAMPLE_CHARM)

    def test_file_one_file(self):
        with HTTMock(manifest_200):
            data = self.cs.files(SAMPLE_CHARM, filename='README.md')
        self.assertEqual(
            u'http://example.com/precise/mysql-1/archive/README.md',
            data)

    def test_file_one_file_error(self):
        with HTTMock(manifest_200):
            with self.assertRaises(EntityNotFound):
                self.cs.files(SAMPLE_CHARM, filename='does.not.exist.md')

    def test_file_read_file(self):
        with HTTMock(manifest_200):
            with HTTMock(file_200):
                data = self.cs.files(
                    SAMPLE_CHARM, filename='README.md', read_file=True)
        self.assertEqual('This is a file.', data)

    def test_file_read_file_error(self):
        with HTTMock(manifest_200):
            with HTTMock(file_404):
                with self.assertRaises(EntityNotFound):
                    self.cs.files(
                        SAMPLE_CHARM, filename='readme.md', read_file=True)

    def test_entityId(self):
        with HTTMock(id_200):
            charm_id = self.cs.entityId('bar')
            self.assertEqual('foo/bar', charm_id)

    def test_ids_no_charm(self):
        with HTTMock(id_404):
            with self.assertRaises(EntityNotFound):
                self.cs.entityId('baz')

    def test_search(self):
        with HTTMock(search_200):
            results = self.cs.search('foo')
            self.assertEqual([{'Id': 'cs:foo/bar-0'}], results)

    def test_search_escaped(self):
        with HTTMock(search_200_escaped):
            results = self.cs.search('&foo')
            self.assertEqual([{'Id': 'cs:foo/bar-0'}], results)

    def test_search_400(self):
        with patch('theblues.charmstore.logging.error') as log_mocked:
            with HTTMock(search_400):
                with self.assertRaises(ServerError) as cm:
                    self.cs.search('foo')
        self.assertEqual(400, cm.exception.args[0])
        log_mocked.assert_called_with(
            'Error during request: http://example.com/search?text=foo '
            'status code:(400) message: '
            '{"Message": "invalid parameter: user", "Code": "bad request"}')

    def test_search_limit(self):
        with HTTMock(search_limit_200):
            results = self.cs.search('foo', limit=1)
            self.assertEqual([{'Id': 'cs:foo/bar-0'}], results)

    def test_search_autocomplete(self):
        with HTTMock(search_autocomplete_200):
            results = self.cs.search(
                'foo', autocomplete=True)
            self.assertEqual([{'Id': 'cs:foo/bar-0'}], results)

    def test_search_includes(self):
        with HTTMock(search_includes_200):
            results = self.cs.search(
                'foo', includes=['archive-size', 'charm-metadata'])
            self.assertEqual([{'Id': 'cs:foo/bar-0'}], results)

    def test_search_tags(self):
        with HTTMock(search_tags_200):
            results = self.cs.search('foo', tags='databases')
            self.assertEqual([{'Id': 'cs:foo/bar-0'}], results)

    def test_search_multiple_tags(self):
        with HTTMock(search_multiple_tags_200):
            results = self.cs.search('foo', tags=['databases', 'applications'])
            self.assertEqual([{'Id': 'cs:foo/bar-0'}], results)

    def test_search_owner(self):
        with HTTMock(search_owner_200):
            results = self.cs.search('', owner='hatch')
            self.assertEqual([{"Id": "cs:foo/bar-0"}], results)

    def test_charm_icon_url(self):
        entity_id = 'mongodb'
        url = self.cs.charm_icon_url(entity_id)
        self.assertEqual('http://example.com/mongodb/icon.svg', url)

    def test_charm_icon_ok(self):
        entity_id = 'precise/mysql-1'
        with HTTMock(icon_200):
            icon = self.cs.charm_icon(entity_id)
        self.assertEqual('icon', icon)

    def test_charm_icon_bad(self):
        entity_id = 'precise/mysql-1'
        with HTTMock(icon_404):
            with self.assertRaises(EntityNotFound):
                self.cs.charm_icon(entity_id)

    def test_bundle_visualization_url(self):
        entity_id = 'mongodb-cluster'
        url = self.cs.bundle_visualization_url(entity_id)
        self.assertEqual('http://example.com/mongodb-cluster/diagram.svg', url)

    def test_bundle_visualization_ok(self):
        entity_id = 'mongodb-cluster'
        with HTTMock(diagram_200):
            diagram = self.cs.bundle_visualization(entity_id)
        self.assertEqual('diagram', diagram)

    def test_bundle_visualization_bad(self):
        entity_id = 'mongodb-cluster'
        with HTTMock(diagram_404):
            with self.assertRaises(EntityNotFound):
                self.cs.bundle_visualization(entity_id)

    def test_entity_readme_url(self):
        entity_id = 'mongodb-cluster'
        url = self.cs.entity_readme_url(entity_id)
        self.assertEqual('http://example.com/mongodb-cluster/readme', url)

    def test_readme_not_found(self):
        with HTTMock(readme_404):
            with self.assertRaises(EntityNotFound):
                self.cs.entity_readme_content('foo')

    def test_readme_content(self):
        with HTTMock(readme_200):
            content = self.cs.entity_readme_content('precise/mysql-1')
            self.assertEqual('This is the readme', content)

    def test_debug(self):
        with HTTMock(debug_200):
            debug_data = self.cs.debug()
            self.assertEqual('all clear', debug_data['status'])

    def test_fetch_macaroon_successful(self):
        with HTTMock(fetch_macaroon_200):
            results = self.cs.fetch_macaroon()
            self.assertEqual('{"mymacaroon": "something"}', results)

    def test_fetch_macaroon_not_found(self):
        with HTTMock(fetch_macaroon_404):
            with self.assertRaises(EntityNotFound) as cm:
                self.cs.fetch_macaroon()
        self.assertEqual(cm.exception.args, ('http://example.com/macaroon',))

    def test_search_with_macaroon(self):
        with HTTMock(search_200_with_macaroon):
            self.cs.macaroons = "[macaroon1, macaroon2]"
            results = self.cs.search('foo')
            self.assertEqual([{'Id': 'cs:foo/bar-0'}], results)
