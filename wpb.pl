########################################
#wpb.pl
#
#prints out all "when play begins" stuff to wpb.txt
#
#currently only reads from story.ni
#

use strict;
use warnings;

####################constants
my $wpb = "c:\\writing\\scripts\\wpb.txt";
my @partitions = ("volume", "book", "part", "chapter", "section");

########################variables
my %curLabel;
my $tr = 0;
my $temp;
my $count;
my $count2;

open(A, "story.ni") || die ("No story.ni");
open(B, ">$wpb");

while ($a = <A>)
{
  for $count (0..$#partitions)
  {
    if ($a =~ /^$partitions[$count] /i)
	{
	  $temp = $a;
	  chomp($temp);
	  $temp =~ s/^$partitions[$count] +//i;
	  $curLabel{$partitions[$count]} = $temp;
	  for $count2 ($count+1..$#partitions)
	  {
	    $curLabel{$partitions[$count2]} = "";
	  }
	  next;
	}
  }
  if ($a =~ /when play begins/)
  {
    $tr = 1;
	if ($a !~ /^when play begins/) { print B "*****TANGENTIAL REFERENCE "; }
    print B "Line $. (";

	for $count(0..$#partitions)
	{
	  if ($curLabel{$partitions[$count]}) { print B "$partitions[$count] $curLabel{$partitions[$count]}/"; }
	}

	print B ") = $a";
    next;
  }
  if ($tr) { print B $a; }
  if ($a !~ /[a-z]/) { $tr = 0; }
}

close(A);
close(B);

print "$wpb now has When Play Begins.\n";

if ($ARGV[0]) { print "Launching $wpb.\n"; `$wpb`; }