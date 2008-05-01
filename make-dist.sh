#!/bin/sh
rm -fv dist/*
python setup.py sdist
python setup.py bdist
python setup.py bdist_rpm
cd dist; fakeroot alien *.noarch.rpm


ncftpput upload.sourceforge.net incoming trash_*_all.deb
ncftpput upload.sourceforge.net incoming trash-*.noarch.rpm
ncftpput upload.sourceforge.net incoming trash-*.tar.gz

echo "To publish the files do the followings:
Go to bluetrash on sourceforge.net 
        http://sourceforge.net/projects/bluetrash
and log in.


Go to Admin > File Releases 
click Add Release
 - Enter trash-x.y.z as release name
 - Follow the instructions.

"
