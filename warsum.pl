##############################
#
#warsum.pl
#
#warnings summary so it doesn't go on for one whole screen
#
#usage is generally with another file e.g.
#
#tofix.pl 2>&1 | warsum.pl
#
#to add: what's in what function(s)

use warnings;
use strict;

my %count;
my %low;
my %high;

my $c;

print "Note if you're not, run this with ws.bat to save a few keystrokes.\n";

while ($a = <STDIN>)
{
  chomp($a);
  $b = $a;
  $b =~ s/.* line //;
  $c = $b; $c =~ s/\.//;
  $a =~ s/^Global symbol \"//; $a =~ s/\".*//;
  if (!$low{$a}) { $low{$a} = $c; $high{$a} = $c; }
  else
  {
    if ($c < $low{$a}) { $low{$a} = $c; }
    if ($c > $high{$a}) { $high{$a} = $c; }
  }
  $count{$a}++;
  #print "$a\n";
}

for my $key (sort keys %low)
{
  print "$key covers $low{$key} to $high{$key}, $count{$key} incidences.\n";
}