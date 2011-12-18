# Copyright (C) 2007-2011 Andrea Francia Trivolzio(PV) Italy

base_version='0.2'

function inject_version() {
    file="$1"
    version="$2"
    sed --in-place s/version=\'svn\'/version=\'"$version"\'/ "$file"
}

set -e
rm -Rf dist
mkdir dist

requested_revision="$1"
# calc version 
if [ -z "$requested_revision" ]; then
        version="$base_version.$(svnversion)"
else 
        version="$base_version.$requested_revision"
fi

package_name="trash-cli-$version"
tarball=dist/"$package_name".tar.gz

# prepare sources
if [ -z "$requested_revision" ]; then
        svn export . dist/"$package_name"
else 
        svn export -r "$requested_revision" . dist/"$package_name"
fi

inject_version dist/"$package_name"/src/libtrash/__init__.py "$version"

# create tarball of sources
tar -C dist -cvz -f "$tarball" "$package_name"
rsync -avP -e ssh "$tarball" andreafrancia@frs.sourceforge.net:uploads/

echo "Go to https://sourceforge.net/project/admin/newrelease.php?package_id=179459&group_id=87144"

echo "New release name: trash-cli-$version"

