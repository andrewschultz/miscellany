##############################
#
#rgo.pl
#opens the line of a file for a room
#
#argument is room name or part of it
#
#line by default must be in the form PART [room] but you can change that
#
#at first it looks for

use strict;
use warnings;

#variables
my $lineTo;
my $backupLine;
my $tabLine;
my $roomSearch = 1;

my $search = "";

#parameter reading
my $count = 0;
my $rmOutline = "part";
my $gotParam = 0;

while ($count <= $#ARGV)
{
  my $arg = $ARGV[$count];
  for ($arg)
  {
    /^-?v$/ && do { $rmOutline = "volume"; $count++; next; };
    /^-?b$/ && do { $rmOutline = "book"; $count++; next; };
    /^-?p$/ && do { $rmOutline = "part"; $count++; next; };
    /^-?c$/ && do { $rmOutline = "chapter"; $count++; next; };
    /^-?s$/ && do { $rmOutline = "section"; $count++; next; };
	/^-?t$/ && do { $roomSearch = 0; $rmOutline = "table of"; $count++; next; };
	if ($arg =~ /^-/) { usage(); }
    if ($gotParam) { $search .= " $arg"; } else { $search = $arg; }
    $gotParam = 1;
	$count++;
  }
}

if (!$search) { die("Need a room string to go to."); }

#TODO: allow people to go to other directories

open(A, "story.ni");

while ($a = <A>)
{
  #if ($a =~ /^$search/i) { print "$. $a"; }
  if ($a =~ /^$rmOutline .*$search/i) { $backupLine = $.; }
  if (($a =~ /^$search[^\t]*?\t/i) && (!$tabLine)) { $tabLine = $.; }

  if ($roomSearch && ($a =~ /^$search ([a-z ])* is (a room in|(north|south|east|west|up|down|above|below|inside|outside) of)/i))
  {
    $lineTo = $.;
  }
}

close(A);

if ($backupLine && !$lineTo)
{
  print "Going with backup part (*) $search\n";
  $lineTo = $backupLine;
}

if ($tabLine && !$lineTo)
{
  print "Going with tab-line (*) $search\n";
  $lineTo = $tabLine;
}

if (!$lineTo) { die ("Didn't find string $search"); }
else
{
  my $cmd = "start \"\" \"C:/Program Files (x86)/Notepad++/notepad++.exe\" story.ni -n$lineTo";
  print "Running $cmd\n";
  `$cmd`;
}

#################################################
#subroutines

sub usage
{
print<<EOT;
Text strings are the rooms to search for. You can use spaces without quotes.
-v volume
-b book
-p part
-c chapter
-s section
EOT
exit()
}