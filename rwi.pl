###################################
#
#rwi.pl
#
#find rule with (string) in it
#
#very crude but part of my utilities

use strict;
use warnings;

my $openAfter = 1;
my $gotRule = 0;

open(A, "story.ni") || die ("No story.ni.");
open(B, ">rwi.txt") || die ("Unwritable rwi.txt.");

while ($a = <A>)
{
  if (($a =~ /^[a-z]/) && ($a =~ /$ARGV[0].*:/))
  {
    print B "Line $.:\n";
    $gotRule = 1;
  }
  if ($gotRule) { print B $a; }
  if ($a !~ /[a-z]/) { $gotRule = 0; }
}

close(A);
close(B);

if ($openAfter) { `rwi.txt`; }