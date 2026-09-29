# How to create a new release

```shell
echo "Before continuing check if HISTORY.txt is updated!"

main_trash_cli_dir="$(pwd)"
# Open a branch in a new worktree
git worktree add ../trash-cli-new-release && cd ../trash-cli-new-release 

# Update the version number::
scripts/bump

# Launch GitHub Actions to check the release::
git push origin master

# Load the version in an environment variable::
version="$(python -c 'import setuptools; setuptools.setup()' --version)"

# Run all tests::
scripts/pre-push

# Create the tarball::
python -m build --sdist

# Check test::
twine check --strict "dist/trash_cli-$version.tar.gz"

# Upload to Test PyPI::
twine upload --repository testpypi "dist/trash_cli-$version.tar.gz"

# Remove previous installation::
python3 -m pip uninstall --yes trash-cli

# Test the installation::
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple trash-cli

# Register and upload::
python3 -m pip install twine
twine upload "dist/trash_cli-$version.tar.gz"

# Now you can tag the repo status::
git tag "${version:?}"
cd "$main_trash_cli_dir"

# Push the tag::
git push origin master "${version:?}"
```

-EOF
