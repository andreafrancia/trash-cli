============================================================
trash-cli - Command Line Interface to FreeDesktop.org Trash.
============================================================

trash-cli provides the following commands:

  * trash-put           trashes files and directories. 
  * trash-empty         empty the trashcan(s).
  * trash-list          list trashed file.
  * restore-trash       restore a trashed file.

For each file the name, original path, deletion date, and permissions
are recorded. The trash command allow trash multiple files with the 
same name. trash-cli uses the same trashcan of KDE, GNOME and XFCE.

Installation
============
Requirements:

 - python == 2.7 (2.6 may also work)
 - python-setuptools (e.g. apt-get install python-setuptools)

Installation:
 
 sudo easy_install trash-cli

Installation from sources
=========================

Install with::

  $ sudo python setup.py install

Usage
=====

Trash a file::

    $ trash-put foo

List trashed files::

    $ trash-list
    2008-06-01 10:30:48 /home/andrea/bar
    2008-06-02 21:50:41 /home/andrea/bar
    2008-06-23 21:50:49 /home/andrea/foo

Search for a file in the trashcan::

    $ trash-list | grep foo
    2007-08-30 12:36:00 /home/andrea/foo
    2007-08-30 12:39:41 /home/andrea/foo

Restore a trashed file
    
    $ restore-trash
    0 2007-08-30 12:36:00 /home/andrea/foo
    1 2007-08-30 12:39:41 /home/andrea/bar
    2 2007-08-30 12:39:41 /home/andrea/bar2
    3 2007-08-30 12:39:41 /home/andrea/foo2
    4 2007-08-30 12:39:41 /home/andrea/foo
    What file to restore [0..4]: 4
    $ ls foo
    foo

Remove all files from the trashcan::

    $ trash-empty

Remove only the files that have been deleted before <days> ago::
    
    $ trash-empy <days>

Example::

    $ date
    Tue Feb 19 20:26:52 CET 2008
    $ trash-list
    2008-02-19 20:11:34 /home/einar/today
    2008-02-18 20:11:34 /home/einar/yesterday
    2008-02-10 20:11:34 /home/einar/last_week
    $ trash-empty 7
    $ trash-list
    2008-02-19 20:11:34 /home/einar/today
    2008-02-18 20:11:34 /home/einar/yesterday
    $ trash-empty 1
    $ trash-list
    2008-02-19 20:11:34 /home/einar/today

Packages from Debian/Ubuntu
===========================

Don't use apt-get, this would install a very old version of trash-cli that 
contain a serious bug that could destroy your data.  Please, if you are 
interested, ask to Debian/Ubuntu to upgrade their version of trash-cli.

Information
===========

       Website: http://code.google.com/p/trash-cli/
 Download page: http://code.google.com/p/trash-cli/wiki/Download
Report bugs to: http://code.google.com/p/trash-cli/issues/list

Features list
=============

 - Command line interface compatible with on of the rm command. You can alias 
   rm with trash.
 - Remembers original path, deletion time and file permissions of each trashed 
   file.
 - Compatible with the KDE trash.
 - Implements the FreeDesktop.org Trash Specification
 - Works with volume other than the home volume (e.g. USB pen or another 
   partition).

Development
===========

Environment setup::

    virtualenv env --no-site-packages
    source env/bin/activate
    pip install -r requirements.txt -r requirements-dev.txt

Running tests::

    nosetests unit_tests                # unit tests
    nosetests integration_tests         # integration tests
    nosetests                           # run all tests

Profiling unit tests::

    pip install gprof2dot
    nosetests --with-profile --profile-stats-file stats.pf --profile-restrict=unit_tests unit_tests
    gprof2dot -w  -f pstats stats.pf | dot -Tsvg >| stats.svg
    open stats.svg

