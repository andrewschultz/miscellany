##########################################
#
#bjames.pl
#
#this tells us whether a lead is Bill James safe or not
# (diff + .5 * (have ball)) squared / (time remaining)
#

use strict;
use warnings;

my $count = 0;
my $dif = 0;
my $secs = 0;
my $haveBall = -1;
my $boths = 0;

my $temp;

if ($#ARGV == -1) { usage(); }

while ($count <= $#ARGV)
{
  $a = $ARGV[$count];

  for ($a)
  {
    /^-?r/ && do { $temp = $a; $temp =~ s/^-?r//; listReverse($temp); exit(); };
    /[0-9]-[0-9]/ && do { my @score = split(/-/, $a); $dif = $score[0] - $score[1]; if ($dif < 0) { $dif = - $dif; } $count++; next; };
	/^-?[0-9]+$/ && do { if ($a < 0) { $a = -$a; print"Assuming nonnegative lead/time.\n"; } if ($a > 30) { $secs = $a; print "Assuming $a seconds.\n"; } else { $dif = $a; print "Assuming $a deficit.\n"; } $count++; next; };
    /[;:,\.]/ && do { my @time = split(/[;:,\.]/, $a); $secs = $time[0]*60 + $time[1]; $count++; next; };
    /[ny]/i && do { $haveBall = ($a =~ /y/i); $count++; next; };
    /b/i && do { $boths = 1; $count++; next; };
    usage();
  }
}

if (($haveBall == -1) && (!$boths)) { $boths = 1; print "Possession not specified, assuming BOTH\n"; }

if ($secs < 0) { die("Can't have negative seconds!"); }

$dif = $dif - 3.5;

if ($boths) { print "WITH: "; bjames($dif+1); print "WITHOUT: "; bjames($dif); }
elsif ($haveBall) { bjames($dif+1); }
else { bjames($dif); }

sub bjames
{
my $safeness = 100 * $_[0]**2 / $secs;

  if ($safeness > 100)
  {
    print "SAFE LEAD: actually, $safeness.\n";
  }
  else
  {
    my $delta = $secs - $_[0]**2 + .25;
    printf("NOT SAFE: $safeness | TIME DELTA: %d:%02d\n", $delta / 60, $delta % 60);
  }
}

sub listReverse
{
  my $listMax = 10;
  if ($_[0]) { $listMax = $_[0]; }
  my $temp;
  for ($temp=0; $temp <= $listMax; $temp++)
  {
    my $temp2 = $temp - 3.5; if ($temp2 < 0) { $temp2 = 0; }
	my $needSafe = ($temp2) ** 2;
	printf("$temp: %d:%02d\n", $needSafe / 60, $needSafe % 60);
  }
}

sub usage
{
if ($#ARGV == -1) { print "No arguments, giving help.\n"; } else { print "Bad argument $a\n"; }
print<<EOT;
Usage:
Score time (has ball) e.g. 78-60 3:45 n/y/b (whether leading team has ball, b = both)
You can also just give the differential
The app guesses if a number is time left (>30) or not
EOT
exit;
}