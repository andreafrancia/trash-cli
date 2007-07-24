# Copyright (C) 2005 Andrea Francia <andreafrancia@users.sourceforge.net>
#  
# This file is free software; as a special exception the author gives
# unlimited permission to copy and/or distribute it, with or without 
# modifications, as long as this notice is preserved.
# 
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY, to the extent permitted by law; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
bin_PROGRAMS = atomic_create curl_escape curl_unescape
bin_SCRIPTS = trash list-trashcan 
CLEANFILES = $(bin_SCRIPTS)
EXTRA_DIST = trash.bash common.bash head.bash list-trashcan.bash

trash: $(srcdir)/trash.bash $(srcdir)/../version.sh common.bash head.bash
	rm -f trash
	cat head.bash > trash
	cat common.bash >> trash
	cat $(srcdir)/trash.bash >> trash
	chmod ugo+x trash

list-trashcan: $(srcdir)/list-trashcan.bash $(srcdir)/../version.sh $(srcdir)/common.bash head.bash
	rm -f list-trashcan
	cat head.bash > list-trashcan
	cat common.bash >> list-trashcan
	cat $(srcdir)/list-trashcan.bash >> list-trashcan
	chmod ugo+x list-trashcan



curl_escape_SOURCES = curl_escape.c
curl_escape_LDADD = -lcurl

curl_unescape_SOURCES = curl_unescape.c
curl_unescape_LDADD = -lcurl

atomic_create_SOURCES = atomic_create.c
