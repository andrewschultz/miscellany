#############################################
#i7t.pl
#reads in i7 source and sees all the tables
#and potentially matches them up with release notes
#determined by a log file i7t.txt
#i7t.pl -s pc
#or run it in a directory with story.ni
#

use POSIX;

use strict;
use warnings;

my $newDir = ".";
my $project = "Project";

my $sum = "";
my $tables = 0;
my $count = 0;
my $curTable = "";
my @important = ();
my $majorTable = 0;
my $tableList = "";

################################
# options
my $tableTab = 0; # this lists how many tables have how many tabs
my $printSuccesses = 0;
my $quietTables = 1;
my $openTableFile = 0;
my $openPost = 0;
my $maxString = 0;

my %rows;
my %exp;
my %failCmd;

my %filesToOpen;
my %doubleErr;

my @tableCount = ();

$exp{"3d"} = "threediopolis";
$exp{"4d"} = "fourdiopolis";
$exp{"pc"} = "Compound";
$exp{"sc"} = "Slicker-City";
$exp{"btp"} = "buck-the-past";

my $countMismatch = 0;
my $writeDir = "c:\\writing\\dict";

if (getcwd() =~ /\.inform/) { $project = getcwd(); $project =~ s/\.inform.*//g; $project =~ s/.*[\\\/]//g; }

my $fileName;

while ($count <= $#ARGV)
{
  $a = $ARGV[$count];
  $b = $ARGV[$count+1];
  for ($a)
  {
    /^-tt$/ && do { $tableTab = 1; $count++; next; };
    /^-t$/ && do { $b = $ARGV[$count+1]; my $important = split(/,/, $b); $count+= 2; next; };
    /^-?e$/ && do { print "Opening source. -f opens the data file, -ef both.\n"; system("start \"\" \"C:\\Program Files (x86)\\Notepad++\\notepad++.exe\" c:\\writing\\scripts\\i7t.pl"); exit; };
    /^-?f$/ && do { print "Opening data file. -e opens the source, -ef both.\n"; `c:\\writing\\scripts\\i7t.txt`; exit; };
	/^-?(ef|fe)$/ && do
    {
      print "Opening data and source.\n";
      `c:\\writing\\scripts\\i7t.txt`;
      `c:\\writing\\scripts\\i7t.pl`;
      next;
    };
	/^-i$/ && do { @important = split(/,/, $b); $count += 2; next; };
	/^-ps$/ && do { $printSuccesses = 1; $count++; next; };
	/^-q$/ && do { $quietTables = 1; $count++; next; };
	/^-tl$/ && do { $quietTables = 0; $count++; next; };
	/^-o$/ && do { $openPost = 1; $count++; next; };
	/^-ot$/ && do { $openTableFile = 1; $count++; next; };
	/^rar$/ && do { $maxString = 1; $tableTab = 1; $fileName = "c:/Program Files (x86)/Inform 7/Inform7/Extensions/Andrew Schultz/Roiling Random Text.i7x"; $count++; next; };
	/^ras$/ && do { $maxString = 1; $tableTab = 1; $fileName = "c:/Program Files (x86)/Inform 7/Inform7/Extensions/Andrew Schultz/Shuffling Random Text.i7x"; $count++; next; };
	/^nur$/ && do { $maxString = 1; $tableTab = 1; $fileName = "c:/Program Files (x86)/Inform 7/Inform7/Extensions/Andrew Schultz/Roiling Nudges.i7x"; $count++; next; };
	/^nus$/ && do { $maxString = 1; $tableTab = 1; $fileName = "c:/Program Files (x86)/Inform 7/Inform7/Extensions/Andrew Schultz/Shuffling Nudges.i7x"; $count++; next; };
	/^-c$/ && do { $writeDir = "."; $count++; next; };
    /-p/ && do { $project = $b; $newDir = "c:/games/inform/$project.inform/Source"; $count+= 2; print "Note -p forces you to write out the project, so -s may be more appropriate.\n"; next; };
	/-s/ && do { if ($exp{$b}) { $project = $exp{$b}; } else { $project = $b; } $newDir = "c:/games/inform/$project.inform/Source"; $count+= 2; next; };
    /[\\\/]/ && do { $newDir = $a; $count++; next; };
	usage();
  }
}

if (!$fileName) { $fileName = "$newDir/story.ni"; }

open(A, "$fileName") || die ("$fileName doesn't exist.");
my $tableFile = "$writeDir\\tables-$project.i7";
open(B, ">$tableFile");

my $tableShort;
my $table = 0;
my $majorList = "";
my $tableRow = 0;

while ($a = <A>)
{
  if ($a =~ /^(\[table|table) /) #we want to be able to make a fake table if we can
  {
    my $aorig = $a;
    @tableCount = ();
    if ($a =~ /^\[/) { $a =~ s/[\[\]]//g;
	#commented out for a non-table in BTP
	#print "--$a";
	}
	$a =~ s/ \(continued\)//g;
    $a =~ s/^\[//g;
    $table = 1; $tables++; $curTable = $a; chomp($curTable);
	$tableShort = $curTable;
	$curTable =~ s/ *\[.*//g; $tableRow = -3;
	if ($aorig =~ /^\[table/) { $tableRow++; }
	$curTable =~ s/ - .*//g;
	if ($tableShort =~ /\[x/) { $tableShort =~ s/.*\[x/x/g; $tableShort =~ s/\]//g; }
	if ($tableShort =~ / \[/) { $tableShort =~ s/ \[.*//g; }
	$tableShort =~ s/ - .*//g;
	for my $x (@important)
	{
	  if ($a =~ /\b$x\b/i) { $majorTable = 1; }
	}
  }
  if ($table)
  {
    print B $a; $count++; $tableRow++; if ($a =~ /^\[/) { print "WARNING: $curTable has a comment which may throw the counter off.\n"; }
	if (($a =~ /[a-z]/i) && ($tableRow > -1))
	{
	  my @tempAry = split(/\t/, $a);
	  if ($#tempAry > $#tableCount) { $maxString = $a; }
	  elsif ($#tempAry == $#tableCount) { $maxString .= $a; }
	  $tableCount[$#tempAry]++;
	}
  }
  if ($a !~ /[a-z]/)
  {
    if (!$table) { next; }
	$table = 0;
    if ($tableTab)
	{
	  print "$tableShort: ";
	  for (0..$#tableCount) { if ($tableCount[$_]) { print "$_ tabs: $tableCount[$_] "; } }
	  print "\n";
	  if (($maxString) && ($#tableCount >= 1) && defined($tableCount[$#tableCount - 1]) && ($tableCount[$#tableCount] < $tableCount[$#tableCount - 1]))
	  {
	    print "Max string: $maxString";
	  }
	}
    if (!$quietTables)
	{
	  $tableList .= "$curTable";
	  if ($curTable ne $tableShort) { $tableList .= "($tableShort)"; }
	  $tableList .= ": $tableRow rows\n";
	}
	#if ($rows{$tableShort}) { print "Tacking on $tableRow to $tableShort, up from $rows{$tableShort}.\n"; }
	$rows{$tableShort} += $tableRow;
	if ($majorTable) { $majorList .= "$curTable: $tableRow rows<br />"; } $majorTable = 0;
  }
}

if (!$quietTables)
{
$sum = "$tables tables, $count lines.\n$tableList";
print $sum;
}

print B $sum;
close(A);
close(B);

open(A, "c:/writing/scripts/i7t.txt");

my @b;
my $ranOneTest = 0;
my $printFail = 0;
my $errLog = "";
my $thisFile = "";
my $lastOpen = "";

while ($a = <A>)
{
  if ($a =~ /^#/) { next; }
  if ($a =~ /^;/) { last; }
  chomp($a);
  @b = split(/\t/, $a);

  if (lc($b[0]) ne lc($project)) { next; }

  if ($#b == 1) { $failCmd{$project} = $b[1]; next; }

  $ranOneTest = 1;

  if ($b[2] ne "\"")
  {
  open(F, $b[2]) || die ("Can't find release notes file $b[2].");
  $thisFile = $lastOpen = $b[2];
  }
  else
  {
  open(F, $lastOpen) || die ("Can't re-open $lastOpen.");
  }

  my $size = 0;

  if ($rows{$b[1]}) { $size = $rows{$b[1]}; } else { print "$b[1] has nothing.\n"; }

  my $sizeX = $size+1;

  my $almost = $b[3]; $almost =~ s/\$[\+\$]/\[0-9\]\*/g;

  $b[3] =~ s/\$\$/$size/g;
  $b[3] =~ s/\$\+/$sizeX/g;
  #print "Looking for this text: $b[3]\n";
  my $success = 0;
  my $nearSuccess = "";
  my $f;

  while ($f = <F>)
  {
    #print "$b[3] =~? $f";
    if ($f =~ /\b$b[3]/) { $success = 1; last; }
	if ($f =~ /$almost/) { if ($filesToOpen{$lastOpen}) { $doubleErr{$lastOpen}++; } else { $filesToOpen{$lastOpen} = $.; } }
  }
  close(F);
  if ($success)
  {
    if ($printSuccesses) { print "$thisFile search for $b[3] PASSED:\n  $f\n"; }
  }
  else
  {
    $countMismatch++;
	print "$thisFile search for $b[3] FAILED\n";
	if (!$filesToOpen{$thisFile}) { $filesToOpen{$thisFile} = $.; }
	$errLog .= "$b[3] needs to be in<br />\n";
	if ($nearSuccess)
	{
	  my $add = "Likely suspect(s): $nearSuccess";
	  print $add;
	  chomp($add);
	  $errLog .= "$add<br />\n";
    }
	$printFail++;
  }
}

if ($printFail)
{
  print "TEST RESULTS:(notes) $project-tables,0,$printFail,0,Look <a href=\"file:///$thisFile\">here</a>\n$errLog";
}

if ($majorList)
{
  $majorList =~ s/,//g;
  print "TEST RESULTS:$project table count,0,$countMismatch,0,$majorList\n";
}

if ($printFail && $failCmd{$project}) { print "RUN THIS: $failCmd{$project}\n"; }

if ($ranOneTest && !$printFail) { print "EVERYTHING WORKED! YAY!\n"; }

if ($openPost)
{
  my $myfi;
  for $myfi (sort keys %filesToOpen)
  {
    print "Opening $myfi, line $filesToOpen{$myfi}\n";
	my $openCmd = "start \"\" \"C:\\Program Files (x86)\\Notepad++\\notepad++.exe\" $myfi";
	if ($filesToOpen{$myfi}) { $openCmd .= " -n$filesToOpen{$myfi}"; }
    `$openCmd`;
  }
  if (!scalar keys %filesToOpen) { print "No error files to open!\n"; }
  if (scalar keys %doubleErr)
  {
    print "Files with >1 error:\n";
	for $myfi (sort { $doubleErr{$a} <=> $doubleErr{$b} } keys %doubleErr )
	{
	  $doubleErr{$myfi}++;
	  print "$myfi: $doubleErr{$myfi} total focus-able errors.\n";
	}
  }
}

if ($openTableFile)
{
  my $openCmd = "start \"\" \"C:\\Program Files (x86)\\Notepad++\\notepad++.exe\" $tableFile";
  `$openCmd`;
}

sub usage
{
print<<EOT;
directory
csv = tables to highlight
-t specifies a CSV of important tables to track
-c specifies the writedir for tables.i7 as the current directory (default is writing\\dict)
-e opens the i7t.pl file
-f opens the i7t.txt file
-ef/fe opens both
-i lists important arrays
-o opens the offending file post-test
-ot opens the table file
-q quiets out the printing of tables
-tl lists them (currently the default)
-ps prints out successes as well
-p specifies the project
-s specifies the project in shorthand
(directory) looks for story.ni in a different directory
(ra|nu)(r|s) does random text or nudges for roiling or shuffling
EOT
exit;
}