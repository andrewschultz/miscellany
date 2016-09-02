use strict;

use warnings;

my $file = "sok.txt";

my @orig = ("U", "R", "D", "L");

my @rot = (0, 1, 2, 3);
my @xrot = @rot;

my %r2;

my $r = 0;
my $h = 0;

my $temp;

for my $argcount(0..$#ARGV)
{
$a = $ARGV[$argcount];

if ($a =~ /^[rdhv]+$/i)
{
  my @a = split(//, $ARGV[$argcount]);
  for (@a)
  {
    /l/i && do { if ($h) { $r++; } else { $r--; } next; };
    /r/i && do { if ($h) { $r--; } else { $r++; } next; };
    /h/i && do { $h = !$h; next; };
    /v/i && do { $h = !$h; $r += 2; next; };
    print "Unknown character $_.\n";
  }
}
else
{
$file = $a;
}
}

$r %= 4;

for (1..$r) { push (@xrot, shift(@xrot)); }

if ($h) { $temp = $xrot[1]; $xrot[1] = $xrot[3]; $xrot[3] = $temp; }

print "$r rotations, $h horizontal flips: @xrot\n";

for (0..3)
{
  $r2{$orig[$_]} = $orig[$xrot[$_]];
}

open(A, "sok.txt") || die ("No sok.txt.");

while ($a = <A>)
{
  print "Orig: $a";
  print "NEW:: ";
  $a =~ s/\b([0-9\*]*)([URDL])\b/$1 . newdir($2)/ge;
#  $a =~ s/\b([0-9\*]*)([URDL])\b/$1newdir($2)/ge;
  print $a;
}

sub newdir
{
  return $r2{$_[0]};
}