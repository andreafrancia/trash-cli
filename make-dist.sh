#!/bin/sh

python setup.py sdist
python setup.py bdist
python setup.py bdist_rpm
cd dist; fakeroot alien *.noarch.rpm
