=============================
theblues
=============================

Python library for using the juju charmstore API.

Installation
------------
The easiest way to install theblues is via pip::

    $pip install theblues

Note that theblues requires python-macaroons (which has its own dependencies),
which must be installed from the repos::

	$apt-get install libmacaroons0 python-macaroons libsodium13

Without these, theblues cannot communicate with the charmstore.
