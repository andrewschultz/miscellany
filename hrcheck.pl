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
#
#tphb = quarter hours
#:(0-5) = 0 past, 10 past, etc.

use strict;
use warnings;
use POSIX;

my $check = "c:\\writing\\scripts\\hrcheck.txt";
my $check2 = "c:\\writing\\scripts\\hrcheckp.txt";
my $code = "c:\\writing\\scripts\\hrcheck.pl";

my $lastTime = "";
my $adjust = 0;
my $cmdCount = 0;
my $mod = 0;

my @times;
my $thistime;

my %browsMap;

$browsMap{"FFX"} = "\"C:\\Program Files (x86)\\Mozilla Firefox\\firefox\"";
$browsMap{"OPE"} = "\"C:\\Program Files (x86)\\Opera\\launcher.exe\"";
$browsMap{"CHR"} = "\"C:\\Users\\Andrew\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe\"";

my $min;

my @quarters  = ("t", "p", "h", "b");
my @tens = (0, 0, 0, 0, 0, 0);

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

my $ignore = 0;

my @b;

while ($line = <A>)
{
  if ($line =~ /^ABORT/i) { die ("Abort found in $_[0], line $.."); }
  if ($line =~ /^--/) { $ignore = 1; next; }
  if ($line =~ /^\+\+/) { $ignore = 0; next; }
  if ($line =~ /^#/) { next; }
  if ($line =~ /^;/) { last; }
  if ($ignore) { next; }
  chomp($line);
  @qhr = (1, 0, 0, 0);
  $mod = 0;
  if ($line =~ /^DEF=/)
  {
    $defaultBrowser = $line;
	$defaultBrowser =~ s/^DEF=//;
	next;
  }
  $cmdCount = 0;
  my $min = 0;
  @b = split(/\|/, $line);
  if ($b[0] eq '"') { $b[0] = $lastTime; $b[0] =~ s/\|.*//; }
  if ($#b == 2)
  {
    my @q = split(/,/, $b[0]);
	my $gotOne = 0;
	for (@q)
	{
	  if ($dayOfWeek == $_)
	  {
	    #print "$line: today\n";
		$gotOne = 1;
      }
    }
	if (!$gotOne) { next; }
    $cmdCount++;
  }
  @times = split(/,/, $b[$cmdCount]);
  
  $cmdCount++;
  
  for $thistime (@times)
  {

  if ($thistime =~ /[m]$/) { $mod = $thistime; $mod =~ s/.*m//g; }
  
  ######################quarter hours
  if ($thistime =~ /[tphb]$/)
  {
    @qhr[0] = 0;
    while ($thistime =~ /[tphb]$/)
    {
      for (0..3)
 	  {
	    if ($thistime =~ /$quarters[$_]$/)
	    {
	      $qhr[$_] = 1;
		  $thistime =~ s/.$//;
        }
      }
    }
  }
  #this needs to be outside the loop so it registers
  $min = floor($minute/15);
 
  if ($thistime =~ /:/)
  {
    @tens = (0, 0, 0, 0, 0, 0);
	my @totens = split(/:/, $thistime);
	$thistime =~ s/:.*//;
	for (1..$#totens) { $tens[$totens[$_]] = 1; }
	$min = floor($minute/10);
  }

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
  if (validHour($thistime))
  {
    #print "$hour, $times[$#times] good so far ($min): @qhr, @tens.\n";
    if (($b[0] eq "*") || ($qhr[$min] || $tens[$min] || ($thistime < 0)))
	{
      if (-f "$b[$cmdCount]" && ($b[$cmdCount] =~ /(txt|otl)$/i)) # skip over empty text file
      {
        if (-s "$b[$cmdCount]" == 0) { print "Skipping empty file $b[$cmdCount].\n"; next; }
      }
	  if ($b[0] eq "*") { print "WILD CARD: "; }
	  print "Running $b[$cmdCount]\n";
	  print `$b[$cmdCount]`;
	}
  }
  }

  if ($lastTime ne '"')
  {
    $lastTime = $b[0];
  }
}

close(A);
}

sub validHour
{
  if ($_[0] eq "*") { return 1; }
  my @ha = split(/,/, $hour);
  for my $h (@ha)
  {
  if ($_[0] == $h) { return 1; }
  if ($_[0] < 0)
  {
    my $mult = - $_[0];
	if (($h * 2 + floor($minute/30)) % $mult == $mod) { return 1; }
  }
  }
  return 0;
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