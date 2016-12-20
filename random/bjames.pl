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
    /-/ && do { my @score = split(/-/, $a); $dif = $score[0] - $score[1]; if ($dif < 0) { $dif = - $dif; } $count++; next; };
	/^[0-9]+$/ && do { if ($a > 30) { $secs = $a; } else { $dif = $a; } $count++; next; };
    /[:,\.]/ && do { my @time = split(/[:,\.]/, $a); $secs = $time[0]*60 + $time[1]; $count++; next; };
    /[ny]/i && do { $haveBall = ($a =~ /y/i); $count++; next; };
    /b/i && do { $boths = 1; $count++; next; };
    usage();
  }
}

if (($haveBall == -1) && (!$boths)) { $haveBall = 0; print "Possession not specified, assuming THEM\n"; }

if ($secs < 0) { die("Can't have negative seconds!"); }

$dif = $dif - 3.5;

if ($boths) { print "WITH: "; bjames($dif+1); print "WITHOUT: "; bjames($dif); }
elsif ($haveBall) { bjames($dif+1); }
else { bjames($dif); }

sub bjames
{
my $safeness = 100 * $_[0]**2 / $secs;

if ($safeness > 100) { print "SAFE LEAD: actually, $safeness.\n"; }
else { print "NOT SAFE: $safeness\n"; }
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
EOT
exit;
}