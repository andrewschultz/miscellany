################################################
#ru.pl
#
#finds where code text is in a rule, or a rule header
#
#sort of antiquated but still worth it

use strict;
use warnings;

my $inHead = 1;
my $inCode = 0;
my $count = 0;

my @match;

while ($count <= $#ARGV)
{

$a = $ARGV[$count];
  print "Trying $count $a\n";

for ($a)
{
  /^-c/ && do { $inCode = 1; $count++; next; };
  /^-nc/ && do { $inCode = 0; $count++; next; };
  /^-h/ && do { $inHead = 1; $count++; next; };
  /^-nh/ && do { $inHead = 0; $count++; next; };
  if ($#match == 1) { print "Only 2 search arguments allowed.\n"; exit; }
  else { push(@match, $a); }
  $count++;
}

}

open(A, "story.ni") || die ("No story.ni.");

my $funcBlock = "";
my $thisValid = 0;
my $head = "";

while ($a = <A>)
{
  chomp($a);
  if ($a =~ /^[a-z]/)
  {
    chomp($a); $head = $a; if (($inHead) && itMatches($a)) { print "$.: $a\n"; } $funcBlock = $a;
  }
  elsif ($inCode && itMatches($a))
  {
    print "$.: $a (found in $head)\n";
	$thisValid = 1;
  }

  if ($a !~ /[a-z]/)
  {
    if ($thisValid) { print "$funcBlock\n"; $thisValid = 0; }
    $funcBlock = "";
  }

}

sub itMatches
{
  if (($#match == 0) && ($a =~ /$match[0]/i)) { return 1; }
  if (($#match == 1) && ($a =~ /$match[0]/i) && ($a =~ /$match[1]/i)) { return 1; }
  return 0;
}