use strict;
use warnings;

my $count = 0;
my $dif = 0;
my $secs = 0;
my $haveBall = -1;

while ($count <= $#ARGV)
{
  $a = $ARGV[$count];

  for ($a)
  {
    /-/ && do { my @score = split(/-/, $a); $dif = $score[0] - $score[1]; if ($dif < 0) { $dif = - $dif; } $count++; next; };
    /:/ && do { my @time = split(/:/, $a); $secs = $time[0]*60 + $time[1]; $count++; next; };
    /[ny]/i && do { $haveBall = ($a =~ /y/i); $count++; next; };
    usage();
  }
}

if ($haveBall == -1) { $haveBall = 0; print "Possession not specified, assuming THEM\n"; }

if ($secs < 0) { die("Can't have negative seconds!"); }

$dif = $dif - 2.5;

if ($haveBall) { $dif++; }

my $safeness = 100 * $dif**2 / $secs;

if ($safeness > 100) { print "SAFE LEAD: actually, $safeness.\n"; }
else { print "NOT SAFE: $safeness\n"; }

sub usage
{
print "Bad argument $a\n";
print<<EOT;
Usage: score time (has ball) e.g. 78-60 3:45 n/y
EOT
exit;
}