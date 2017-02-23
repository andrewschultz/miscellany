########################################
#wpb.pl
#
#prints out all "when play begins" stuff to wpb.txt
#

use strict;
use warnings;

my $wpb = "c:\\writing\\scripts\\wpb.txt";
open(A, "story.ni") || die ("No story.ni");
open(B, ">$wpb");

my $tr = 0;

while ($a = <A>)
{
  if ($a =~ /when play begins/) { $tr = 1; print B "Line: $.\n$a"; next; }
  if ($tr) { print B $a; }
  if ($a !~ /[a-z]/) { $tr = 0; }
}

close(A);
close(B);

print "$wpb now has When Play Begins.\n";

if ($ARGV[0]) { `$wpb`; }