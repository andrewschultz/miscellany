#gq.pl: stands for "grep quick"
#this shows where certain text I may've already used pops up in Roiling or Shuffling. It pegs them both as Shuffling << Roiling.
#-tb1 = table random, start with that word
#-tb = table random
#-t = table only
#usage
#gq.pl -tb rosco coors (matches both)
#gq.pl -tb rosco (matches one)
#gq.pl -tb1 rosco (matches starting with rosco)
#gq.pl -m 10 yes (matches 1st 10 yes's)
#
#

use POSIX;

use strict;
use warnings;

################constants
my $gqfile = "c:/writing/scripts/gq.txt";

#################vars
my @availRuns = ();
my @thisAry = ();
my $pwd = getcwd();
my @runs = ();
my $count = 0;
my %map;
my %cmds;
my @blanks;
my @errStuff;
my $blurby = "";
my $myHeader = "";
my $foundSomething = 0;
my $thisTable = "";
my $shortName = "";
my $totalFind = 0;
my $lastHeader = "";

#################options
my $printTabbed = 1;
my $printUntabbed = 1;
my $onlyTables = 0;
my $onlyRand = 0;
my $firstStart = 0;
my $runAll = 0;
my $showRules = 0;
my $showHeaders = 0;
my $headersToo = 0;
my $dontWant = 0;
my $maxFind = 0;

if ($pwd =~ /oafs/) { @runs = ("oafs"); }
elsif ($pwd =~ /(threed|fourd)/) { @runs = ("opo"); }
elsif ($pwd =~ /Compound/i) { @runs = ("as"); }
elsif ($pwd =~ /slicker/i) { @runs = ("as"); }
elsif ($pwd =~ /(buck|past)/i) { @runs = ("as"); }

