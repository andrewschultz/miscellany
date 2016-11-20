##########################################
#
#comout.pl
#
#requires comout.txt

use strict;
use warnings;

my %proj;

my $need = 4;
my $myproj = "slicker-city";
my $project;

my @projs;

open(A, "c:/writing/scripts/comout.txt");

while ($a = <A>)
{

  if ($a =~ /^;/) { next; }
  if ($a =~ /^#/) { next; }

  if ($a =~ /^PROJ=/i)
  {
    $project = $a; chomp($project); $a =~ s/^PROJ=//gi; next;
  }
  if ($project) { $proj{$project} .= $a; next; }  
}

if (defined($ARGV[0])) { $myproj = $ARGV[0]; }

if (not defined $proj{$myproj}) { die ("No project $myproj.\n"); }

@projs = split($proj{$myproj});

my $line;
my $match;

my $stor = "c:/games/inform/$project.inform/source/story";
my $inTable = 0;

open(A, "$stor.ni") || die ("Can't open story file $stor.ni.\n");
open(B, ">$stor.22");

my $temp;

while ($line = <A>)
{
  if (($inTable == 1) && ($line !~ /[a-z]/i)) { print B "\]$a"; }
  print B $line;
  for $match (@projs)
  {
  if ($line =~ /$match/)
  {
    for $temp (1..$need)
	{
	  $line = <A>;
	  print B $line;
	  print B "\[";
	  $inTable = 1;
	  next;
	}
  }
  }
}

