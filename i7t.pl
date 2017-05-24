#############################################
#i7t.pl
#reads in i7 source and sees all the tables
#and potentially matches them up with release notes
#determined by a log file i7t.txt
#i7t.pl -s pc
#or run it in a directory with story.ni
#

use POSIX (getcwd);
use Win32;

use strict;
use warnings;

my $newDir = ".";
my $project = "Project";

#######################################varaiables
my $popupString = "";
my $sum = "";
my $tables = 0;
my $count = 0;
my $curTable = "";
my @important = ();
my $majorTable = 0;
my $tableList = "";

my $tabfile = "c:/writing/scripts/i7t.txt";
my $tabfilepriv = "c:/writing/scripts/i7tp.txt";

my %xtraFiles;

###################duplicate detector hashes
my %tableDup;
my %extraRows;
my %ignoreDup;

my @tableReadFiles = ($tabfile, $tabfilepriv);

my @filesToRead = ();

################################
# options
my $tableTab = 0; # this lists how many tables have how many tabs
my $printSuccesses = 0;
my $quietTables = 1;
my $openTableFile = 0;
my $openPost = 0;
my $maxString = 0;
my $spawnPopup = 0;

my %rows;
my %falseRows;
my %trueRows;
my %smartIdeas;
my %exp;
my %failCmd;

my %filesToOpen;
my %doubleErr;

my @tableCount = ();

$exp{"3d"} = "threediopolis";
$exp{"4d"} = "fourdiopolis";
$exp{"pc"} = "compound";
$exp{"sc"} = "slicker-city";
$exp{"btp"} = "buck-the-past";
$exp{"bs"} = "btp-st";

my $countMismatch = 0;
my $writeDir = "c:\\writing\\dict";

