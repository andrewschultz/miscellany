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
my $code = "c:\\writing\\scripts\\hrcheck.pl";

my ($second, $minute, $hour, $dayOfMonth, $month, $yearOffset, $dayOfWeek, $dayOfYear, $daylightSavings) = localtime(time);

my %browsMap;

$browsMap{"FFX"} = "\"C:\\Program Files (x86)\\Mozilla Firefox\\firefox\"";
$browsMap{"OPE"} = "\"C:\\Program Files (x86)\\Opera\\launcher.exe\"";
$browsMap{"CHR"} = "\"C:\\Users\\Andrew\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe\"";

my @quarters  = ("t", "p", "h", "b");

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

my @qhr = (0, 0, 0, 0);

my $defaultBrowser = "";

while ($line = <A>)
{
  chomp($line);
  @qhr = (1, 0, 0, 0);
  if ($line =~ /^DEF=/)
  {
    $defaultBrowser = $line;
	$defaultBrowser =~ s/^DEF=//;
	next;
  }
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

sub usage
{
print<<EOT;
e = check stuff to check
c = check code
? (or anything else) = usage
EOT
exit;
}