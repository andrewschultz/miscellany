##############################
#
# alfit.pl
# alphabetizes first and last names
#

use strict;
use warnings;

alfnam("firsts");
alfnam("lasts");

sub alfnam
{
my %names;

open(A, "$_[0].txt");

print "Processing $_[0].txt\n";

open(A2, ">$_[0]-nd.txt");

print "Writing $_[0]-nd.txt\n"; 

while (my $line = <A>)
{
  chomp($line);
  if (!defined($names{$line})) { print A2 "$line\n"; }
  $names{$line} = 1;
}

close(A2);

print "Writing $_[0]-a.txt\n";

open(B, ">$_[0]-a.txt");

for my $x (sort keys %names) { print B "$x\n"; }

print "Writing $_[0]-l-a.txt\n";

open(C, ">$_[0]-l-a.txt");

for my $x (sort { length($a) <=> length($b) || $a cmp $b } keys %names) { print C "$x\n"; }

close(A);
close(B);
close(C);

print "Size of $_[0].txt: " . (-s "$_[0].txt") . "\n";
print "Size of $_[0]-nd.txt: " . (-s "$_[0]-nd.txt") . "\n";
print "Size of $_[0]-a.txt: " . (-s "$_[0]-a.txt") . "\n";
print "Size of $_[0]-l-a.txt: " . (-s "$_[0]-l-a.txt") . "\n";
}