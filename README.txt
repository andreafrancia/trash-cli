------------------------------------------------------------
trash-cli - Command Line Interface to FreeDesktop.org Trash.
------------------------------------------------------------

trash-cli provides the following commands to manage the trash:

  * trash-put          trashes files and directories. 
  * trash-empty         empty the trashcan(s).
  * trash-list          list trashed file.
  * trash-restore       restore a trashed file.
  * trash-admin         administrate trashcan(s).

For each file the name, original path, deletion date, and permissions 
are recorded. The trash command allow trash multiple files with the 
same name. trash-cli uses the same trashcan of KDE, GNOME and XFCE.

Usage
-----
        Trash a file:
          $ trash-put /home/andrea/foobar

        List trashed files:
          $ trash-list
          2008-06-01 10:30:48 /home/andrea/bar
          2008-06-02 21:50:41 /home/andrea/bar
          2008-06-23 21:50:49 /home/andrea/foo

        Restore a trashed file:
          $ trash-restore /home/andrea/foo

        Empty the trashcan:
          $ trash-empty

Informations
------------
       Website: http://code.google.com/p/trash-cli/
 Download page: http://code.google.com/p/trash-cli/wiki/Download
Report bugs to: http://code.google.com/p/trash-cli/issues/list

Installation
------------
See the INSTALL file.

Software requirements
---------------------
The trash-cli software depends on these packages:
 - python
 - python-ctypes

And from these python packages
 - enum

Testing the software
--------------------
See the TEST file.

-EOF
