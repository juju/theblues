.. :changelog:

History
-------

0.5.2 (2019-10-15)
++++++++++++++++++

Make session persistant per CS object

0.5.1 (2019-01-10)
++++++++++++++++++

Add the ability to define default includes when getting entity info

0.5.0 (2018-10-03)
++++++++++++++++++

make_request: add support for including macaroons header

0.4.1 (2018-09-20)
++++++++++++++++++

Do not rely on idm auth anymore. Add support for macaroons instead

0.3.9 (2018-09-18)
++++++++++++++++++

Make it possible to disable stats collection
Add wallets and budgets
Use http bakery.
Add charm-actions data to charm_data

0.3.8 (2016-11-23)
++++++++++++++++++

Properly quote the user name in the idm query when requesting discharge tokens.

0.3.7 (2016-11-03)
++++++++++++++++++

Supports overriding the default URL for backwards compatibility.
Accept cs: prefix on entity IDs

0.3.6 (2016-10-03)
++++++++++++++++++

Replaces JEM API with JIMM API.

0.3.5 (2016-09-30)
++++++++++++++++++

Discharge for user to return an encoded array.
Update Makefile to work on clean trusty machine.
Trivial rename of development channel.

0.3.4 (2016-07-28)
++++++++++++++++++

Unify timeout.
Make sure we don't have unexpected exception.
Add discharge token for user endpoint.

0.3.3 (2016-07-04)
++++++++++++++++++

Add support case creation.

0.3.2 (2016-06-14)
++++++++++++++++++

Add support for terms and plan.

0.3.1 (2016-05-10)
++++++++++++++++++

Include owner in api call

0.3.0 (2016-05-03)
++++++++++++++++++

Update JEM API calls to version 2.

0.2.2 (2016-04-19)
++++++++++++++++++

Add resources in meta search and resource_url method.

0.2.1 (2016-04-15)
++++++++++++++++++

* Added code for identity manager and juju environment manager APIs
* Updated docs

0.2.0 (2016-03-24)
++++++++++++++++++

* Add LGPL3 license.
* Add optional channel arguments.
* Make deps less strict to work across trusty -> xenial.

0.1.1 (2016-01-25)
++++++++++++++++++

* Use Reference from jujubundlelib as a parameter.
* Add list endpoint.


0.1.0 (2015-12-04)
++++++++++++++++++

* Fix for empty macaroon cookie.


0.0.5 (2015-11-20)
++++++++++++++++++

* Expose common-info.
* Fix import.


0.0.4 (2015-06-10)
++++++++++++++++++

* Support setting a timeout on charmstore requests.


0.0.3 (2015-05-04)
++++++++++++++++++

* Add type filter to charmstore search.


0.0.2 (2015-04-08)
++++++++++++++++++

* Add series filter to charmstore search.
* Handle 407 http error from charmstore as EntityNotFound.
* Add simple usage example to README.
* Minor changes to HACKING.
* Minor fixes.


0.0.1 (2015-03-19)
++++++++++++++++++

* Initial release.
