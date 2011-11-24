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

Usage
=====

  Trash a file::

    $ trash-put /home/andrea/foobar

  List trashed files::

    $ trash-list
    2008-06-01 10:30:48 /home/andrea/bar
    2008-06-02 21:50:41 /home/andrea/bar
    2008-06-23 21:50:49 /home/andrea/foo

  Restore a trashed file::

    $ trash-restore /home/andrea/foo

  Empty the trashcan::

    $ trash-empty

Information
===========

       Website: http://code.google.com/p/trash-cli/
 Download page: http://code.google.com/p/trash-cli/wiki/Download
Report bugs to: http://code.google.com/p/trash-cli/issues/list

Installation
============
See the INSTALL file.

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

