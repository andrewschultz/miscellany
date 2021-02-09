###############################################
#
# a.pl: goes through the daily files and makes sure they're arranged correctly
#
# obsolete now since dff.py and dgrab.py do the job better
#

use File::Copy;
use Win32::Clipboard;

use strict;
use warnings;

my $lastDay = 0;

my $clip = Win32::Clipboard::new();

my $betterDie;
my $openOnWarn = 0;
my $warns = 0;
my $bigErrs = 0;
my @allDailyFiles = ();
my $justCheck;
my $clipboard;
my $debug;
my $numLim = 0;
my $curIdx = 0;
my $count;
my $theMax = 0;
my $theMin = 0;
my $defFar;
my $filesToTry = 0;
my $printToErrorFile = 0;
my $allBack;
my $verifyHeadings;
my $bigWarn;
my $warning = "";
my $checkHeaders;
my $inDir = "";
my $fileToOpen = "";
my $bailFileToOpen = "";
my $showOK = 0; my $showProc = 0; my $showFile = 0; my $showWarn = 0;
my $onlyLim = 0;
my $viewErrorFile = 0;
my $openFile = 0;
my $headString = 0;
my $thisDay = "";
my $thisFile = "";
my $testing = 0;
my $testErrList = "";

my @badFiles = ();
my @goodFiles = ();

my %vh; # this is to verify headers

setGlobals();

my %mapTo = ();
my %sortOrd = ();

my $elog = "c:\\writing\\daily\\errlog.txt";

processTabs();

while ($ARGV[$count])
{
  my $mya = $ARGV[$count];
  my $myb = defined($ARGV[$count+1]) ? $ARGV[$count+1] : 0;
  for ($mya)
  {
    /^-?2h/ && do
	{
	  my $wriout = "c:\\writing\\scripts\\daily-results.htm";
	  my $cmd = "a.pl -180 -a | perl -pe \"s/^/<br \\\/>/g\" > $wriout";
	  `$cmd`;
	  `$wriout`;
	  exit();
	};
    /^-?[0-9]/ && do { $theMax = $mya; if ($theMax le 0) { $theMax = 0 - $theMax; } $count++; next; };
	/^-a$/ && do { $allBack = 1; $count++; next; };
	/^-b$/ && do { $inDir="c:/users/andrew/dropbox/daily"; $count++; next; };
	/^-c$/ && do { $justCheck = 1; $count++; next; };
	/^-cb$/ && do { $clipboard = 1; $count++; next; };
	/^-d$/ && do { $debug = 1; $count++; next; };
	/^-le$/ && do { `$elog`; exit; };
	/^-ef$/ && do { $printToErrorFile = 1; $count++; next; };
	/^-ev$/ && do { $printToErrorFile = 1; $viewErrorFile = 1; $count++; next; };
	/^-eo$/ && do { $justCheck = 1; $verifyHeadings = 0; $theMax = 200; $allBack = 1; $showOK = $showProc = 0; $openFile = 1; $inDir="c:/users/andrew/dropbox/daily"; $count++; next; };
	/^-eh$/ && do { $justCheck = 1; $verifyHeadings = 0; $theMax = 200; $allBack = 1; $showOK = $showProc = 0; $openFile = 1; $inDir="c:/writing/daily"; $count++; next; };
	/^-f$/ && do { $justCheck = 0; $count++; next; };
	/^-h$/ && do { $checkHeaders = 1; $allBack = 1; $headString = $ARGV[$count+1]; if (!$headString) { die ("Need a string to check.\n"); } $count+=2; next; };
	/^-l$/ && do { $onlyLim = 1; $count++; next; };
	/^-ma$/ && do { $theMax = $myb; $count += 2; next; };
	/^-mi$/ && do { $theMin = $myb; $count += 2; next; };
	/^-n$/ && do { $openFile = 0; $count++; next; };
	/^-nh$/ && do { $verifyHeadings = 0; $count++; next; };
	/^-nw$/ && do { $showWarn = 0; $count++; next; };
	/^-q$/ && do { $showOK = $showWarn = 0; $count++; next; };
	/^-o$/ && do { $openFile = 1; $count++; next; };
	/^-ow$/ && do { $openFile = 1; $openOnWarn = 1; $count++; next; };
	/^-t$/ && do { $testing = 1; $count++; next; };
	/^-u$/ && do { $allBack = 1; $count++; if ($theMax == $defFar) { $theMax = 90; } next; };
	/^-sp$/ && do { $showProc = 1; $count++; next; };
	/^-[hn]p$/ && do { $showProc = 0; $count++; next; };
	/^-w$/ && do { $showOK = 0; $count++; next; };
	/^-v(h)?$/ && do { $verifyHeadings = 1; $count++; next; };
	usage();
  }
}

