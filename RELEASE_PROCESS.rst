Prepare for the release
-----------------------

Clone a fresh copy from the root repo. Do not attempt a release in your
current working repository as the following commands expect a fresh clone.

::

     git clone git@github.com:juju/theblues.git
     cd theblues


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


Update the application version to the correct version.

Update the application version in the the setup.py

::

    vim setup.py


change

setup(
    name='theblues',
    version='$the_new_version'


and then commit the changes.

::

    git commit -a -m "Prepare for release: $THEBLUESRELEASE"


Create the release
------------------


Checkout the master branch, and merge develop into it. Verify that it passes
tests by running make check.

::

    git checkout master
    git merge develop
    make check


Tag the commit with the release number and push your changes to master on github.


::

    git tag $THEBLUESRELEASE
    git push origin master --tags


Head back to the develop branch and push it to the remote.

::

    git co develop
    git merge master
    git push origin develop

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

    make dist
    make upload

