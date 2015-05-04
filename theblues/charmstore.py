import logging

import requests
from requests.exceptions import HTTPError

from errors import (
    EntityNotFound,
    ServerError,
    )

try:
    from urllib import quote
except:
    from urllib.parse import quote


class CharmStore(object):
    """A connection to the charmstore."""

    def __init__(self, url, macaroons=None, verify=True):
        super(CharmStore, self).__init__()
        self.url = url
        self.verify = verify
        self.macaroons = macaroons

    def _get(self, url):
        cookies = dict([('macaroon-storefront', self.macaroons)])
        try:
            response = requests.get(url, verify=self.verify, cookies=cookies)
            response.raise_for_status()
            return response
        # XXX: To be reviewed when splitting the library.
        # Is it te right place to log or should we let the users of the blues
        # to handle logging ?
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
        except requests.exceptions.RequestException as exc:
            message = ('Error during request: {url} '
                       'message: {message}').format(
                           url=url,
                           message=exc.message)
            logging.error(message)
            raise ServerError(exc.args[0][1].errno,
                              exc.args[0][1].strerror,
                              exc.message)

    def _meta(self, entity_id, includes):
        '''Retrieve metadata about an entity in the charmstore.

        @param entity_id The ID of the entity to get.
        @param includes Which metadata fields to include in the response.
        '''
        url = '%s/%s/meta/any?' % (self.url, entity_id)
        for include in includes:
            url += 'include=%s&' % include
        data = self._get(url)
        return data.json()

    def entity(self, entity_id, get_files=False):
        '''Get the default data for any entity (e.g. bundle or charm).

        @param entity_id The entity's id.
        '''
        includes = [
            'bundle-machine-count',
            'bundle-metadata',
            'bundle-unit-count',
            'bundles-containing',
            'charm-config',
            'charm-metadata',
            'extra-info',
            'revision-info',
            'stats'
        ]
        if get_files:
            includes.append('manifest')
        return self._meta(entity_id, includes)

    def entities(self, entity_ids):
        '''Get the default data for entities.

        @param entity_ids A list of entity id strings.
        '''
        url = '%s/meta/any?include=id&' % self.url
        for entity_id in entity_ids:
            url += 'id=%s&' % entity_id
        # Remove the trailing '&' from the URL.
        url = url[:-1]
        data = self._get(url)
        return data.json()

    def bundle(self, bundle_id):
        '''Get the default data for a bundle.

        @param bundle_id The bundle's id.
        '''
        return self.entity(bundle_id, get_files=True)

    def charm(self, charm_id):
        '''Get the default data for a charm.

        @param charm_id The charm's id.
        '''
        return self.entity(charm_id, get_files=True)

    def charm_icon_url(self, charm_id):
        '''Generate the path to the icon for charms.

        @param charm_id The ID of the charm, bundle icons are not currently
        supported.
        @return url string for the path to the icon.'''
        url = '%s/%s/icon.svg' % (self.url, charm_id)
        return url

    def charm_icon(self, charm_id):
        url = self.charm_icon_url(charm_id)
        response = self._get(url)
        return response.content

    def bundle_visualization(self, bundle_id):
        url = self.bundle_visualization_url(bundle_id)
        response = self._get(url)
        return response.content

    def bundle_visualization_url(self, bundle_id):
        url = '%s/%s/diagram.svg' % (self.url, bundle_id)
        return url

    def entity_readme_url(self, entity_id):
        '''Generate the url path for the readme of the entity.'''
        url = '%s/%s/readme' % (self.url, entity_id)
        return url

    def entity_readme_content(self, entity_id):
        readme_url = self.entity_readme_url(entity_id)
        response = self._get(readme_url)
        return response.text

    def archive_url(self, entity_id):
        '''Generate a URL for the archive.

        @param entity_id The ID of the entity to look up.
        '''
        return '%s/%s/archive' % (self.url, entity_id)

    def file_url(self, entity_id, filename):
        '''Generate a URL for a file in an archive without requesting it.

        @param entity_id The ID of the entity to look up.
        @param filename The name of the file in the archive.
        '''
        return '%s/%s/archive/%s' % (self.url, entity_id, filename)

    def files(self, entity_id, manifest=None, filename=None, read_file=False):
        '''Get the files or file contents of a file for an entity.

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
        '''
        if manifest is None:
            manifest_url = '%s/%s/meta/manifest' % (self.url, entity_id)
            manifest = self._get(manifest_url)
            manifest = manifest.json()
        files = {}
        for f in manifest:
            manifest_name = f['Name']
            file_url = self.file_url(entity_id, manifest_name)
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

    def config(self, charm_id):
        '''Get the config data for a charm.

        @param charm_id The charm's id.
        '''
        url = '%s/%s/meta/charm-config' % (self.url, charm_id)
        data = self._get(url)
        return data.json()

    def entityId(self, partial):
        '''Get an entity's full id provided a partial one.

        Raises EntityNotFound if partial cannot be resolved.
        @param partial The partial id (e.g. mysql, precise/mysql).
        '''
        url = '%s/%s/meta/any' % (self.url, partial)
        data = self._get(url)
        return data.json()['Id']

    def search(self, text, includes=None, doc_type=None, limit=None,
               autocomplete=False, promulgated_only=False, tags=None,
               sort=None, owner=None, series=None):
        '''Search for entities in the charmstore.

        @param text The text to search for.
        @param includes What metadata to return in results (e.g. charm-config)
        @param doc_type Filter to this type: bundle or charm
        @param limit Maximum number of results to return.
        @param autocomplete Whether to prefix/suffix match search terms.
        @param promulgated_only Whether to filter to only promulgated charms.
        @param tags The tags to filter; can be a list of tags or a single tag.
        @param sort Sorting the result based on the sort string provided
               which can be name, author, series and - in front for descending
        @param owner Optional owner. If provided, search results will only
               include entities that owner can view.
        @param series The series to filter; can be a list of series or a
               single series.
        '''
        url = '%s/search?text=%s' % (self.url, quote(text))
        if includes is not None:
            includes = '&'.join(['include=%s' % i for i in includes])
            url += '&%s' % includes
        if doc_type is not None:
            url += '&type=%s' % doc_type
        if limit is not None:
            url += '&limit=%s' % limit
        if autocomplete:
            url += '&autocomplete=1'
        if promulgated_only:
            url += '&owner='
        elif owner is not None:
            url += '&owner=' + owner
        if tags is not None:
            if type(tags) is list:
                tags = ','.join(tags)
            url += '&tags=%s' % tags
        if series is not None:
            if type(series) is list:
                series = ','.join(series)
            url += '&series=%s' % series
        if sort is not None:
            url += '&sort=%s' % sort
        data = self._get(url)
        return data.json()['Results']

    def fetch_related(self, ids):
        if not ids:
            return []
        meta = '&id='.join(id['Id'] for id in ids)
        url = ('{url}/meta/any?id={meta}'
               '&include=bundle-metadata&include=stats'
               '&include=extra-info&include=bundle-unit-count').format(
                   url=self.url, meta=meta)
        data = self._get(url)
        return data.json().values()

    def fetch_interfaces(self, interface, way):
        """Get the list of charms that provides or requires this id

        @param id: charm string
        @param way: provides or requires
        @returns: List of charms
        """
        if not interface:
            return []
        if way == 'requires':
            request = '&requires=' + interface
        else:
            request = '&provides=' + interface
        url = (self.url + '/search?' +
               'include=charm-metadata&include=stats' +
               '&include=extra-info&include=bundle-unit-count' +
               '&limit=1000' + request)
        data = requests.get(url, verify=self.verify)
        return data.json().values()

    def debug(self):
        '''Retrieve the debug information from the charmstore.'''
        url = '%s/debug/status' % (self.url)
        data = self._get(url)
        return data.json()

    def fetch_macaroon(self):
        '''Fetch a macaroon from charmstore.'''
        url = '{charmstore_url}/macaroon'.format(
            charmstore_url=self.url)
        response = self._get(url)
        return response.text
