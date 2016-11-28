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
use POSIX;

my $check = "c:\\writing\\scripts\\hrcheck.txt";
my $check2 = "c:\\writing\\scripts\\hrcheckp.txt";
my $code = "c:\\writing\\scripts\\hrcheck.pl";

my $adjust = 0;

my %browsMap;

$browsMap{"FFX"} = "\"C:\\Program Files (x86)\\Mozilla Firefox\\firefox\"";
$browsMap{"OPE"} = "\"C:\\Program Files (x86)\\Opera\\launcher.exe\"";
$browsMap{"CHR"} = "\"C:\\Users\\Andrew\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe\"";

my @quarters  = ("t", "p", "h", "b");

if (defined($ARGV[0]))
{
if ($ARGV[0] =~ /^(-|\+)?[0-9]+$/) { $adjust += $ARGV[0]; }
elsif ($ARGV[0] eq "e" || $ARGV[0] eq "-e")
{
  my $cmd = "start \"\" \"C:/Program Files (x86)/Notepad++/notepad++.exe\" $check";
  `$cmd`;
  exit;
}
elsif ($ARGV[0] eq "p" || $ARGV[0] eq "-p")
{
  my $cmd = "start \"\" \"C:/Program Files (x86)/Notepad++/notepad++.exe\" $check2";
  `$cmd`;
  exit;
}
elsif ($ARGV[0] eq "c" || $ARGV[0] eq "-c")
{
  my $cmd = "start \"\" \"C:/Program Files (x86)/Notepad++/notepad++.exe\" $code";
  `$cmd`;
  exit;
}
else
{
usage();
}
}

my ($second, $minute, $hour, $dayOfMonth, $month, $yearOffset, $dayOfWeek, $dayOfYear, $daylightSavings) = localtime(time + $adjust * 60);

my $defaultBrowser = "";

hrcheck($check);
hrcheck($check2);

sub hrcheck
{
open(A, "$_[0]") || die ("No $_[0]");

my $line;

my @qhr = (0, 0, 0, 0);

while ($line = <A>)
{
  if ($line =~ /^ABORT/i) { die ("Abort found in $_[0], line $.."); }
  if ($line =~ /^#/) { next; }
  if ($line =~ /^;/) { last; }
  chomp($line);
  @qhr = (1, 0, 0, 0);
  if ($line =~ /^DEF=/)
  {
    $defaultBrowser = $line;
	$defaultBrowser =~ s/^DEF=//;
	next;
  }
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

  ######################quarter hours
  if ($time =~ /[tphb]$/) { @qhr[0] = 0; }
  while ($time =~ /[tphb]$/)
  {
    for (0..3) { if ($time =~ /$quarters[$_]$/) { $qhr[$_] = 1; $time =~ s/.$//; } }
  }
  my $min = floor($minute/15);
  $cmdCount++;

  #print "$b[1]\n"; exit;
  if ($defaultBrowser)
  {
  $b[$cmdCount] =~ s/^DEF/$defaultBrowser/;
  }
  for my $q (keys %browsMap)
  {
  my $name_idx = index $b[$cmdCount], $q;
  if ($name_idx >= 0)
  {
  substr ($b[$cmdCount],
  $name_idx,
  length($q),
  $browsMap{$q} );
  }
  }
  if ($time == $hour)
  {
    if ($qhr[$min])
	{
      if (-f "$b[$cmdCount]" && ($b[$cmdCount] =~ /(txt|otl)$/i)) # skip over empty text file
      {
        if (-s "$b[$cmdCount]" == 0) { print "Skipping empty file $b[$cmdCount].\n"; next; }
      }
	  print "Running $b[$cmdCount]\n";
	  print `$b[$cmdCount]`;
	}
  }
}

close(A);
}

sub usage
{
print<<EOT;
e = check stuff to check
c = check code
p = check private file
? (or anything else) = usage
EOT
exit;
}