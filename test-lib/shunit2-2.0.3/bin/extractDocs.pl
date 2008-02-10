#! /usr/bin/perl
# $Id: extractDocs.pl 12 2007-02-18 03:31:14Z sfsetse $

if(@ARGV != 1) {
   print "usage: $0 sourceFile\n";
   exit;
}

$sourceFile = $ARGV[0];

#
# read in the source file
#
$rslt = open(FILE, $sourceFile)
  || die "could not open file ($sourceFile)";

$inComment = 0;
while(<FILE>) {
  next if /^[^#]/;
  s/^# //;
  s/^#//;

  if(/^\/\*\*/) {
    $inComment = 1;
    next;
  }
  if(/\*\/$/) {
    $inComment = 0;
    next;
  }

  if ($inComment == 1) { print $_ };
  if ($inComment == 0 && /\/\/\*/) {
    @line = split /\/\/\*/, $_, 2;
    $line[1] =~ s/^ //;
    print $line[1];
  }
}

close(FILE);
