
my $count = 0;

while ($count <= $#ARGV)
{
  $a = $ARGV[$count];

  for ($a)
  {
    /-/ && do { @score = split(/-/, $a); $dif = @score[0] - @score[1]; if ($dif < 0) { $dif = - $dif; } $count++; next; };
    /:/ && do { @time = split(/:/, $a); $secs = @time[0]*60 + @time[1]; $count++; next; };
    /[ny]/i && do { $haveBall = ($a =~ /y/i); $count++; next; };
    usage();
  }
}

$dif = $dif - 2.5;

if ($haveBall) { $dif++; }

$formula = 100 * $dif**2 / $secs;

if ($formula > 100) { print "SAFE LEAD: actually, $formula.\n"; }
else { print "NOT SAFE: $formula\n"; }

sub usage()
{
print "Bad argument $a\n";
print<<EOT;
Usage: score time (has ball) e.g. 78-60 3:45 n/y
EOT
exit;
}