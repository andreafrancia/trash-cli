How to build a release
======================

Update the version number::

    script/bump

Load the version in an environment variable::

    version="$(python setup.py --version)"

Run all tests::

    pytest

Create the tarball::

    python setup.py sdist

Upload to Test PyPI::

    twine upload --repository testpypi dist/*

Remove previous installation::

    python3 -m pip uninstall trash-cli

Test the installation::

    python3 -m pip install --index-url https://test.pypi.org/simple/ trash-cli

Register and upload::

    twine upload dist/*

Now you can tag the repo status::

    git tag "${version:?}"

Push the tag::

    git push --tags origin master

-EOF
