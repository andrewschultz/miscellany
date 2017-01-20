#####################################################
#naz.pl
#
#this file alphabetizes all the notes in notes9.otl and dumps them to notes-a-z.otl
#
#usage: no arguments
#

#die(strt(" lose memory, maybe lose some of the ways I bullshitted myself when I was younger to\n"));

use warnings;
use strict;

##################variables
my %nums;
my $inMain = 0;
my $dumpNext = 0;

my $in = "c:/writing/notes9.otl";
my $tin = "c:/writing/temp/notes9.otl";
my $out = "c:/writing/notes-a-z.otl";
my $tout = "c:/writing/temp/notes-a-z.otl";

open(A, "$in") || die ("Big oops no $in");
open(B, "$out") || die ("Big oops no $out");
open(C, ">$tin") || die ("Can't open $tin for writing");
open(D, ">$tout") || die ("Can't open $tout for writing");

while ($a = <A>)
{
  if ($a =~ /(ide=Basic Ideas|notes2|notes1)/i)
  {
    print C $a;
    $inMain = 1;
    next;
  }

  if (!$inMain) { print C $a; next; } # default, just print to notes file

  if ($a !~ /[0-9a-z]/i) { $inMain = 0; print C $a; next; } #final line of main notes

  $nums{strt($a)} .= $a;
}
close(A);
close(C);

while ($a = <B>)
{
  if ($a =~ /^\\ia/) { $dumpNext = $a; chomp($dumpNext); $dumpNext =~ s/^\\ia-//g; $dumpNext =~ s/=.*//g; }
  if (($dumpNext) && ($a !~ /[a-z0-9]/i))
  {
    print D $nums{$dumpNext};
	delete $nums{$dumpNext};
    $dumpNext = "";
  }
  print D $a;
}

close(B);
close(D);

byteSizeCheck();

################################
#prsz
#
#stub to print a file and its size
#
sub prsz
{
  print "$_[0]: " . (-s $_[0]) . "\n";
}

sub strt
{
  my $quo = $_[0];

  $quo =~ s/^[^0-9a-z]+//gi;
  $quo =~ s/^(a|an|the) //gi;
  $quo =~ s/^[^0-9a-z]+//gi;
  if ($quo !~ /^[0-9a-z]/i)
  {
    #die();
	die("$in Line probably needs a character or something:\n$_[0]$quo");
  }
  
  if ($quo =~ /^1 /) { return 1; }
  if ($quo =~ /^[0-9]/) { return "#"; }
  return lc(substr($quo, 0, 1));
}

##############################
#byteSizeCheck
#
#makes sure that we got all the strings over
sub byteSizeCheck
{
print "Byte size check:\n";
prsz($in);
prsz($out);
prsz($tin);
prsz($tout);

my $inBytes = (-s $in) + (-s $out);
my $outBytes = (-s $tin) + (-s $tout);

printf("%d + %d = %d\n%d + %d = %d\n", -s $in, -s $out, $inBytes, -s $tin, -s $tout, $outBytes);

for my $x (sort keys %nums)
{
  print "Didn't delete hash key $x\n$nums{$x}.\n";
}

if ($inBytes != $outBytes)
{
  print "In/out bytes don't match! Not copying over.";
  exit;
}
}
