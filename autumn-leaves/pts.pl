##############################
# pts.pl
# this is a big conglomerator to see how many "points" you start with in Autumn Leaves.

use strict;
use warnings;

my @found = (0) x 11;
my @c;

my $q, my $x;
my $count = 0;
my $cur = 0;

my $hiValue = 21;

for (0..5) { $c[$_] = $hiValue - $_; }

while ($c[0] >= 5)
{

  processPoints();
  if ($c[5] > 0) { $c[5]--; }
  else
  {
    $count = 4;
    while (($c[$count] - $c[$count+1] == 1) && ($count > 0)) { $count--; }
    $c[$count]--;
    #if ($count == 0) { print "$c[$count]\n"; }
    for $x ($count..4)
    {
    $c[$x+1] = $c[$x] - 1;
    }
  }
}

for (0..$#found)
{
  if ($found[$_]) { $q = sprintf("or 1 in %.4f", $cur / $found[$_]);} else { $q = ""; }
  printf("$_: %d/%d=%.4f%% $q\n", $found[$_], $cur, 100*$found[$_]/$cur);
}

sub processPoints
{
  $cur++;
  my @suit = (0) x 52;
  if ($cur % 100000 == 0) { print "@c $cur\n"; }
  my $points = 0;
  my $pts = 0;
  for (0..4) { if (($c[$_] - $c[$_+1] == 1) && ($c[$_] % 13)) { $points++; } }
  #print "1st count @c has $points\n";
  for $x (0..5)
  {
    $suit[$c[$x]-$c[$x]%13]++;
  }
  for (0..$#suit)
  {
    if ($suit[$_] > 1) { $pts += ($suit[$_] - 1); }
  }
  #print "@c: $points, $pts from array @suit\n";
  $found[$points+$pts]++;
}