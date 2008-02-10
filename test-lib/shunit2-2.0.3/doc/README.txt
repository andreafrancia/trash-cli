#------------------------------------------------------------------------------
# SourceForge
#

This project is stored on SourceForge as http://sf.net/projects/shunit2. The
source code can be accessed using the following information.

* Subversion
$ svn co https://shunit2.svn.sourceforge.net/svnroot/shunit2/trunk/source shunit2

Subversion may also be browsed via a web browser at
http://svn.sourceforge.net/shunit2

#------------------------------------------------------------------------------
# Making a release
#

For these steps, it is assumed we are working with release 2.0.0.

Steps:
* write release notes
* update version
* finish changelog
* check all the code in
* tag the release
* export the release
* create tarball
* md5sum the tarball and sign with gpg
* update website
* post to SourceForge and Freshmeat

WRITE RELEASE NOTES

This should be pretty self explainatory. Use one of the release notes from a
previous release as an example.

To get the versions of the various shells, do the following:
Cygwin
  bash:  $ bash --version
  ksh:   actually pdksh
  pdksh: look in the downloaded Cygwin directory
Linux
  bash:  $ bash --version
  dash:  look at installed version
  ksh:   $ ksh --version
  pdksh: $ strings /bin/pdksh |grep 'PD KSH'
  zsh:   $ zsh --version
Solaris 10
  sh:    not possible
  bash:  $ bash --version
  ksh:   $ strings /usr/bin/ksh |grep 'Version'

UPDATE VERSION

Edit the shunit2 source code, and change the version number in the comment, as
well as in the __SHUNIT_VERSION variable. Next, edit the
src/docbook/shunit2.xml file, edit the version in the <title> element, and make
sure there is a revision section for this release.

FINISH DOCUMENTATION

Make sure that any remaning changes get put into the CHANGES-X.X.txt file.

Finish writing the RELEASE_NOTES-X.X.X.txt. Once it is finished, run it through
the 'fmt' command to make it pretty.

$ fmt -w 80 RELEASE_NOTES-2.0.0.txt >RELEASE_NOTES-2.0.0.txt.new
$ mv RELEASE_NOTES-2.0.0.txt.new RELEASE_NOTES-2.0.0.txt

We want to have an up-to-date version of the documentation in the release, so
we'd better build it.

$ pwd
.../shunit2/source/2.0
$ make docs
...
$ cp -p build/shunit2.html doc
$ svn ci -m "" doc/shunit2.html

CHECK IN ALL THE CODE

This step is pretty self-explainatory

TAG THE RELEASE

$ pwd
.../shunit2/source
$ ls
2.0  2.1
$ svn cp -m "Release 2.0.0" \
2.0 https://shunit2.svn.sourceforge.net/svnroot/shunit2/tags/source/2.0.0

EXPORT THE RELEASE

$ pwd
.../shunit2/builds
$ svn export \
https://svn.sourceforge.net/svnroot/shunit2/tags/source/2.0.0 shunit2-2.0.0

CREATE TARBALL

$ tar cfz ../releases/shunit2-2.0.0.tgz shunit2-2.0.0

MD5SUM THE TARBALL AND SIGN WITH GPG

$ cd ../releases
$ md5sum shunit2-2.0.0.tgz >shunit2-2.0.0.tgz.md5
$ gpg --default-key kate.ward@forestent.com --detach-sign shunit2-2.0.0.tgz

UPDATE WEBSITE

Again, pretty self-explainatory. Make sure to copy the MD5 and GPG signature
files. Once that is done, make sure to tag the website so we can go back in
time if needed.

$ pwd
.../shunit2
$ ls
source  website
$ svn cp -m "Release 2.0.0" \
website https://shunit2.svn.sourceforge.net/svnroot/shunit2/tags/website/20060916

Now, copy the website into place

$ rsync -aP --delete --exclude '.svn' website/ sf.net:www/projects/shunit2

POST TO SOURCEFORGE AND FRESHMEAT

http://sourceforge.net/projects/shunit2/
http://freshmeat.net/

#------------------------------------------------------------------------------
# Related documentation
#

Docbook XML
  docbook-xml-4.4.zip
    http://www.docbook.org/xml/4.4/docbook-xml-4.4.zip
    http://www.oasis-open.org/docbook/xml/4.4/docbook-xml-4.4.zip
  docbook-xml-4.5.zip
    http://www.docbook.org/xml/4.5/docbook-xml-4.5.zip

Docbook XSL
  docbook-xsl-1.71.0.tar.bz2
    http://prdownloads.sourceforge.net/docbook/docbook-xsl-1.71.0.tar.bz2?download
  docbook-xsl-1.71.1.tar.bz2
    http://downloads.sourceforge.net/docbook/docbook-xsl-1.71.1.tar.bz2?use_mirror=puzzle

JUnit
  http://www.junit.org


$Revision: 64 $
