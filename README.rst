trash-cli - Command Line Interface to FreeDesktop.org Trash.
============================================================

|Donate|_

trash-cli trashes files recording the original path, deletion date, and 
permissions. It uses the same trashcan used by KDE, GNOME, and XFCE, but you 
can invoke it from the command line (and scripts).

It provides these commands::

    trash-put           trash files and directories. 
    trash-empty         empty the trashcan(s).
    trash-list          list trashed files.
    trash-restore       restore a trashed file.
    trash-rm            remove individual files from the trashcan.

Usage
-----

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

Restore a trashed file::
    
    $ trash-restore
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

Remove only the files that have been deleted more than <days> ago::
    
    $ trash-empty <days>

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

Remove only files matching a pattern::

    $ trash-rm \*.o

Note: you need to use quotes in order to protect the pattern from shell expansion.

FAQ
---

How to create a top level .Trash dir?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Steps ::

    sudo mkdir --parent /.Trash
    sudo chmod a+rw /.Trash
    sudo chmod +t /.Trash

Can I alias `rm` to `trash-put`?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can but you shouldn't. In the early days I thought it was a good idea to do
that but now I changed my mind. 

Although the interface of `trash-put` seems to be compatible with `rm`, it has
different semantics which will cause you problems. For example, while `rm`
requires `-R` for deleting directories `trash-put` does not.

But sometimes I forget to use `trash-put`, really can't I?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You could alias `rm` to something that will remind you to not use it::

    alias rm='echo "This is not the command you are looking for."; false'

Then, if you really want to use `rm`, simply prepend a slash to bypass the alias::

    \rm file-without-hope

Note that Bash aliases are used only in interactive shells, so using 
this alias should not interfere with scripts that expect to use `rm`.

Installation
------------

The easy way
~~~~~~~~~~~~

Requirements:

 - Python 3 (Python 2.7 may work)
 - pip (use `apt-get install python-pip` on Debian)

Installation command::
 
    pip install trash-cli

From sources
~~~~~~~~~~~~

System-wide installation::

    git clone https://github.com/andreafrancia/trash-cli.git
    cd trash-cli
    sudo pip install .

User-only installation::

    git clone https://github.com/andreafrancia/trash-cli.git
    cd trash-cli
    pip install .

After the user installation you may want add this line to your .bashrc::

    export PATH=~/.local/bin:"$PATH"

For uninstalling use::

    pip uninstall trash-cli

Bugs and feedback
-----------------

If you discover a bug please report it here:

    https://github.com/andreafrancia/trash-cli/issues

You can also email me to andrea@andreafrancia.it. On Twitter I'm @andreafrancia.

Development
-----------

Environment setup::

    virtualenv env --no-site-packages
    source env/bin/activate
    pip install -r requirements-dev.txt

Running tests::

    nosetests unit_tests           # run only unit tests
    nosetests integration_tests    # run all integration tests
    nosetests -A 'not stress_test' # run all tests but stress tests
    nosetests                      # run all tests

Check the installation process before release::

    python check_release_installation.py

Profiling unit tests::

    pip install gprof2dot
    nosetests --with-profile --profile-stats-file stats.pf --profile-restrict=unit_tests unit_tests
    gprof2dot -w  -f pstats stats.pf | dot -Tsvg >| stats.svg
    open stats.svg

.. |Donate| image:: https://www.paypalobjects.com/en_GB/i/btn/btn_donate_SM.gif
.. _Donate: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=93L6PYT4WBN5A