if (getcwd() =~ /\.inform/) { $project = getcwd(); $project =~ s/\.inform.*//g; $project =~ s/.*[\\\/]//g; $project = lc($project); }

my $fileName;

while ($count <= $#ARGV)
{
  $a = $ARGV[$count];
  $b = $ARGV[$count+1];
  for ($a)
  {
    /^-tt$/ && do { $tableTab = 1; $count++; next; };
    /^-t$/ && do { $b = $ARGV[$count+1]; my $important = split(/,/, $b); $count+= 2; next; };
    /^-?c$/ && do { print "Opening source. -e opens the data file, -ec/ce both, -pr private.\n"; system("start \"\" \"C:\\Program Files (x86)\\Notepad++\\notepad++.exe\" c:\\writing\\scripts\\i7t.pl"); exit; };
    /^-?e$/ && do { print "Opening data file. -c opens the source, -ec/ce both, -pr private.\n"; `$tabfile`; exit; };
	/^-?(ec|ce)$/ && do
    {
      print "Opening data and source.\n";
      `c:\\writing\\scripts\\i7t.txt`;
      `c:\\writing\\scripts\\i7t.pl`;
      next;
    };
    /^-?pr$/ && do { print "Opening private file. -e opens the source, -ef both. -p private.\n"; `$tabfilepriv`; exit; };
	/^-i$/ && do { @important = split(/,/, $b); $count += 2; next; };
	/^-sp$/ && do { $spawnPopup = 1; $count++; next; };
	/^-ps$/ && do { $printSuccesses = 1; $count++; next; };
	/^-q$/ && do { $quietTables = 1; $count++; next; };
	/^-tl$/ && do { $quietTables = 0; $count++; next; };
	/^-o$/ && do { $openPost = 1; $count++; next; };
	/^-ot$/ && do { $openTableFile = 1; $count++; next; };
	/^rar$/ && do { $maxString = 1; $tableTab = 1; $fileName = ""; $count++; next; };
	/^-?\.$/ && do { $writeDir = "."; $count++; next; };
    /-[ps]$/ && do
	{
	  $project = $b;
	  $newDir = "c:/games/inform/$project.inform/Source";
	  $count+= 2;
	  if ($exp{$project}) { print "Found brief project, so changing $project to $exp{$project}.\n"; $project = $exp{$project}; }
	  next;
    };
    /[\\\/]/ && do { $newDir = $a; $count++; next; };
	usage();
  }
}

for (@tableReadFiles)
{
  findExtraFiles($_);
}

my $tableFile = "$writeDir\\tables-$project.i7";
open(B, ">$tableFile");
close(B);

my $sourceFile;

if (!defined($xtraFiles{$project})) { die ("No project defined for $project.\n"); }

my @sourceFileList = @{$xtraFiles{$project}};

my $tableShort;
my $table = 0;
my $majorList = "";
my $tableRow = 0;
my $falseRow = 0;
my $trueRow = 0;
my $smartIdea = 0;

for $sourceFile (@sourceFileList)
{

print "Reading $sourceFile...\n";
open(A, "$sourceFile") || die ("$sourceFile in $project doesn't exist.");
open(B, ">>$tableFile");

while ($a = <A>)
{
  if ($a =~ /^(\[)?table /) #we want to be able to make a fake table if we can
  {
    my $aorig = $a;
    @tableCount = ();
    if ($a =~ /^\[/)
	{ $a =~ s/[\[\]]//g;
	#commented out for a non-table in BTP
	#print "--$a";
	}
	$a =~ s/ \(continued\).*?\[/ \[/g;
	#if ($aorig =~ /continued/) { print "#####################$a"; }
    $a =~ s/^\[//g;
    $table = 1; $tables++; $curTable = $a; chomp($curTable);
	$tableShort = $curTable;
	$curTable =~ s/ *\[.*//g;
	$falseRow = $trueRow = $smartIdea = 0;
	$curTable =~ s/ - .*//g;
	if ($tableShort =~ /\[x/) { $tableShort =~ s/.*\[x/x/g; $tableShort =~ s/\]//g; }
	if ($tableShort =~ / \[/) { $tableShort =~ s/ \[.*//g; }
	$tableShort =~ s/ - .*//g;
	for my $x (@important)
	{
	  if ($a =~ /\b$x\b/i) { $majorTable = 1; }
	}
	$tableRow = 0;
    if ($aorig =~ /^\[table/) { }
	else
	{
	  <A>;
	}
	next;
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
	$smartIdeas{$tableShort} += $smartIdea;
	$rows{$tableShort} += $tableRow;
	$falseRows{$tableShort} += $falseRow;
	$trueRows{$tableShort} += $trueRow;
	if ($majorTable) { $majorList .= "$curTable: $tableRow rows<br />"; } $majorTable = 0;
  }
  if ($table)
  {
    print B $a; $count++; $tableRow++; if ($a =~ /^\[/) { print "WARNING: $curTable has a comment which may throw the counter off.\n"; }
	if ($a =~ /(false\t|\tfalse)/) { $falseRow++; }
	if ($a =~ /(true\t|\ttrue)/) { $trueRow++; }
	my $y = $a;
	my $tempAdd = ($y =~ s/\[(activation of|e0|e1|e2|e3|e4|na)//g);
	if (($tempAdd < 1) && $smartIdea)
	{
	  print "Line $. in $sourceFile has no activations.\n";
	}
	$smartIdea += $tempAdd;
	if (($a =~ /[a-z]/i) && ($tableRow > -1))
	{
	  my @tempAry = split(/\t/, $a);
	  if ($#tempAry > $#tableCount) { $maxString = $a; }
	  elsif ($#tempAry == $#tableCount) { $maxString .= $a; }
	  $tableCount[$#tempAry]++;
	}
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
}

my $ranOneTest = 0;
my $printFail = 0;
my $errLog = "";
my $thisFile = "";
my $lastOpen = "";

for my $trf (@tableReadFiles)
{
open(A, $trf) || do { print "No $trf.\n"; next; };

my @b;

while ($a = <A>)
{
  if ($a =~ /^#/) { next; }
  if ($a =~ /^;/) { last; }
  chomp($a);
  @b = split(/\t/, $a);

  if (lc($b[0]) ne lc($project)) { next; }

  if ($b[1] =~ /^xrow:/)
  {
    my @q = split(/:/, $b[1]);
	$extraRows{$q[2]} = $q[1];
	next;
  }

  if ($b[1] =~ /^igdup:/)
  {
    $b[1] =~ s/^igdup://;
	$ignoreDup{$b[1]} = 1;
	next;
  }

  if ($#b == 1) { $failCmd{$project} = $b[1]; next; }

  #print "parsing @b\n";
  $ranOneTest = 1;

  if (($b[2] ne "\"") && ($b[2] ne "\"\""))
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

  #most of the time, the 5th element (oh hi, Bruce Willis!) will be a 1 to signify that there is a message once the table comes to an end. But I can adjust this if I want.
  #This used to be $+ instead of $$ but then I had other things I wanted to track for partial tables.

  my $adjust = 0;
  if (defined($b[4])) { $adjust = $b[4]; } else { print "WARNING: line $. should have a 5th column for fudging extra row counts\n"; }
  if (defined($b[5])) { print "WARNING line $. has too many lines.\n"; }

  my $almost = $b[3]; $almost =~ s/\$[\+\$]/\[0-9\]\*/g;

  $b[3] =~ s/\$\$/$size+$adjust/ge;
  $b[3] =~ s/\$c/$smartIdeas{$b[1]}+$adjust/ge;
  $b[3] =~ s/\$f/$falseRows{$b[1]}+$adjust/ge;
  $b[3] =~ s/\$t/$trueRows{$b[1]}+$adjust/ge;

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
    if ($printSuccesses) { print "$thisFile search for $b[3] PASSED:\n  $f"; }
  }
  else
  {
    $countMismatch++;
	if ($b[3] =~ /[^\w\+]0\W/)
	{
	  print "Did not find table *$b[1]* for the check *$b[3]\*.\n";
    } #todo: find a way to do this less hackily, x+0 now throws an error
	else
	{
	print "$thisFile search for $b[3] FAILED\n";
	$popupString .= "* $b[3]\n";
	}
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

}

###########################
#this can/should be done better
#
#we can/should move this in with the main while for A with the while-loop to do table counts
#
my $dupFail = 0;
my $dupLog = "";

close(A);
close(B);
close(F);

for $sourceFile (@sourceFileList)
{
  open(A, "$sourceFile") || die ("$sourceFile in $project doesn't exist.");
  while ($a = <A>)
  {
    if ($a =~ /^table +of/i)
	{
	  chomp($a);
	  $curTable = lc($a);
	  $curTable =~ s/ [\(\[].*//;
	  <A>;
	  next;
	}
	if ($a !~ /[a-z]/i)
	{
	  $curTable = "";
	  next;
	}
	if ($curTable && (!$ignoreDup{$curTable}))
	{
	  my @tempAry = split(/\t/, $a);
	  my $unique = $tempAry[0];
	  if ($extraRows{$curTable})
	  {
		if ($#tempAry < $extraRows{$curTable} - 1)
		{
		  print "Warning: may be ignoring too many rows in $curTable, line $.: @tempAry\n";
		  $extraRows{$curTable} = $#tempAry + 1;
		}
	    $unique = join("/", @tempAry[0..$extraRows{$curTable}-1]);
	  }
	  if ($tableDup{$curTable}{$unique})
	  {
	    print "Duplicate at line $.: $curTable/$unique also at $tableDup{$curTable}{$unique}\n";
		$dupLog .= "$unique/$tableDup{$curTable}{$unique}<br />";
		$dupFail++;
      }
	  $tableDup{$curTable}{$unique} = $.;
    }
  }
  close(A);
}

if ($dupFail)
{
  print "TEST RESULTS:(notes) $project-tabledup,0,$dupFail,0,$dupLog\n";
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

if ($ranOneTest && !$printFail && !$dupFail) { print "EVERYTHING WORKED! YAY!\n"; }

if ($openPost)
{
  my $myfi;
  for $myfi (sort keys %filesToOpen)
  {
    print "Opening $myfi, line $filesToOpen{$myfi}\n";
	my $openCmd = "start \"\" \"C:\\Program Files (x86)\\Notepad++\\notepad++.exe\" $myfi";
	if ($filesToOpen{$myfi}) { $openCmd .= " -n$filesToOpen{$myfi}"; }
    `$openCmd`;
	if ($spawnPopup && $popupString)
	{
	  my $myShort = $myfi; $myShort =~ s/.*[\/\\]//;
	  Win32::MsgBox("Miscounts in $myShort\n" . ('=' x 20) . "\n$popupString", 0, "I7T.PL results");
	}
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
elsif ($spawnPopup)
{
  print "'\nNOTE: The program forces you to type -o with spawnPopup (-sp), because otherwise you just see a popup and then have to type in the file to edit anyway.\n";
}

if ($openTableFile)
{
  my $openCmd = "start \"\" \"C:\\Program Files (x86)\\Notepad++\\notepad++.exe\" $tableFile";
  `$openCmd`;
}

sub findExtraFiles
{
  open(A, "$_[0]") || die ("No file $_[0]");
  while ($a = <A>)
  {
    if ($a =~ /^xtra/)
	{
	  chomp($a);
	  my @filemap = split(/\t/, $a);
	  if ($#filemap != 2) { warn "Need 3 fields in $.: $a\n"; next; }
	  if (!defined($xtraFiles{$filemap[1]})) { $xtraFiles{$filemap[1]} = []; }
	  push(@{$xtraFiles{$filemap[1]}}, $filemap[2]);
	}
    if ($a =~ /^story/)
	{
	  chomp($a);
	  my @filemap = split(/\t/, $a);
	  if ($#filemap != 1) { warn "Need 2 fields in $.: $a\n"; next; }
	  if (!defined($xtraFiles{$filemap[1]})) { $xtraFiles{$filemap[1]} = []; }
	  push(@{$xtraFiles{$filemap[1]}}, "c:/games/inform/$filemap[1].inform/Source/story.ni");
	}
  }
  close(A);
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
-[ps] specifies the project, written out or in shorthand
-sp spawns a popup Windows message box to tell what to replace, if valid
(directory) looks for story.ni in a different directory
(ra|nu)(r|s) does random text or nudges for roiling or shuffling
EOT
exit;
}