#!/bin/sh

function get_version() {
    base_version='0.1.10'
    scm_version="$(svnversion)"
    echo "$base_version.$scm_version"
}

function inject_version() {
    file="$1"
    version="$2"
    sed --in-place s/version=\'svn\'/version=\'"$version"\'/ "$file"
}

set -e
if [ -e dist ]; then
	mv -b dist old.dist
fi

mkdir dist

version="$(get_version)"
package_name="trash-cli-$version"
tarball="$package_name".tar.gz

# prepare sources
svn export . dist/"$package_name"
inject_version dist/"$package_name"/libtrash.py "$version"

# create tarball of sources
tar -C dist -cvz -f "$tarball" "$package_name"
rsync -avP -e ssh "$tarball" andreafrancia@frs.sourceforge.net:uploads/

echo "Go to https://sourceforge.net/project/admin/newrelease.php?package_id=179459&group_id=87144"

echo "New release name: trash-$version"

