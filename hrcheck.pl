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
use Win32;
use POSIX qw (floor);

my $check = "c:\\writing\\scripts\\hrcheck.txt";
my $check2 = "c:\\writing\\scripts\\hrcheckp.txt";
my $code = "c:\\writing\\scripts\\hrcheck.pl";

my $xtraFile = "c:\\writing\\scripts\\hrcheckx.txt";

my $lastTime = "";
my $adjust = 0;
my $cmdCount = 0;
my $mod = 0;
my $cmd = "";
my $count = 0;

my @extraFiles = ();

my $overrideSemicolonEnd = 1;
my $semicolonSeen = 0;

my $popupIfAbort = 0;
my $gotImportantLine = 0;

my @times;
my $thistime;

my %browsMap;

$browsMap{"FFX"} = "\"C:\\Program Files (x86)\\Mozilla Firefox\\firefox\"";
$browsMap{"OPE"} = "\"C:\\Program Files (x86)\\Opera\\launcher.exe\"";
$browsMap{"CHR"} = "\"C:\\Users\\Andrew\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe\"";

my $min;

my @quarters  = ("t", "p", "h", "b");
my @tens = (0, 0, 0, 0, 0, 0);
my $gotTime, my $hourTemp, my $minuteTemp;

while ($count <= $#ARGV)
{
  $a = $ARGV[$count];
  if (defined($ARGV[$count])) { $b = $ARGV[$count+1]; }
  for ($a)
  {
  /^[0-9]+:[0-9]+$/ && do { my @time = split(/:/, $a); $hourTemp = $time[0]; $minuteTemp = $time[1]; $gotTime = 1; $count++; next; };
  /^(-|\+)?[0-9]+$/ && do { $adjust = $a; $count++; next; };
  /^-pop/ && do { $popupIfAbort = 1; $count++; next; };
  /^-?is$/i && do { $overrideSemicolonEnd = 1; $count++; next; };
  /^-?f$/i && do { @extraFiles = (@extraFiles, split(/,/, $b)); $count+= 2; next; };
  /^-?x$/i && do { @extraFiles = (@extraFiles, $xtraFile); $count++; next; };
  /^-?t(x)?$/i && do { searchHR($b, $a =~ /x/i); exit(); };
  /^-?e$/i && do { $cmd = "start \"\" \"C:/Program Files (x86)/Notepad++/notepad++.exe\" $check"; `$cmd`; exit; };
  /^-?p$/i && do { $cmd = "start \"\" \"C:/Program Files (x86)/Notepad++/notepad++.exe\" $check2"; `$cmd`; exit; };
  /^-?c$/i && do { $cmd = "start \"\" \"C:/Program Files (x86)/Notepad++/notepad++.exe\" $code"; `$cmd`; exit; };
  usage();
  }
}

my ($second, $minute, $hour, $dayOfMonth, $month, $yearOffset, $dayOfWeek, $dayOfYear, $daylightSavings) = localtime(time + $adjust * 60);
if ($gotTime)
{
  $hour = $hourTemp;
  $minute = $minuteTemp;
}

my $defaultBrowser = "";

hrcheck($check);

if (($popupIfAbort) && (!$gotImportantLine))
{
  Win32::MsgBox("Remember to remove any semicolons for debugging, so HRCHECK reads in everything!");
}

hrcheck($check2);

for my $tocheck (@extraFiles)
{
  hrcheck($tocheck);
}

sub hrcheck
{
open(A, "$_[0]") || die ("No $_[0]");

print "Reading $_[0]...\n";

my $line;

my @qhr = (0, 0, 0, 0);

my $ignore = 0;

my @b;

my $months = 0;

while ($line = <A>)
{
  if ($line =~ /^ABORT/i) { die ("Abort found in $_[0], line $.."); }
  if ($line =~ /^!!!!!!!!/ && (!$semicolonSeen)) { $gotImportantLine = 1; next; }
  if ($line =~ /^--/) { $ignore = 1; next; }
  if ($line =~ /^\+\+/) { $ignore = 0; next; }
  if ($line =~ /^#/) { next; }
  if ($semicolonSeen)
  {
    if (($overrideSemicolonEnd) && ($line =~ /^\*/))
	{
	}
	else
	{
	  next;
	}
  }
  if ($line =~ /^;/) { $semicolonSeen = 1; next; }
  if ($ignore) { next; }
  chomp($line);
  $line =~ s/^\*+//;

  $months = ($line =~ /^m/i);
  $line =~ s/^m//i;

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
  my $lineMod = $line;
  if ($lineMod =~ /^\"/)
  {
  $lineMod =~ s/\"/$lastTime/;
  }
  else
  {
  $lastTime = $line;
  $lastTime =~ s/\|[^\|]*$//;
  #print "Last time prefix = $lastTime\n";
  }
  @b = split(/\|/, $lineMod);
  if ($#b == 2)
  {
    my @q = split(/,/, $b[0]);
	my $gotOne = 0;
	for (@q)
	{
	  if (($dayOfWeek == $_) && ($months == 0))
	  {
		$gotOne = 1;
      }
	  if (($dayOfMonth == $_) && ($months == 1))
	  {
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

  if ($line !~ /^\"/)
  {
    $lastTime = $line;
    #print "Last time before $lastTime\n";
	$lastTime =~ s/\|[^\|]*$//;
    #print "Last time after $lastTime\n";
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

sub searchHR
{
  my @files = ($check, $check2, $xtraFile);

  for (@files)
  {
  open(A, "$_");
  while ($a = <A>)
  {
	if ($_[1] && ($a =~ /\b$_[0]\b/i)) { print "$_ ($.): $a"; }
	if (!$_[1] && ($a =~ /$_[0]/i)) { print "$_ ($.): $a"; }
  }
  close(A);
  }
}

sub usage
{
print<<EOT;
-(#) or +(#) = add or substract minutes
e = check stuff to check
c = check code
p = check private file
pop = popup if abort early
is = ignore semicolon for *'d entries
? (or anything else) = usage
EOT
exit;
}