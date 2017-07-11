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
my $anyExtra = 0;
my @extraFiles = ();
#comment below out, or not, to change default behavior
$anyExtra = 1; @extraFiles = ($xtraFile);

my $allBookmarks = 0;
my $lastTime = "";
my $adjust = 0;
my $cmdCount = 0;
my $mod = 0;
my $cmd = "";
my $count = 0;
my $printOnly = 0;

my $overrideSemicolonEnd = 1;
my $semicolonSeen = 0;

my $popupIfAbort = 0;
my $gotImportantLine = 0;


my $autoBookmark = 0;
my $bookmarkLook = "";
my $bookmarkNote = 0;

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
  if (defined($ARGV[$count+1]))
  {
    $b = $ARGV[$count+1];
  }
  else
  {
    $b = "";
  }
  if (defined($ARGV[$count])) { $b = $ARGV[$count+1]; }
  for ($a)
  {
  /^[0-9]+:[0-9]+/ && do
  {
    my @time = split(/:/, $a);
	if ($time[0] > 24 or $time[0] < 0) { warn("Odd hour value, going to do the best I can.\n"); }
	$hourTemp = $time[0] % 24;
	$time[1] =~ s/[^0-9]*$//;
	if ($time[1] > 60 or $time[1] < 0) { warn("Odd minute value, going to do the best I can.\n"); }
	$minuteTemp = $time[1] % 60;
	$gotTime = 1; $count++; next;
  };
  /^(-|\+)?[0-9]+$/ && do { $adjust = $a; print "Adjusting time from current by $adjust minutes. Use : to try an exact time.\n"; $count++; next; };
  /^-pop/ && do { $popupIfAbort = 1; $count++; next; };
  /^-?is$/i && do { $overrideSemicolonEnd = 1; $count++; next; };
  /^-?f$/i && do { @extraFiles = (@extraFiles, split(/,/, $b)); $count+= 2; next; };
  /^-?h$/i && do { @extraFiles = (); $anyExtra = 0; $count++; next; };
  /^-?x$/i && do
  {
	if ($extraFiles[0] eq $xtraFile) { print "$xtraFile already in...\n"; } # very lazy coding but I don't plan to write in a lot of extra files
	else { @extraFiles = (@extraFiles, $xtraFile); $anyExtra = 1; }
	$count++; print "-ex edits the extras file.\n"; next;
  };
  /^-?o$/i && do { $printOnly = 1; $count++; next; };
  /^-?t(x)?$/i && do { searchHR($b, $a =~ /x/i); exit(); };
  /^-?ex$/i && do { $cmd = "start \"\" \"C:/Program Files (x86)/Notepad++/notepad++.exe\" $xtraFile"; `$cmd`; exit; };
  /^-?e$/i && do { $cmd = "start \"\" \"C:/Program Files (x86)/Notepad++/notepad++.exe\" $check"; `$cmd`; exit; };
  /^-?p$/i && do { $cmd = "start \"\" \"C:/Program Files (x86)/Notepad++/notepad++.exe\" $check2"; `$cmd`; exit; };
  /^-?c$/i && do { $cmd = "start \"\" \"C:/Program Files (x86)/Notepad++/notepad++.exe\" $code"; `$cmd`; exit; };
  /^-?ab$/i && do { $allBookmarks = 1; next; };
  /^-?b$/i && do { $bookmarkLook = $b; $count += 2; next; };
  /^=/i && do { $bookmarkLook = $a; $bookmarkLook =~ s/^=//; $count ++; next; };
  /^-?bp$/i && do { for ($check, $check2, $xtraFile) { printBkmk($_); } exit(); };
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
if (!$anyExtra) { print ("For critical stuff to run, you may wish to run -x.\n"); }
else { print ("If tests you don't want to run are popping up, you may wish to run -h.\n"); }

sub hrcheck
{
open(A, "$_[0]") || die ("No $_[0]");

print "Reading $_[0]...\n";

my $line;

my @qhr = (0, 0, 0, 0);

my $ignore = 0;

my @b;

my $months = 0;

my $ignoreHiddenBookmark = 0;

while ($line = <A>)
{
  chomp($line);
  if ($line =~ /^ABORT/i) { die ("Abort found in $_[0], line $.."); }
  if ($line =~ /^!!!!!!!!/ && (!$semicolonSeen)) { $gotImportantLine = 1; next; }
  if ($line =~ /^--/) { $ignore = 1; next; }
  if ($line =~ /^\+\+/) { $ignore = 0; next; }
  if ($line eq "==") { $autoBookmark = 0; $ignoreHiddenBookmark = 0; next; }
  if ($autoBookmark && ($line =~ /^=[^=]/)) { die ("Forgot to close with == before opening another = tab."); }
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
  if ($line =~ /^DEF=/)
  {
    $defaultBrowser = $line;
	$defaultBrowser =~ s/^DEF=//;
	next;
  }
  if ($bookmarkLook)
  {
    if ($line =~ /^=(\/)?$bookmarkLook[\W:]/) { $autoBookmark = 1; next; }
	if ($autoBookmark == 0) { next; }
  }
  elsif ($line =~ /^=\//) { $ignoreHiddenBookmark = 1; next; }
  elsif ($line =~ /^=/) { next; }
  $line =~ s/^\*+//;

  $months = ($line =~ /^m/i);
  $line =~ s/^m//i;

  @qhr = (1, 0, 0, 0);
  $mod = 0;
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

  print "Warning Line $. of $_[0] has no command defined.\n" if !defined($b[$cmdCount]);

  #print "$b[1]\n"; exit;
  if ($defaultBrowser && defined($b[$cmdCount]))
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
    if (($b[0] eq "*") || ($qhr[$min] || $tens[$min] || ($thistime < 0)) || $autoBookmark)
	{
      if (-f "$b[$cmdCount]" && ($b[$cmdCount] =~ /(txt|otl)$/i)) # skip over empty text file
      {
        if (-s "$b[$cmdCount]" == 0) { print "Skipping empty file $b[$cmdCount].\n"; next; }
      }
	  if ($b[0] eq "*") { print "WILD CARD: "; }
	  if ($printOnly)
	  {
	    print "Without -o, we would run $b[$cmdCount]\n";
	  }
	  else
	  {
	  if ($ignoreHiddenBookmark && !$allBookmarks) { print "Not running $b[$cmdCount]" . ($bookmarkNote ? "" : " (-ab to run this and others)" ) . "\n"; $bookmarkNote = 1; }
	  else
	  {
	  print "Running $b[$cmdCount]\n";
	  print `$b[$cmdCount]`;
	  }
	  }
	}
	last;
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
  if ($bookmarkLook) { return $autoBookmark; }
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

sub printBkmk
{
  open(A, $_[0]) || do { warn("$_[0] not found as an hrcheck file.\n"); return; };
  while ($a = <A>)
  {
    if ($a =~ /^=[^=]/) { chomp($a); if ($a =~ /^=\//) { print "HIDDEN: "; } $a =~ s/^=\//=/; print "$_[0]: $a\n"; }
  }
  close(A);
}

sub usage
{
print<<EOT;
-(#) or +(#) = add or substract minutes
b = looks for a bookmark to execute (so = stack overflow) (= also)
bp = prints all bookmarks
h = hide extra file if extra-default is on
e = check stuff to check (main file of tasks)
c = check code
p = check private file
ex = check extra file (side tasks, or ABSOLUTELY CRITICAL nightly stuff)
o = only print
t = search for text in the scheduling files
pop = popup if abort early
is = ignore semicolon for *'d entries
? (or anything else) = usage
EOT
exit;
}