while ($count <= $#ARGV)
{
  $a = $ARGV[$count];

  for ($a)
  {
  /^0$/ && do { processNameConditionals(); exit; };
  /^-?e$/ && do { `$gqfile`; exit; };
  /^\// && do { $thisAry[0] =~ s/^\///g; $onlyTables = 1; $onlyRand = 1; $firstStart = 1; $count++; next; };
  /^-?a$/ && do { $runAll = 1; $count++; next; }; # run all
  /^-o$/ && do { @runs = ("oafs"); $count++; next; }; # oafs?
  /,/ && do { @runs = split(/,/, $a); $count++; next; };
  /^-?n$/ && do { @runs = ("names"); $count++; next; }; # names
  /^-?(3d|3|4d|4)$/i && do { @runs = ("opo"); $count++; next; }; # 3dop try
  /^-?(c|as|sc|pc)$/i && do { @runs = ("as"); $count++; next; }; # Alec Smart?
  /^-?(r|roi|s|sa)$/i && do { @runs = ("sts"); $count++; next; }; # roiling original? (default)
  /^-sr$/ && do { $showRules = 1; $count++; next; }; # show the rules text is in
  /^-h$/ && do { $showHeaders = 1; $count++; next; };
  /^-p$/ && do { $headersToo = 1; $count++; next; };
  /^-nt$/ && do { $printTabbed = 0; $count++; next; };
  /^-x/ && do { $dontWant = 1; $count++; next; };
  /^-nd$/ && do { newDefault($ARGV[$count+1]); $count++; next; };
  /^-ft$/ && do { $printUntabbed = 0; $count++; next; };
  /^-m$/ && do { $maxFind = $thisAry[1]; @thisAry = $thisAry[2..$#thisAry]; $count+= 2; next; };
  /^-t$/ && do { $onlyTables = 1; $count++; next; }; #not perfect, -h + -t = conflict
  /^-tb$/ && do { $onlyTables = 1; $onlyRand = 1; $count++; next; }; #not perfect, -h + -t = conflict
  /^-tb1$/ && do { $onlyTables = 1; $onlyRand = 1; $firstStart = 1; $count++; next; }; #not perfect, -h + -t = conflict
  /,/ && do { @runs = split(/,/, $a); $count++; next; };
  /^[\\0-9a-z]/ && do { if ($map{$a}) { print "$a -> $map{$a}, use upper case to avoid\n"; push(@thisAry, $map{$a}); } else { push(@thisAry, $a); } $count++; next; }; # if we want to use AS as a word, it would be in upper case
  print "Argument $a failed.\n"; usage();
  }

}
if (!$thisAry[0]) { die ("Need a process-able word for an argument."); }

processListFile();

my $myrun;

if ($runAll)
{
  foreach $myrun (@availRuns)
  {
    processFiles($myrun);
  }
}
else
{
  foreach $myrun (@runs)
  {
    processFiles($myrun);
  }
}

for (@runs)
{
  addSaveFile(join(" ", @thisAry), $_);
}

#################################################subroutines

sub addSaveFile
{
  my $saveFile = "c:\\writing\\scripts\\gq-$_[1].txt";
  my @saveData;
  my %saveHash;
  my $q = $_[0]; $q =~ s/ //g;
  push(@saveData, $q);
  $saveHash{$q} = 1;

  open(A, $saveFile) || warn ("No save file $saveFile.");
  while ($a = <A>)
  {
    chomp($a);
	if ($a =~ / /)
	{
	  my @words = split(/ /, lc($a));
	  if ($saveHash{"$words[1]$words[0]"}) { print "$a already in save list.\n"; next; }
	  if ($saveHash{"$words[0]$words[1]"}) { print "$a already in save list.\n"; next; }
	}
	else
	{
	  if ($saveHash{lc($a)}) { print "$a already in save list.\n"; next; }
	}
	$a =~ s/ //g;
	$saveHash{$a} = 1;
	if ($#saveData == 29) { last; }
	push(@saveData, $a);
  }
  close(A);
  open(A, ">$saveFile");
  for (@saveData)
  {
    print A "$_\n";
  }
  close(A);
  print "Wrote to $saveFile.\n";
}

sub processListFile
{
  my $line;
  my $defaultString;
  my $currentLedger;

  open(A, $gqfile) || die ("Can't find $gqfile.");

  while ($line = <A>)
  {
    if ($line =~ /^#/) { next; }
    if ($line =~ /^;/) { last; }
	if ($line =~ /^MAP=/)
	{
	  chomp($line); $line =~ s/^MAP=//;
	  my @b = split(/:/, $line);
	  my @c = split(/,/, @b);
	  for (@c) { $map{$_} = $b[1]; }
	}
	if ($line =~ /^DEFAULT=/)
	{
	  $defaultString = $line; chomp($defaultString); $defaultString =~ s/DEFAULT=//;
	}
    if ($line =~ /^run=/)
	{
      chomp($line);
	  $line =~ s/.*=//g;
	  $currentLedger = $line;
	  push(@availRuns, $line);
	  next;
	}
	if ($line !~ /[a-z]/i) { $currentLedger = ""; next; }
	if ($currentLedger)
	{
	$cmds{$currentLedger} .= $line;
	}

  }
  close(A);
  if ($#runs == -1)
  {
    if ($defaultString) { @runs = ($defaultString); }
    else
    {
      die("No default string specified in $gqfile, and no project specified in the command line. Bailing.\n");
    }
  }
}

sub processFiles
{
  my @x = split(/\n/, $cmds{$_[0]});

  foreach my $cmd (@x)
  {
	my @fileAndMarkers = split(/\t/, $cmd);
	processOneFile(@fileAndMarkers);
  }
  if ($#blanks > -1) { print "EMPTY FILES: " . join(", ", @blanks) . "\n"; }
  if ($errStuff[0]) { print "TEST RESULTS: $_[0],0," . $#errStuff+1 . ",0," . join("<br />", @errStuff) . "\n"; }
}

sub processOneFile
{
  my $inImportant = 1;
  my $alwaysImportant = 1;
  my $inTable = 0;
  my $line = 0;
  my $currentTable = "";
  my $foundOne = 0;
  my $latestRule;
  my $thisImportant = 0;
  my $idx;
  my @importants;

  if ($_[1])
  {
    $inImportant = 0;
	$alwaysImportant = 0;
	@importants = split(/,/, $_[1]);
  }
  my $modFile = $_[0];
  if ($modFile =~ /story.ni/)
  {
    $modFile =~ s/\.inform.*/ MAIN/;
	$modFile =~ s/.*[\\\/]//;
  }
  if ($modFile =~ /(trizbort|i7x)/) { $modFile =~ s/.*[\\\/]//g; }
  open(A, "$_[0]") || die ("No $_[0]");
  while ($a = <A>)
  {
    if (($a =~ /^[a-z]/) && ($a !~ /\t/)) { $latestRule = "$a"; }
    if ($inImportant) { $idx++; }
    if ($a =~ /^\\/)
	{
      if ($_[1])
	  {
        for (@importants) { if ($a =~ /^\\$_[=\|]/) { $idx = 0; $inImportant = 1; $thisImportant = $a; chomp($thisImportant); $thisImportant =~ s/[\|=].*//g; } }
	  }
	  else { $thisImportant = $a; $thisImportant =~ s/^\\//g; $thisImportant =~ s/[=\\].*//g; chomp($thisImportant); }
	}
    $line++;
	if ($a =~ /^table/) { $idx = -1; $currentTable = $a; $currentTable =~ s/ *\[.*//g; $currentTable =~ s/\t//g; chomp($currentTable); $inTable = 1; }
	if ($a !~ /[a-z]/i) { $currentTable = ""; $inTable = 0; if (!$alwaysImportant) { $inImportant = 0; $thisImportant = ""; } }
	my $crom = cromu($a);
    if ($inImportant && $crom)
	{
	  if ($dontWant) { push (@errStuff, "$modFile L$idx"); }
	  if (!$foundOne) { print "Results for $modFile:\n"; }
	  $foundOne++;
	  print "$modFile($line";
	  if ($currentTable) { print ",$currentTable"; }
	  if ($thisImportant) { print ",$thisImportant,L$idx"; }
	  chomp($a);
	  print "): $a";
	  if ($crom == 2) { print " **PLURAL**"; }
	  print "\n";
	  if ($showRules) { print "RULE=$latestRule"; }
	}
  }
  close(A);
  if (!$foundOne) { push (@blanks, $modFile); }
}

sub cromu
{
  if ($firstStart)
  {
    if (($_[0] !~ /^\"$thisAry[0]/i) && ($_[0] !~ /'$thisAry[0]'/i)){ return 0; }
  }

    $a =~ s/\[one of\]/\[\]/g;
    $a =~ s/\[end if\]/\[\]/g;

  if ($_[0] =~ /^(test|volume|chapter|book|part|section)/) { return 0; }
  #lumped together
  if ($#thisAry)
  {
  if ($_[0] =~ /\b$thisAry[0]$thisAry[1]\b/i) { return 1; }
  if ($_[0] =~ /\b$thisAry[1]$thisAry[0]\b/i) { return 1; }
  if ($_[0] =~ /\b$thisAry[0]$thisAry[1]s\b/i) { return 2; }
  if ($_[0] =~ /\b$thisAry[1]$thisAry[0]s\b/i) { return 2; }
  if (($_[0] =~ /\b$thisAry[0]\b/i) && ($_[0] =~ /\b$thisAry[1]s\b/i)) { return 2; }
  if (($_[0] =~ /\b$thisAry[0]s\b/i) && ($_[0] =~ /\b$thisAry[1](s)?\b/i)) { return 2; }
  }
  elsif ($#thisAry == 0)
  {
  if ($_[0] =~ /\b$thisAry[0]s\b/i) { return 2; }
  if ($_[0] =~ /\b$thisAry[0]\b/i) { return 1; }
  }

  #words apart
  for my $tomatch (@thisAry)
  {
    if ($_[0] !~ /\b$tomatch\b/i) { if (($headersToo) && ($myHeader =~ /\b$tomatch\b/i)) { next; } return 0; }
  }
  return 1;
}

sub processStory
{
  my $fileName;
  my $tabrow;

  if ($_[0] =~ /trizbort/i)
  {
    $fileName = $_[0];
  }
  else
  {
  $shortName = $_[0];
  if ($_[1] == 1) { $fileName = "c:/Program Files (x86)/Inform 7/Inform7/Extensions/Andrew Schultz/$_[0] Random Text.i7x"; } else { $fileName = "c:/games/inform/$_[0].inform/Source/story.ni"; }
  }
  open(A, "$fileName") || die ("No $fileName.");
  $foundSomething = 0;
  $count = 0;
  while ($a = <A>)
  {
    chomp($a);
	if (($a =~ /^[a-z].*: *$/i) || ($a =~ /^table/)) { $myHeader = $a;  $tabrow = 0; $blurby = 0;}
	if ($a =~ /^blurb/) { $blurby = 1; }
    $count++;
	$tabrow++;
    if ($a =~ /`/) { print "WARNING: Line $count has back-quote!\n$a"; }
	if ($a =~ /^table of /i) { $a =~ s/ *\[[^\]]*\].*//g; $thisTable = "($a) "; } elsif ($a !~ /[a-z]/i) { $thisTable = ""; }
	my $tmp = cromu($a);
    if ($tmp)
    {
      if ($a =~ /list of text variable/i)
      { processList($a); }
      else
      {
	    if ($showHeaders)
		{
		  if ($myHeader ne $lastHeader)
		    { print "======================$myHeader\n"; $lastHeader = $myHeader; }
		}
		if (isPrintable())
		{ if (!$foundSomething) { print "In $fileName:\n"; }
		print "$shortName L$count ";
		$totalFind++;
		  if ($thisTable)
		  { my $tr2 = $tabrow - 2; print "/$tr2"; }
		  if ($showHeaders) { print ": $a\n"; }
		  else
		  {
		  print ": $thisTable$a";
		  if ($tmp == 2) { print "****PLURAL****"; }
		  print "\n";
		  }
		if ($maxFind == $totalFind) { print "Hit the limit.\n"; }
		  $foundSomething = 1;
		}
	  }
    }
  }

  close(A);
  if (!$foundSomething) { print "Nothing in $fileName.\n"; }

}

sub isPrintable
{
  if (($maxFind) && ($maxFind <= $totalFind)) { return 0; }
  if (!$onlyTables) { return 1; }
  if (($onlyRand) && ($thisTable) && ($blurby) && tabCheck($a)) { return 1; }
  if (tabCheck($a) && ($thisTable) && (!$onlyRand)) { return 1; }
  return 0;
}
sub tabCheck
{
  if (($_[0] =~ /^\t/) && ($printUntabbed)) { return 1; }
  if (($_[0] !~ /^\t/) && ($printTabbed)) { return 1; }
  return 0;
}

sub processList
{
  my $listName = $a; $listName =~ s/.is a list of.*//gi;
  my $yep = 0;
  if ($a =~ /\{/)
  {
    $a =~ s/^[^\"]*.//g; $a =~ s/\" *\}.*//g;
    my @b = split(/\", \"/, $a);
    for (@b)
    {
	  my $temp = cromu($_);
      if ($temp)
      { $yep = 1; $foundSomething = 1; print "$listName (L$count): $_"; if ($temp == 2) { print " (PLURAL)"; } print "\n"; }
    }
    return;
  }
  print "$a\n";
  if (!$yep) { print "$shortName had $ARGV[0]/$ARGV[1] but not in same entry.\n"; }
}

sub newDefault
{
my @array;
open(A, "$gqfile");
my $newDefLine = "DEFAULT=$_[1]";
while ($a = <A>)
{
  if ($a =~ /^DEFAULT/)
  {
    push (@array, $newDefLine);
  }
  else
  {
    push(@array, $a);
  }
}
close(A);
open(A, ">$gqfile");
print A join("\n", @array);

}

sub processNameConditionals
{
open(A, "C:/games/inform/roiling.inform/Source/story.ni") || die ("Can't open Roiling source.");

my $line;
my $l2;
my $l3;
my $processTo;

while ($line = <A>)
{
  if ($line =~ /section gender specific stubs/) { print "List of gender-says:\n"; $processTo = 1; next; }
  if ($processTo)
  {
    if ($line =~ /^section/) { last; }
	if ($line =~ /^to /)
	{
	  $l2 = $line; chomp($l2); $l2 =~ s/to say //g; $l2 =~ s/:.*//g;
	  $l3 = <A>;
	  if ($l3 =~ /\[one of\]/)
	  {
	    $l3 =~ s/.*one of\]//g;
		$l3 =~ s/\[in random.*//g;
		$l3 =~ s/\[or\]/\//g;
	  }
	  else
	  {
	    $l3 =~ s/\[end if.*//g; $l3 =~ s/.*if [^\]]*\]//g; $l3 =~ s/\[else\]/\//g;
	  }
	  print "$l2 = $l3";
	}
  }

}
close(A);

}

sub usage
{
print<<EOT;
0 = process Roiling name conditionals
-h = show headers
-p = headers too
-nt = print tabbed
-ft = print untabbed
-t = only in tables
EOT
exit;
}