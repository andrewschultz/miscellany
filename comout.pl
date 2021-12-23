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
my $cmd;
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
  my $arg = $ARGV[$count];
  for ($arg)
  {
  /^-?n?[0-9]+/ && do { $need = $arg; $need =~ s/^-?n?//g; $count++; next; };
  /^-?[ef]$/i && do { `$comcfg`; exit(); };
  /^-?[a]$/i && do { $afterComp = 1; $count++; print "Opening WinDiff after...\n"; next; };
  /^-?[c]$/i && do { $cmd = "start \"\" \"C:\\Program Files\\Notepad++\\notepad++.exe\" $comsou"; `$cmd`; exit(); };
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

my $stor = "c:\\games\\inform\\$project.inform\\source\\story";
my $inTable = 0;

close(A);

open(A, "$stor.ni") || die ("Can't open story file $stor.ni.\n");
open(B, ">$stor.22");

my $temp;

if ($need)
{
while ($line = <A>)
{
  if (($inTable == 1) && ($line !~ /[a-z]/i)) { print B "\]$line"; $inTable = 0; next; }
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
}
else
{
while ($line = <A>)
{
  if (($inTable == 1) && ($line !~ /[a-z]/)) { print B "\n"; $inTable = 0; next; }
  if (($inTable == 1) && ($line =~ /^\[/)) { $line =~ s/^\[//; }
  if ($line =~ /^\[?table of /) { $inTable = 1; }
  print B $line;
  next;
}
}

$cmd = "copy /Y $stor.22 $stor.ni";
print "$cmd\n";
my $q = `$cmd`;
print $q;

if ($afterComp) { `wm $stor.ni $stor.22`; exit(); }