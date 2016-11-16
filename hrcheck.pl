############################################
#hrcheck.pl
#
#scheduling stuff, and stuff
#hrcheck.txt edited for what, when
#
#example of one line:
#
#11|start "" "C:\Program Files (x86)\Mozilla Firefox\firefox" "http://www.thefreedictionary.com"
#

use strict;
use warnings;

my $check = "c:\\writing\\scripts\\hrcheck.txt";
my $code = "c:\\writing\\scripts\\hrcheck.pl";

my ($second, $minute, $hour, $dayOfMonth, $month, $yearOffset, $dayOfWeek, $dayOfYear, $daylightSavings) = localtime(time);

if (defined($ARGV[0]))
{
if ($ARGV[0] eq "e")
{
  my $cmd = "start \"\" \"C:/Program Files (x86)/Notepad++/notepad++.exe\" $check";
  `$cmd`;
  exit;
}

if ($ARGV[0] eq "c")
{
  my $cmd = "start \"\" \"C:/Program Files (x86)/Notepad++/notepad++.exe\" $code";
  `$cmd`;
  exit;
}
usage();
}

open(A, "$check") || die ("No $check");

my $line;

while ($line = <A>)
{
  chomp($line);
  if ($line =~ /^#/) { next; }
  my @b = split(/\|/, $line);
  my $time = $b[0];
  if ($time == $hour) { print "Running $b[1]\n"; `$b[1]`; }
}

close(A);

sub usage
{
print<<EOT;
e = check stuff to check
c = check code
EOT
exit;
}