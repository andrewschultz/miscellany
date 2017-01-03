##########################################
#gt.pl
#
#go to something to search for
#

use strict;
use warnings;

my $default = "buck-the-past";
my $file = "";
my $cur = 0;

if ($ARGV[0] eq "g") { $cur++; $file = "c:\\writing\\games.otl"; }

if ((!$file) && (-f "story.ni")) { $file = "story.ni"; }
elsif (! -f $file)
{
  print "No story.ni/games.otl, looking for $default.\n";
  $file = "c:\\games\\inform\\$default.inform\\Source\\story.ni";
}

open(A, "$file") || die ("No $file, bailing.");

#############################counters
my $line;

#############################variables
my $getLine = 0;
my $sr = $ARGV[$cur];


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

if (!$getLine) { print "String not found, just opening $file.\n"; }

system("start \"\" \"C:\\Program Files (x86)\\Notepad++\\notepad++.exe\" \"$file\" -n$getLine"); exit;