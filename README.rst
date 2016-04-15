=============================
theblues
=============================

Python library for using the juju charmstore API.

Installation
------------
The easiest way to install theblues is via pip::

    $ pip install theblues

Parts of theblues require the use of macaroons (e.g. parsing the return of
`Charmstore.fetch_macaroon` or interacting with `IdentityManager.discharge`).

To use authenticated aspects of theblues, e.g. jem, you'll need to be able to
manage macaroons. theblues was developed around libmacaroons. On ubuntu, you
can get libmacaroons from a ppa::


	$ sudo add-apt-repository ppa:yellow/ppa -y
	$ apt-get install libmacaroons0 python-macaroons libsodium13

Without these, theblues cannot make any authenticated requests to the
charm store or other services, but is usable to communicate with the charm
store for things like looking up charm information.

Usage
-----

Interacting with the charmstore is pretty simple. To look up an entity on the
charmstore (e.g. a charm or bundle)::

    >>> from theblues.charmstore import CharmStore
    >>> cs = CharmStore('https://api.jujucharms.com/v4')
    >>> entity = cs.entity('wordpress')
    >>> entity['Id']
    u'cs:trusty/wordpress-2'

Data for an entity is contained in the `Meta` item of the response, matching the
json returned from the charmstores::

    >>> entity['Meta']['charm-metadata']['Name']
    u'wordpress'

You can also get files for the entity::

    >>> cs.files('wordpress')['hooks/install']
    u'https://api.jujucharms.com/v4/wordpress/archive/hooks/install
    >>> hook = cs.files('wordpress', filename='hooks/install', read_file=True)
    >>> print hook
    #!/bin/bash

    set -xe
    ...
    <snipped for length>
    ...
    juju-log "So, environment is setup. We'll wait for some hooks to fire off before we get all crazy"

To see all methods available, refer to the full docs.
