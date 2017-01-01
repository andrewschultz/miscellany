##########################################
#gt.pl
#
#go to something to search for
#

use strict;
use warnings;

my $default = "buck-the-past";
my $file = "";

if (-f "story.ni") { $file = "story.ni"; }
else
{
  print "No story.ni, looking for $default.\n";
  $file = "c:\\games\\inform\\$default.inform\\Source\\story.ni";
}

open(A, "$file") || die ("No $file, bailing.");

#############################counters
my $line;

#############################variables
my $getLine = 0;
my $sr = $ARGV[0];


if ($sr =~ /^[0-9]+$/)
{ $getLine = $sr; }
else
{
while ($line = <A>)
{
  if ($line =~ /$sr/)
  {
    $getLine = $.;
    last;
  }
}
}

close(A);

system("start \"\" \"C:\\Program Files (x86)\\Notepad++\\notepad++.exe\" \"$file\" -n$getLine"); exit;