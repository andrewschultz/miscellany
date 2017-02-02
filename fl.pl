##############################################
# lf.pl
# last-or-first
#

use strict;
use warnings;

my $count = 0;

my $first = 1;
my $last = 1;

my @searchies;

while ($count <= $#ARGV)
{
  my $arg = $ARGV[$count];
  for ($arg)
  {
  /^-b$/ && do { $first = 1; $last = 1; $count++; next; };
  /^-f$/ && do { $first = 1; $last = 0; $count++; next; };
  /^-l$/ && do { $first = 0; $last = 1; $count++; next; };
  push(@searchies, $arg); $count++;
  }
}

if ($#ARGV == -1) { @searchies = ("jim"); print ("Using default $searchies[0].\n"); }

my $endStr = "";
my @endAry;

for (@searchies)
{
  @endAry = ();
  if ($first) { namelook("c:/writing/dict/firsts.txt", "first", "f", $_); }
  if ($last) { namelook("c:/writing/dict/lasts.txt", "last", "l", $_); }
  $endStr = join(",", sort(@endAry));
  if ($endStr) { print "Best matches:$endStr\n"; }
}

sub namelook
{
  my $p = "($_[2])";
  my $mainStr = "";
  my @mainAry = ();

  open(A, "$_[0]") || die ("No $_[0]");
  while ($a = <A>)
  {
    if (($a =~ /^$_[3]/i) || ($a =~ /$_[3]$/i)) { chomp($a); push(@endAry, "$a$p"); next;}
    if (($a =~ /$_[3]/i) && ($a !~ /[0-9]/)) { chomp($a); push(@mainAry, "$a$p"); }
  }
  $mainStr = join(",", sort(@mainAry));
  if ($mainStr) { print "Anywhere for $_[1]:$mainStr\n"; }
  close(A);
}