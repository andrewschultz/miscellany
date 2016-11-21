##########################################
#
#comout.pl
#
#requires comout.txt
#

use strict;
use warnings;

my %proj;

############################options
my $afterComp;

############################variables
my $need = 4;
my $myproj = "slicker-city";
my $project;

my @projs;

my $comcfg = "c:\\writing\\scripts\\comout.txt";
my $comsou = "c:\\writing\\scripts\\comout.pl";

open(A, "$comcfg") || die ("No such file $comcfg.");

my $count = 0;
while ($count <= $#ARGV)
{
  for ($ARGV[$count])
  {
  /^-?[ef]$/i && do { `$comcfg`; exit(); };
  /^-?[a]$/i && do { $afterComp = 1; $count++; print "Opening WinDiff after...\n"; next; };
  /^-?[c]$/i && do { my $cmd = "start \"\" \"C:\\Program Files (x86)\\Notepad++\\notepad++.exe\" $comsou"; `$cmd`; exit(); };
  $myproj = $ARGV[$count];
  last;
  }
}

while ($a = <A>)
{
  if ($a =~ /^;/) { next; }
  if ($a =~ /^#/) { next; }

  if ($a =~ /^PROJ(ECT)?=/i)
  {
    $project = $a; chomp($project); $project =~ s/^PROJ(ECT)?=//gi; print "Active project $project,\n"; next;
  }
  if ($project) { $proj{$project} .= $a; print "$project added\n"; next; }  
}

if (not defined $proj{$myproj}) { die ("No project $myproj.\n"); }

@projs = split('\n', $proj{$myproj});

my $line;
my $match;

my $stor = "c:/games/inform/$project.inform/source/story";
my $inTable = 0;

close(A);

open(A, "$stor.ni") || die ("Can't open story file $stor.ni.\n");
open(B, ">$stor.22");

my $temp;

while ($line = <A>)
{
  if (($inTable == 1) && ($line !~ /[a-z]/i)) { print B "\]$line"; $inTable = 0; }
  print B $line;
  for $match (@projs)
  {
  if ($line =~ /^$match/)
  {
    for $temp (1..$need)
	{
	  $line = <A>;
	  if ($temp eq $need) { print B "\["; }
	  print B $line;
	  $inTable = 1;
	  next;
	}
  }
  }
}

if ($afterComp) { `wm $stor.ni $stor.22`; exit(); }