if ($printToErrorFile) { open(EL, ">$elog"); }

if ($justCheck == 1) { print ("Run with -f to clean any file(s) up. Or -a for all. (-)# for a specific # of days, default = $defFar.\n"); }

if ($verifyHeadings)
{
  open(A, "c:/writing/ideahash.txt");
  while (my $line = <A>)
  {
    chomp($line); $line =~ s/ +=.*//g; $vh{"\\$line"} = 1;
  }
  close(A);
}

  if ($theMin > $theMax) { die("min $theMin > max $theMax"); }

  for $thisDay ($theMin..$theMax)
  {
    $thisFile = daysAgo($thisDay);
	if (-f $thisFile)
	{
	  my $thatFile = $thisFile;
	  $thatFile =~ s/.*[\\\/]//g;
	  push(@allDailyFiles, $thatFile);
	  $lastDay = $thisDay+1;
	  processDaily($thisFile, $thisDay);
	  if (!$allBack) { exit; }
    }
  }

@allDailyFiles = sort(@allDailyFiles);

if ($onlyLim) { print "$numLim limericks in $lastDay days.\n"; }
else
{
  local $" = ", ";
  print "" . (scalar @allDailyFiles) . " daily files in $lastDay days: @allDailyFiles.\n";
  if (scalar @allDailyFiles > 1)
  {
  if (scalar @goodFiles)
  {
  print "" . (scalar @goodFiles) . " good file(s): @goodFiles.\n";
  }
  else
  {
  print "No files passed.\n";
  }
  if (scalar @badFiles)
  {
  print "" . (scalar @badFiles) . " bad file(s): @badFiles.\n";
  }
  else
  {
  print "No bad files!\n";
  }
  }
}

testResults();

if(!fileno(EL)) { close(EL); } if ($viewErrorFile) { `$elog`; }

exit;

sub daysAgo
{
my $temp = time();

$curIdx = 0;

my $i = $ARGV[0];

(my $second, my $minute, my $hour, my $dayOfMonth, my $month, my $yearOffset, my $dayOfWeek, my $dayOfYear, my $daylightSavings) = localtime($temp - 86400*$_[0]);

my $c = sprintf("$inDir/%s%02d%02d.txt", $yearOffset+1900, $month+1, $dayOfMonth);

return $c;

}

sub processTabs
{
  open(T, "c:/writing/scripts/a.txt") || die ("Can't find c:/writing/scripts/a.txt");
  while ($a = <T>)
  { chomp($a);
    my @b = split(/\t/, $a);
	my @c = split(/,/, $b[0]);
	for my $me (@c) { $mapTo{"\\$me"} = $c[0]; $sortOrd{"\\$me"} = $b[1]; }
  } ##for $x (sort keys %mapTo) { print "$mapTo{$x} =~ $sortOrd{$x}\n"; } for $x (sort keys %sortOrd) { print "$mapTo{$x} =~ $sortOrd{$x}\n"; } die;
  close(T);
}

