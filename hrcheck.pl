############################################
#hrcheck.pl (formerly sov.pl for stack overflow stuff)
#
#scheduling stuff, and stuff
#hrcheck.txt edited for what, when
#
#example of one line:
#
#11|FFX "http://www.thefreedictionary.com"
#
#Weekly thing
#5|8|FFX "http://btpowerhouse.com"

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
  my $cmdCount = 0;
  my $day = -1;
  my @b = split(/\|/, $line);
  if ($#b == 2)
  {
    $day = $b[0];
	if (($day >= 0) && ($day != $dayOfWeek)) { next; }
    $cmdCount++;
  }
  my $time = $b[$cmdCount];
  $cmdCount++;
  #print "$b[1]\n"; exit;
  $b[$cmdCount] =~ s/FFX/start "" "C:\\Program Files (x86)\\Mozilla Firefox\\firefox"/;
  $b[$cmdCount] =~ s/OPE/start "" "C:\\Program Files (x86)\\Opera\\launcher.exe"/;
  $b[$cmdCount] =~ s/CHR/start "" "C:\\Users\\Andrew\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe"/;
  if ($time == $hour) { print "Running $b[$cmdCount]\n"; `$b[$cmdCount]`; }
}

close(A);

sub usage
{
print<<EOT;
e = check stuff to check
c = check code
? (or anything else) = usage
EOT
exit;
}