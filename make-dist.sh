#!/bin/sh

python setup.py sdist
python setup.py bdist
python setup.py bdist_rpm
cd dist; fakeroot alien *.noarch.rpm

echo "To publish the files do the followings:

  $ cd dist/
  $ ncftp ftp://upload.sourceforge.net/incoming/
  ncftp /incoming > put trash-0.1.6-1.noarch.rpm
  ncftp /incoming > put trash_0.1.6-2_all.deb
  ncftp /incoming > put trash-0.1.6.tar.gz
  ncftp /incoming > quit
  $

Go to bluetrash on sourceforge.net and log in.

Go to Admin > File Releases 
click Add Release
 - Enter trash-x.y.z as release name
 - Follow the instructions.

"