sub processDaily
{
  if ($checkHeaders)
  {
    findHeader($_[0]);
	return;
  }
  $betterDie = 0;

  if (! -f $_[0]) { return; }
  if ($debug) { print ("$_[0] exists.\n"); }

  if (isUnix($_[0])) { printExt("$_[0] is probably a unix file.\n"); return; }
  if (-s $_[0] == 0) { printExt("Zero byte file $_[0], skipping.\n"); return; }

  my $shortName = $_[0]; $shortName =~ s/.*[\\\/]//g;

  my %startLine;

  open(A, "$_[0]");

  my @myHdr = ();

  my $gotNames = 0;

  $bigWarn .= $warning;
  $warning = "";

  my $limericks = 0;
  my $lineToGo = 0;
  my @myAry;

 if ($showProc) { print "Processing $_[0], $_[1] days ago...\n"; }

 if ($onlyLim) { processLim($_[0]); return; }

my $hasSomething = 0;

 while (my $line = <A>)
{
  if (($line =~ /[a-z]/i) && ($line !~ /^\\/)) { $hasSomething = 1; }
  $b = $line; chomp($b);
  if ($line =~ /====/) { $limericks = 1; }
  if ($line =~ /\\nam/) { $gotNames = 1; }
  if (($curIdx > 0) && (!defined($myAry[$curIdx])) && ($line !~ /\\/))
  {
    if (($line !~ /[a-z]/) && ($showWarn)) { $warns++; $warning .= "  WARNING extra carriage return at line $. of $shortName.\n"; if ($openOnWarn) { $fileToOpen = $_[0]; $betterDie = 1; $lineToGo = $.; } next; } #this is to make sure that double carriage returns don't bomb out;
    printErrExt("You don't have a header in $shortName ($.): $line");
    if (($openFile) && (!$fileToOpen)) { $fileToOpen = $_[0]; }
	$betterDie++;
  }
  if ($line =~ /^\\/)
  { if (lc($b) ne $b) { if ($showWarn) { $warns++; $warning .= "WARNING header $b not in lower case.\n"; } }
    $b = lc($b);
    if ($myAry[$curIdx]) { printErrExt("Header needs spacing: $line"); $betterDie++;   $fileToOpen = $_[0]; }
	else { if ($startLine{$b}) { printErrExt ("    $shortName: $b: line $. duplicates line $startLine{$b}.\n"); $betterDie++; if (!$lineToGo) { $lineToGo = $.; }
      #if (($openFile) && (!$fileToOpen))
	  { $fileToOpen = $_[0]; }
	} else { $startLine{$b} = $.; } $myHdr[$curIdx] = $b; if ((!$vh{$b}) && ($verifyHeadings)) { $warns++; $warning .= "  $shortName BAD HEADER: $b\n"; if ($openOnWarn) { $fileToOpen = $_[0]; $betterDie = 1; $lineToGo = $.; } } }
  }
  $myAry[$curIdx] .= $line;
  if ($line !~ /[a-z=]/i) { $curIdx++; next; }
}

close(A);

$bigErrs += $betterDie;

if (!$hasSomething) { printExt("$_[0] has no text.\n"); }

my $count = 0;
my $curLines = 0;

if ($limericks)
{
  open(A, "$_[0]");
  my $lastLimerick = 0;
  my $lastEq = 0;
  while ($a = <A>)
  {
    $count++;
    if ($a =~ /====/)
	{
	  $lastLimerick = $count;
	  $lastEq = $count;
	  while (($a = <A>)=~ /[a-z=]/i)
	  {
	  $count++;
	  if ($a =~ /=/) { limPan($curLines, $lastEq, $count, $_[0]);  $curLines = 0; $lastEq = $count; }
	  if ($a !~ /^=/) { $curLines++; }
	  }
	  if ($curLines != 5) { limPan($curLines, $lastEq, $count, $_[0]); }
	  $curLines = 0;
	}
  }
  close(A);
}


if (($myAry[0] !~ /[a-z]/) && ($showWarn))
{ $warns++; $warning .= "  WARNING: No main ideas in $_[0].\n"; $betterDie = 1; }

for (1..$#myAry)
{
  if ($myAry[$_] !~ /\n[\(\)a-z0-9\t]/i)
  {
    if ($showWarn && defined($myHdr[$_]))
	{
	  $warns++; $warning .= "  WARNING: $myHdr[$_] ($shortName) has no content.\n";
	  if (($openFile) && (!$fileToOpen)) { $fileToOpen = $_[0]; printExt("Tagging $_[0].\n"); }
	}
  }
}

if ((!$gotNames) && (-s $_[0] > 0)) { printExt("No names, but no big deal in $shortName.\n"); } else
{
  my @namelist0 = split(/\t/, $myAry[$curIdx]);
  my @namelist = sort(@namelist0);
  if (!$namelist[1]) { printExt("$_[0] Claimed name list with no names.\n"); if (($openFile) && (!$fileToOpen)) { $betterDie++; $fileToOpen = $_[0]; printExt("Tagging $_[0].\n"); } }
  else
  {
  for (0..$#namelist)
  {
    if ($namelist[$_] eq $namelist[$_-1])
	{
	  for my $i (0..$#namelist) { if (($namelist[$_] eq $namelist0[$i])) {
	  printExt("Duplicate $namelist[$_] # $i in names for $shortName, " . ($_ + 1) . " of " . ($#namelist+1) . " in alphabetized.\n"); last;
	  }
	  }
	}
  }
  }
}

my @r = sort(@myAry); for (@r) { $_ =~ s/\n.*//g; }

my %found;

for (0..$#r)
{
  #if (@r[$_] eq @r[$_+1]) { print "@r[$_] listed twice in $_[0]...\n"; $betterDie++; }
  if (!defined($mapTo{$r[$_]})) { next; }
  if ($found{$mapTo{$r[$_]}} ) { printExt("    $r[$_] -> $mapTo{$r[$_]} overlaps in $_[0].\n"); $betterDie++; }
 }

 ##for $x (keys %sortOrd) { print "$x $sortOrd{$x}\n"; } die;
my @q = sort {
  my $a2; my $b2;
  if ($a !~ /^\\/) { return -1; }
  if ($b !~ /^\\/) { return 1; }
  if (sortOrd($a) < sortOrd($b)) { return -1; }
  if (sortOrd($a) > sortOrd($b)) { return 1; }
  if ($a =~ /^\\nam/) { return 1; }
  if ($b =~ /^\\nam/) { return -1; }
  return $a cmp $b;
} (@myAry);

if ($betterDie)
{
  if ($warning) { print $warning; }
  print ("Fix stuff in $_[0] before sorting.\n");
  push (@badFiles, $shortName);
  if ($openFile)
  {
	my $fileOpenCmd = "start \"\" \"c:\\program files (x86)\\notepad++\\notepad++\" $fileToOpen -n$lineToGo"; `$fileOpenCmd`; testResults(); exit;
  }
  if ($clipboard)
  {
    $filesToTry .= "$_[0]\n";
  }
  if ($openFile && !$fileToOpen)
  { $fileToOpen = $_[0]; print "Tagging $fileToOpen.\n"; }
  return;
}
else
{
  push(@goodFiles, $shortName);
}

if ($justCheck)
{
  if ($debug)
  { print ("Returning after checking $_[0]--this is a debug try with -d.\n"); }
  else
  {
    if ($showOK) { printExt("$_[0] checked okay.\n"); }
	if ($warning) { print "$warning"; } }
	return;
  }
else { if ($showProc) { printExt ("Processing $_[0]."); } }

#print @q;

open(B, ">$_[0].bak");

for (@q) { print B "$_"; }

close(B);

 if (-s "$_[0].bak" != -s "$_[0]") { die "Uh oh, size of $_[0] and $_[0].bak aren't equal. Not copying over."; }
move("$_[0].bak", "$_[0]");

}

sub findHeader
{
  open(THISDAY, $_[0]) || die ("No file $_[0].\n");

  my $thisFileYet = 0;
  my $processHeader = 0;
  my $headString = $_[0];

  my $limChar = 0;
  my $isLim = 0;
  my $limLines = 0;

  while ($a = <THISDAY>)
  {
    if ($a =~ /^\\$headString/)
	{
	  $processHeader = 1;
	  print "Header $headString in $_[0]:\n";
	  if ($a =~ /\\lim/) { $isLim = 1; } else { $isLim = 0; }
	  next;
	}
	if ($processHeader)
	{
	  print $a;
	  if ($isLim)
	  {
	    $limLines++;
		if ($a =~ /^=/) { $limLines = 0; }
	    if (($a =~ /^=/) && ($limChar > 0))
		{
		  procLimChar($limChar, $limLines);
		}
	  }
	}
	if ($a !~ /[a-z=]/) { $processHeader = 0; if ($isLim) { procLimChar($limChar, $limLines); } }
  }
}

sub procLimChar
{
  if ($_[1] != 5) { printExt("Bad # of lines in limerick.\n"); }
  elsif (($_[0] < 120) || ($_[0] > 200)) { printExt("$_[0] characters in limerick. Probably bad.\n"); }
  else { printExt("Nothing bad.\n"); }
}

sub sortOrd
{
  my $stub = $_[0];
  $stub =~ s/\n.*//g;
  #print "$stub $sortOrd{$stub}\n";
  if (!defined($sortOrd{$stub})) { return -10000; }
  return $sortOrd{$stub};
}

sub isUnix
{
  my $buffer;
  open(XYZ, $_[0]);
  binmode(XYZ);
  read(XYZ, $buffer, 1000, 0);
  close(XYZ);
  my $retval = 0;

  foreach (split(//, $buffer)) {
    if ($_ eq chr(13)) { return 0;}
    if ($_ eq chr(10)) { return 1;}
	}
  return $retval;
}

sub processLim
{
  open(A, "$_[0]");
  while ($a = <A>)
  {
    if ($a =~ /====/)
	{
	  $numLim++;
	  print "================ $_[0]\n";
	  while ($b = <A>)
	  {
	  if ($b =~ /[a-z=]/i) { print $b; if ($b =~ /====/) { $numLim++; } } else { last; }
	  }
	}
  }
  close(A);
}

sub limPan
{
  my $badLimerick;
  if ($_[0] != 5)
  {
  $badLimerick = "$_[3]: Bad limerick $_[0]-$_[1], $_[2]";
  print "******$. $badLimerick\n";
  $testErrList .= "$badLimerick<br />\n";
  $betterDie++;
  }
#else { print "Ok limerick $_[0] to $_[1]\n"; }
}

sub setGlobals
{
$filesToTry = "";

$inDir = "c:/writing/daily";
$checkHeaders = 0;
$count = 0;
$theMax = $defFar = 7;
$justCheck = 1;
$debug = 0;
$showWarn = 1;
$showOK = 1;
$showProc = 1;
$verifyHeadings = 1;
$onlyLim = 0;

}

sub printErrExt
{
  $testErrList .= "$_[0]<br />\n";
  printExt($_[0]);
 }

sub printExt
{
  if ($printToErrorFile) { print EL $_[0]; }
  print $_[0];
}

sub testResults
{
if ($testing)
{
  print "TEST RESULTS: daily file big errors,$bigErrs,0,0,$testErrList\n";
  $bigWarn =~ s/\n/<br \/>\n/g;
  print "TEST RESULTS: daily file warning,$warns,10,0,$bigWarn";
}
}

sub usage
{
print<<EOT;
-a all back not just 1
-b dropbox folder
-c just check (default) vs -f
-d debug text
-f full check and sort
-l check limericks
-n don't open file
-np/-sp hide/show what's processing (default = show)
-o open file
-q keep quiet about successes/warnings (default = show)
-v verify headings (default) vs -nh don't verify
-w show only warnings
-# # of days back
SAMPLE USES:
    a.pl -h lim -b 200 shows limericks in dropbox
    a.pl -c -a -200 -nh -b -w -np -o shows just the errors (Dropbox) and opens on the way (-eo)
    a.pl -c -a -200 -nh -w -np -o shows just the errors (Local) and opens on the way (-eh)
EOT

exit;
}