Prepare for the release
-----------------------

Clone a fresh copy from the root repo. Do not attempt a release in your
current working repository as the following commands expect a fresh clone.

::

     git clone git@github.com:juju/theblues.git
     cd theblues



Generate changelog
------------------
We structure merge commit messages to be a short summary of the change. As such
you can get a quick log of all the major changes since the last release with
`git log`.  You can find the last release by looking in the `.bumpversion` file.

::

    vim CHANGELOG.rst
    git log $last-release...HEAD --merges

Use the output from that to update the changelog with the major changes of the
release.


Update the master branch and test
---------------------------------

Checkout the master branch, and merge develop into it. Verify that it passes
tests by running make check.

::

    git checkout master
    git merge develop
    make check

Increment the version
---------------------

To just increment the patch level (e.g. 0.2.0 ->
0.2.1) just run

::

    make bumpversion

To increment the minor (e.g. 0.2.2 -> 0.3.0) run

::

    VPART=minor make bumpversion

To increment the major (e.g. 0.2.2 -> 1.0.0) run

::

    VPART=major make bumpversion


Create the release
------------------

At this point the version is incremented, committed to git, and tagged.  Push
the changes upstream.

::

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
    repository=https://pypi.python.org/pypi
    username={{your_username}}
    password={{your_password}}

    [pypitest]
    repository=https://testpypi.python.org/pypi
    username={{your_username}}


Then you can publish the release to pipy,

::

    make dist
    make upload

Upload the release to Github
----------------------------

Go to the tags_ page in Github and find the release that should have been
generated from your tag. If you do not see it, ensure you pushed your tag when
you pushed your other changes.

Go to the proper release, and click `Edit release notes`. Update the release
notes to match the changelog you put in CHANGELOG.rst. Set the name to be the
tag name.

Upload the release tarball you created in the binaries field.

.. _tags: https://github.com/juju/theblues/tags
