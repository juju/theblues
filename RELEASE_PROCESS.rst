Prepare for the release
-----------------------

Clone a fresh copy from the root repo. Do not attempt a release in your
current working repository as the following commands expect a fresh clone.

::

     git clone git@github.com:juju/theblues.git
     cd blues_browser


Find the next release number. You can check the last release by running `git
tag` and finding the largest version number. Note that the values are sorted
as strings, so don't just look at the last value.

::

    git tag | sort -V

Select the next number in sequence keeping in mind the minor/major versions
use.

::

    export THEBLUESRELEASE=$the_new_version


Generate changelog
------------------
We structure merge commit messages to be a short summary of the change. As such
you can get a quick log of all the major changes since the last release with
`git log`.

::

    vim CHANGELOG.rst
    git log $last-release...HEAD --merges

Use the output from that to update the changelog with the major changes of the
release.


Update the application version to the correct version and then commit the
changelog.

::

    vim setup.py

update the setup.py

::

    vim CHANGELOG.rst


change

setup(
    name='theblues',
    version='$the_new_version'

::

    git commit -a -m "Prepare for release: $THEBLUESRELEASE"


Create the release
------------------

Tag the commit with the release number and push your changes to master on github.


::

    git tag $THEBLUESRELEASE
    git push origin develop --tags


Upload the release to pypi
----------------------------

Have an account to pypi if not go to and create your account :
https://pypi.python.org/pypi?%3Aaction=register_form

You need to be an owner of the package,
please ask the team members on freenode juju-gui

Have a file ~/.pypirc with the following content

::

    [distutils] # this tells distutils what package indexes you can push to
        index-servers =
            pypi
            pypitest

        [pypi]
        repository: https://pypi.python.org/pypi
        username: {{your_username}}
        password: {{your_password}}

        [pypitest]
        repository: https://testpypi.python.org/pypi
        username: {{your_username}}





Then you can publish the release to pipy,

::

    python setup.py register -r pypitest
    python setup.py sdist upload -r pypitest
    python setup.py register -r pypi
    python setup.py sdist upload -r pypi


