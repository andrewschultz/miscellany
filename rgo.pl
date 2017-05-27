##############################
#
#rgo.pl
#opens the line of a file for a room
#

use strict;
use warnings;

my $lineTo;
my $backupLine;

my $search = $ARGV[0];

my $rmOutline = "part";

if (!$search) { die("Need a room string to go to."); }

#TODO: allow people to go to other directories

open(A, "story.ni");

while ($a = <A>)
{
  #if ($a =~ /^$search/i) { print "$. $a"; }
  if ($a =~ /^$rmOutline .*$search/i) { $backupLine = $.; }

  if ($a =~ /^$search ([a-z ])* is (a room in|(north|south|east|west|up|down|above|below|inside|outside) of)/i)
  {
    $lineTo = $.;
  }
}

close(A);

if ($backupLine && !$lineTo)
{
  print "Going with backup part (*) $search";
  $lineTo = $backupLine;
}

if (!$lineTo) { die ("didn't find string $search"); }
else
{
  my $cmd = "start \"\" \"C:/Program Files (x86)/Notepad++/notepad++.exe\" story.ni -n$lineTo";
  print "Running $cmd\n";
  `$cmd`;
}
