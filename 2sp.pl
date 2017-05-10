######################################
#2sp.pl
#
#

use strict;
use warnings;

#####################options
my $difference = 0;
my $copy = 0;
my $makeDifFile = 1;

#####################variables
my $inI6 = 0;

my $dir = ".";

my $in = "$dir\\story.ni";
my $out = "$dir\\story.nsp";
my $dif = "$dir\\story.dif.txt";

open(A, $in);
open(B, ">$out");
if ($makeDifFile)
{
open(C, ">$dif");
}

while ($a = <A>)
{
  if ($a =~ /^-\)/) { $inI6 = 0; print B $a; next; }
  if ($a =~ /^Include \(-/i) { $inI6 = 1; print B $a; next; }
  if ($a =~ /^\[line break/) { print B $a; next; }

  $b = $a;

  if (!$inI6)
  {
  if ($b =~ /  /)
  {
  $b =~ s/  +/ /g;
  if ($makeDifFile)
  {
  print C "before:$a" . "after:$b";
  }
  }
  }
  print B $b;
}

close(A);
close(B);

if ($difference)
{
  `wm \"$in\" \"$out\"`;
}

if ($makeDifFile)
{
  close(C);
  `$dif`;
}

if ($copy)
{
  print "Copying $in to $out\n";
  `xcopy /y \"$in\" \"$out\"`;
}
