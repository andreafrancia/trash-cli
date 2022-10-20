How to build a release
======================

Update the version number::

    scripts/bump

Load the version in an environment variable::

    version="$(python -c 'import setuptools; setuptools.setup()' --version)"

Run all tests::

    pytest

Create the tarball::

    python -m build --sdist

Upload to Test PyPI::

    twine upload --repository testpypi "dist/trash-cli-${version}.tar.gz"

Remove previous installation::

    python3 -m pip uninstall --yes trash-cli

Test the installation::

    python3 -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple trash-cli

Register and upload::

    twine upload dist/trash-cli-${version}.tar.gz

Now you can tag the repo status::

    git tag "${version:?}"

Push the tag::

    git push --tags origin master

-EOF
