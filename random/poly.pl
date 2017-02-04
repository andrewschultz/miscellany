#######################################
#
#poly.pl
#
#this is something from a HS project I always had in the back of my mind
#The 1st assignment of the class was to do a binary search for a polynomial root
#You could also do a weighted search or newtonian search for extra credit
#I always thought it was too complicated or silly and put it off but then I decided to look at it
#of course the newtonian misfires if the slope is 0 (basically we take the line tangent to the curve at one point and see where it hits 0)
#
#the algorithm is to calculate the midpoint, weighted mid and where the lower/higher end point to 0
#then look at the intervals created and choose the smallest one with a point above/below 0.
#there should always be one, and we will always cut the interval size by at least a half.
#
#obviously it's a bit easier in PERL than PASCAL but it's nice to be able to overcome old failures
#and I think it's a good project for learning any programming language
#
#also I could put in more parameters than just a polynomial but I've done that with other projects. The emphasis is on finding the roots here.

use warnings;
use strict;

my @poly = split(/,/, $ARGV[0]);

if ($#poly == -1) { die ( "Need polynomial!"); }

my $low = -100;
my $high = 100;

my $med;
my $wtMed;
my $slopeLow;
my $slopeHigh;

if (f($low) == 0) { die ("$low is a root.\n"); }
if (f($high) == 0) { die ("$low is a root.\n"); }

if ((f($high) > 0 ) == (f($low) > 0))
{
print f($high);
print "\n";

print f($low);
die ("No guaranteed root.");
}
my $turns = 0;

my @poss = ();
my $bound;
my $gap;
my $gapIdx;
my $delta = .1 ** 15;

while (($high - $low > $delta) && ($turns < 100))
{
  $turns++;
  $med = ($low + $high) / 2;
  $wtMed = (($low * f($high)) - ($high * f($low))) / (f($high) - f($low));
  @poss = ($low, $med, $wtMed, $high);
  if (deriv($low))
  {
    $slopeLow = $low - f($low)/deriv($low);
	if (($slopeLow > $low) && ($slopeLow < $high))
	{
	  push(@poss, $slopeLow);
	}
  }
  if (deriv($high))
  {
    $slopeHigh = $high - f($high)/deriv($high);
	if (($slopeHigh > $low) && ($slopeHigh < $high))
	{
	  push(@poss, $slopeHigh);
	}
  }
  @poss = sort {$a <=> $b} (@poss);
  $gap = $high - $low;
  for my $x(@poss) { print "$x = " . f($x) . "\n"; }
  $gapIdx = -1;
  for $bound (0..$#poss-1)
  {
    if (negOpp($poss[$bound], $poss[$bound+1]))
	{
	  #printf("%f %f %f %f\n", $poss[$bound], f($poss[$bound]), $poss[$bound+1], f($poss[$bound+1]));
	  if (($poss[$bound+1] - $poss[$bound]) < $gap)
	  {
	    $gap = $poss[$bound+1] - $poss[$bound];
		$gapIdx = $bound;
	  }
	}
  }
  if ($gapIdx == -1) { die ("Uh-oh, no new interval found. This is a big bug."); }
  $low = $poss[$gapIdx];
  $high = $poss[$gapIdx+1];
  
  print ("=" x 40);
  print "New range $low to $high.\n";
}

printf("%.6f is a root: %.6f", $med, f($med));

sub f
{
  my $sum = 0;
  my $idx;
  for $idx (0..$#poly)
  {
    $sum *= $_[0];
    $sum += $poly[$idx];
  }  
  return $sum;
}

sub deriv
{
  my $sum = 0;
  for (0..$#poly-1)
  {
  $sum *= $_[0];
  $sum += $poly[$_] * ($#poly-$_);
  }
  return $sum;
}

sub negOpp
{
  return ((f($_[0]) < 0) != (f($_[1]) < 0));
}