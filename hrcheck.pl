############################################
#hrcheck.pl
#
#scheduling stuff, and stuff
#hrcheck.txt edited for what, when
#

my $check = "c:\\writing\\scripts\\hrcheck.txt";

($second, $minute, $hour, $dayOfMonth, $month, $yearOffset, $dayOfWeek, $dayOfYear, $daylightSavings) = localtime(time);

if ($ARGV[0] eq "e") { `$check`; exit; }

open(A, "$check") || die ("No $check");
while ($a = <A>)
{
  chomp($a);
  @b = split(/\|/, $a);
  $time = @b[0];
  print @b[0];
  if ($time == $hour) { print "Running @b[1]\n"; `@b[1]`; }
}

close(A);
