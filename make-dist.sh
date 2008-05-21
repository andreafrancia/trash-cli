#!/bin/sh
trash dist
mkdir dist

version=0.1.9
svn export . dist/trash-"$version"

# create .tar.gz (sources)
tarball=dist/trash-"$version".tar.gz
tar cvfz "$tarball" dist/trash-"$version"

# create .rpm
python setup.py bdist_rpm
rpm="$(echo dist/*.noarch.rpm)"

# create .deb
cd dist
fakeroot alien *.noarch.rpm
deb="$(echo dist/*.deb)"

rsync -avP -e ssh "$tarball" andreafrancia@frs.sourceforge.net:uploads/
rsync -avP -e ssh "$rpm" andreafrancia@frs.sourceforge.net:uploads/
rsync -avP -e ssh "$deb" andreafrancia@frs.sourceforge.net:uploads/

echo "Go to https://sourceforge.net/project/admin/newrelease.php?package_id=179459&group_id=87144"

echo "New release name: trash-x.y.z"

