import logging
try:
    from urllib import urlencode
except:
    from urllib.parse import urlencode

import requests
from requests.exceptions import (
    HTTPError,
    RequestException,
    Timeout,
    )

from .errors import (
    EntityNotFound,
    ServerError,
    )


class CharmStore(object):
    """A connection to the charmstore."""

    def __init__(self, url, macaroons=None, timeout=None, verify=True):
        """Initializer.

        @param url The url to the charmstore API.
        @param macaroons The optional discharged macaroon allowing access to
            authenticated queries against the charmstore.
        @param timeout How long to wait in seconds before timing out a request;
            a value of None means no timeout.
        @param verify Whether to verify the certificate for the charmstore API
            host.
        """
        super(CharmStore, self).__init__()
        self.url = url
        self.verify = verify
        self.timeout = timeout
        self.macaroons = macaroons

    def _get(self, url):
        """Make a get request against the charmstore.

        This method is used by other API methods to standardize querying.

        @param url The full url to query
            (e.g. https://api.jujucharms.com/charmstore/v4/macaroon)
        """
        if self.macaroons is None or len(self.macaroons) == 0:
            cookies = {}
        else:
            cookies = dict([('macaroon-storefront', self.macaroons)])
        try:
            response = requests.get(url, verify=self.verify, cookies=cookies,
                                    timeout=self.timeout)
            response.raise_for_status()
            return response
        except HTTPError as exc:
            if exc.response.status_code in (404, 407):
                raise EntityNotFound(url)
            else:
                message = ('Error during request: {url} '
                           'status code:({code}) '
                           'message: {message}').format(
                               url=url,
                               code=exc.response.status_code,
                               message=exc.response.text)
                logging.error(message)
                raise ServerError(exc.response.status_code,
                                  exc.response.text,
                                  message)
        except Timeout:
            message = 'Request timed out: {url} timeout: {timeout}'
            message = message.format(url=url, timeout=self.timeout)
            logging.error(message)
            raise ServerError(message)
        except RequestException as exc:
            message = ('Error during request: {url} '
                       'message: {message}').format(
                           url=url,
                           message=exc.message)
            logging.error(message)
            raise ServerError(exc.args[0][1].errno,
                              exc.args[0][1].strerror,
                              exc.message)

    def _meta(self, entity_id, includes, channel=None):
        '''Retrieve metadata about an entity in the charmstore.

        @param entity_id The ID either a reference or a string of the entity
               to get.
        @param includes Which metadata fields to include in the response.
        @param channel Optional channel name, e.g. `development`.
        '''
        queries = []
        if includes is not None:
            queries.extend([('include', include) for include in includes])
        if channel is not None:
            queries.append(('channel', channel))
        if len(queries):
            url = '{}/{}/meta/any?{}'.format(self.url, _get_path(entity_id),
                                             urlencode(queries))
        else:
            url = '{}/{}/meta/any'.format(self.url, _get_path(entity_id))
        data = self._get(url)
        return data.json()

    def entity(self, entity_id, get_files=False, channel=None):
        '''Get the default data for any entity (e.g. bundle or charm).

        @param entity_id The entity's id either as a reference or a string
        @param get_files Whether to fetch the files for the charm or not.
        @param channel Optional channel name.
        '''
        includes = [
            'bundle-machine-count',
            'bundle-metadata',
            'bundle-unit-count',
            'bundles-containing',
            'charm-config',
            'charm-metadata',
            'common-info',
            'extra-info',
            'owner',
            'revision-info',
            'published',
            'stats',
            'resources',
            'supported-series'
        ]
        if get_files:
            includes.append('manifest')
        return self._meta(entity_id, includes, channel=channel)

    def entities(self, entity_ids):
        '''Get the default data for entities.

        @param entity_ids A list of entity ids either as strings or references.
        '''
        url = '%s/meta/any?include=id&' % self.url
        for entity_id in entity_ids:
            url += 'id=%s&' % _get_path(entity_id)
        # Remove the trailing '&' from the URL.
        url = url[:-1]
        data = self._get(url)
        return data.json()

    def bundle(self, bundle_id, channel=None):
        '''Get the default data for a bundle.

        @param bundle_id The bundle's id.
        @param channel Optional channel name.
        '''
        return self.entity(bundle_id, get_files=True, channel=channel)

    def charm(self, charm_id, channel=None):
        '''Get the default data for a charm.

        @param charm_id The charm's id.
        @param channel Optional channel name.
        '''
        return self.entity(charm_id, get_files=True, channel=channel)

    def charm_icon_url(self, charm_id, channel=None):
        '''Generate the path to the icon for charms.

        @param charm_id The ID of the charm.
        @param channel Optional channel name.
        @return The url to the icon.
        '''
        url = '{}/{}/icon.svg'.format(self.url, _get_path(charm_id))
        return _add_channel(url, channel)

    def charm_icon(self, charm_id, channel=None):
        '''Get the charm icon.

        @param charm_id The ID of the charm.
        @param channel Optional channel name.
        '''
        url = self.charm_icon_url(charm_id, channel=channel)
        response = self._get(url)
        return response.content

    def bundle_visualization(self, bundle_id, channel=None):
        '''Get the bundle visualization.

        @param bundle_id The ID of the bundle.
        @param channel Optional channel name.
        '''
        url = self.bundle_visualization_url(bundle_id, channel=channel)
        response = self._get(url)
        return response.content

    def bundle_visualization_url(self, bundle_id, channel=None):
        '''Generate the path to the visualization for bundles.

        @param charm_id The ID of the bundle.
        @param channel Optional channel name.
        @return The url to the visualization.
        '''
        url = '{}/{}/diagram.svg'.format(self.url, _get_path(bundle_id))
        return _add_channel(url, channel)

    def entity_readme_url(self, entity_id, channel=None):
        '''Generate the url path for the readme of an entity.

        @entity_id The id of the entity (i.e. charm, bundle).
        @param channel Optional channel name.
        '''
        url = '{}/{}/readme'.format(self.url, _get_path(entity_id))
        return _add_channel(url, channel)

    def entity_readme_content(self, entity_id, channel=None):
        '''Get the readme for an entity.

        @entity_id The id of the entity (i.e. charm, bundle).
        @param channel Optional channel name.
        '''
        readme_url = self.entity_readme_url(entity_id, channel=channel)
        response = self._get(readme_url)
        return response.text

    def archive_url(self, entity_id, channel=None):
        '''Generate a URL for the archive of an entity..

        @param entity_id The ID of the entity to look up as a string
               or reference.
        @param channel Optional channel name.
        '''
        url = '{}/{}/archive'.format(self.url, _get_path(entity_id))
        return _add_channel(url, channel)

    def file_url(self, entity_id, filename, channel=None):
        '''Generate a URL for a file in an archive without requesting it.

        @param entity_id The ID of the entity to look up.
        @param filename The name of the file in the archive.
        @param channel Optional channel name.
        '''
        url = '{}/{}/archive/{}'.format(self.url, _get_path(entity_id),
                                        filename)
        return _add_channel(url, channel)

    def files(self, entity_id, manifest=None, filename=None,
              read_file=False, channel=None):
        '''
        Get the files or file contents of a file for an entity.

        If all files are requested, a dictionary of filenames and urls for the
        files in the archive are returned.

        If filename is provided, the url of just that file is returned, if it
        exists.

        If filename is provided and read_file is true, the *contents* of the
        file are returned, if the file exists.

        @param entity_id The id of the entity to get files for
        @param manifest The manifest of files for the entity. Providing this
            reduces queries; if not provided, the manifest is looked up in the
            charmstore.
        @param filename The name of the file in the archive to get.
        @param read_file Whether to get the url for the file or the file
            contents.
        @param channel Optional channel name.
        '''
        if manifest is None:
            manifest_url = '{}/{}/meta/manifest'.format(self.url,
                                                        _get_path(entity_id))
            manifest_url = _add_channel(manifest_url, channel)
            manifest = self._get(manifest_url)
            manifest = manifest.json()
        files = {}
        for f in manifest:
            manifest_name = f['Name']
            file_url = self.file_url(_get_path(entity_id), manifest_name,
                                     channel=channel)
            files[manifest_name] = file_url

        if filename:
            file_url = files.get(filename, None)
            if file_url is None:
                raise EntityNotFound(entity_id, filename)
            if read_file:
                data = self._get(file_url)
                return data.text
            else:
                return file_url
        else:
            return files

    def resource_url(self, entity_id, name, revision):
        '''
        Return the resource url for a given resource on an entity.

        @param entity_id The id of the entity to get resource for.
        @param name The name of the resource.
        @param revision The revision of the resource.
        '''
        return '{}/{}/resource/{}/{}'.format(self.url,
                                             _get_path(entity_id),
                                             name,
                                             revision)

    def config(self, charm_id, channel=None):
        '''Get the config data for a charm.

        @param charm_id The charm's id.
        @param channel Optional channel name.
        '''
        url = '{}/{}/meta/charm-config'.format(self.url, _get_path(charm_id))
        data = self._get(_add_channel(url, channel))
        return data.json()

    def entityId(self, partial, channel=None):
        '''Get an entity's full id provided a partial one.

        Raises EntityNotFound if partial cannot be resolved.
        @param partial The partial id (e.g. mysql, precise/mysql).
        @param channel Optional channel name.
        '''
        url = '{}/{}/meta/any'.format(self.url, _get_path(partial))
        data = self._get(_add_channel(url, channel))
        return data.json()['Id']

    def search(self, text, includes=None, doc_type=None, limit=None,
               autocomplete=False, promulgated_only=False, tags=None,
               sort=None, owner=None, series=None):
        '''
        Search for entities in the charmstore.

        @param text The text to search for.
        @param includes What metadata to return in results (e.g. charm-config).
        @param doc_type Filter to this type: bundle or charm.
        @param limit Maximum number of results to return.
        @param autocomplete Whether to prefix/suffix match search terms.
        @param promulgated_only Whether to filter to only promulgated charms.
        @param tags The tags to filter; can be a list of tags or a single tag.
        @param sort Sorting the result based on the sort string provided
            which can be name, author, series and - in front for descending.
        @param owner Optional owner. If provided, search results will only
            include entities that owner can view.
        @param series The series to filter; can be a list of series or a
            single series.
        '''
        queries = self._common_query_parameters(doc_type, includes, owner,
                                                promulgated_only, series, sort)
        if len(text):
            queries.append(('text', text))
        if limit is not None:
            queries.append(('limit', limit))
        if autocomplete:
            queries.append(('autocomplete', 1))
        if tags is not None:
            if type(tags) is list:
                tags = ','.join(tags)
            queries.append(('tags', tags))
        if len(queries):
            url = '{}/search?{}'.format(self.url, urlencode(queries))
        else:
            url = '{}/search'.format(self.url)
        data = self._get(url)
        return data.json()['Results']

    def list(self, includes=None, doc_type=None, promulgated_only=False,
             sort=None, owner=None, series=None):
        '''
        List entities in the charmstore.

        @param includes What metadata to return in results (e.g. charm-config).
        @param doc_type Filter to this type: bundle or charm.
        @param promulgated_only Whether to filter to only promulgated charms.
        @param sort Sorting the result based on the sort string provided
            which can be name, author, series and - in front for descending.
        @param owner Optional owner. If provided, search results will only
            include entities that owner can view.
        @param series The series to filter; can be a list of series or a
            single series.
        '''
        queries = self._common_query_parameters(doc_type, includes, owner,
                                                promulgated_only, series, sort)
        if len(queries):
            url = '{}/list?{}'.format(self.url, urlencode(queries))
        else:
            url = '{}/list'.format(self.url)
        data = self._get(url)
        return data.json()['Results']

    def _common_query_parameters(self, doc_type, includes, owner,
                                 promulgated_only, series, sort):
        '''
        Extract common query parameters between search and list into slice.

        @param includes What metadata to return in results (e.g. charm-config).
        @param doc_type Filter to this type: bundle or charm.
        @param promulgated_only Whether to filter to only promulgated charms.
        @param sort Sorting the result based on the sort string provided
            which can be name, author, series and - in front for descending.
        @param owner Optional owner. If provided, search results will only
            include entities that owner can view.
        @param series The series to filter; can be a list of series or a
            single series.
        '''
        queries = []
        if includes is not None:
            queries.extend([('include', include) for include in includes])
        if doc_type is not None:
            queries.append(('type', doc_type))
        if promulgated_only:
            queries.append(('promulgated', 1))
        if owner is not None:
            queries.append(('owner', owner))
        if series is not None:
            if type(series) is list:
                series = ','.join(series)
            queries.append(('series', series))
        if sort is not None:
            queries.append(('sort', sort))
        return queries

    # XXX j.c.sackett 2016-04-15 this should be updated to just accept a list
    # of id strings, and client code should be updated to pass that.
    def fetch_related(self, ids):
        """Fetch related entity information.

        Fetches metadata, stats and extra-info for the supplied entities.

        @param ids The entity ids to fetch related information for. A list of
            entity id dicts from the charmstore.
        """
        if not ids:
            return []
        meta = '&id='.join(id['Id'] for id in ids)
        url = ('{url}/meta/any?id={meta}'
               '&include=bundle-metadata&include=stats'
               '&include=supported-series&include=extra-info'
               '&include=bundle-unit-count').format(
                   url=self.url, meta=meta)
        data = self._get(url)
        return data.json().values()

    def fetch_interfaces(self, interface, way):
        """Get the list of charms that provides or requires this interface.

        @param interface The interface for the charm relation.
        @param way The type of relation, either "provides" or "requires".
        @return List of charms
        """
        if not interface:
            return []
        if way == 'requires':
            request = '&requires=' + interface
        else:
            request = '&provides=' + interface
        url = (self.url + '/search?' +
               'include=charm-metadata&include=stats&include=supported-series'
               '&include=extra-info&include=bundle-unit-count'
               '&limit=1000' + request)
        data = self._get(url)
        return data.json().values()

    def debug(self):
        '''Retrieve the debug information from the charmstore.'''
        url = '{}/debug/status'.format(self.url)
        data = self._get(url)
        return data.json()

    def fetch_macaroon(self):
        '''Fetch a macaroon from charmstore.'''
        url = '{charmstore_url}/macaroon'.format(
            charmstore_url=self.url)
        response = self._get(url)
        return response.text


def _get_path(entity_id):
    '''Get the entity_id as a string if it is a Reference.

    @param entity_id The ID either a reference or a string of the entity
          to get.
    @return entity_id as a string
    '''
    try:
        path = entity_id.path()
    except AttributeError:
        path = entity_id
    return path


def _add_channel(url, channel=None):
    '''Add channel query parameters when present.

    @param url The url to add the channel query when present.
    @param channel The channel name.
    @return the url with channel query parameter when present.
    '''
    if channel is not None:
        url = '{}?channel={}'.format(url, channel)
    return url
