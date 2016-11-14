#############################################
#i7t.pl
#reads in i7 source and sees all the tables
#and potentially matches them up with a log file
#i7t.pl -s pc
#or run it in a directory with story.ni
#

use POSIX;

my $newDir = ".";
my $project = "Project";
$tables = 0;
$count = 0;

$exp{"3d"} = "threediopolis";
$exp{"4d"} = "fourdiopolis";
$exp{"pc"} = "Compound";
$exp{"sc"} = "Slicker-City";
$exp{"btp"} = "buck-the-past";

my $countMismatch = 0;
my $writeDir = "c:\\writing\\dict";

if (getcwd() =~ /\.inform/) { $project = getcwd(); $project =~ s/\.inform.*//g; $project =~ s/.*[\\\/]//g; }

while ($count <= $#ARGV)
{
  $a = @ARGV[$count];
  $b = @ARGV[$count+1];
  for ($a)
  {
    /^-tt$/ && do { $tableTab = 1; $count++; next; };
    /^-t$/ && do { $b = @ARGV[$count+1]; @important = split(/,/, $b); $count+= 2; next; };
    /^-?e$/ && do { print "Opening source. -f opens the data file.\n"; system("start \"\" \"C:\\Program Files (x86)\\Notepad++\\notepad++.exe\" c:\\writing\\scripts\\i7t.pl"); exit; };
    /^-?f$/ && do { print "Opening data file. -e opens the source.\n"; `c:\\writing\\scripts\\i7t.txt`; exit; };
	/^-q$/ && do { $quietTables = 1; $count++; next; };
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
$tableFile = "$writeDir\\tables-$project.i7";
open(B, ">$tableFile");

while ($a = <A>)
{
  if ($a =~ /^(\[table|table) /) #we want to be able to make a fake table if we can
  {
    @tableCount = ();
    if ($a =~ /^\[/) { $a =~ s/[\[\]]//g; print "--$a"; }
	$a =~ s/ \(continued\)//g;
    $a =~ s/^\[//g;
    $table = 1; $tables++; $curTable = $a; chomp($curTable); $tableShort = $curTable;
	$curTable =~ s/ *\[.*//g; $tableCount = -3;
	$curTable =~ s/ - .*//g;
	if ($tableShort =~ /\[x/) { $tableShort =~ s/.*\[x/x/g; $tableShort =~ s/\]//g; }
	if ($tableShort =~ / \[/) { $tableShort =~ s/ \[.*//g; }
	$tableShort =~ s/ - .*//g;
	for $x (@important)
	{
	  if ($a =~ /\b$x\b/i) { $majorTable = 1; }
	}
  }
  if ($table)
  {
    print B $a; $count++; $tableCount++; if ($a =~ /^\[/) { print "WARNING: $curTable has a comment which may throw the counter off.\n"; }
	if ($a =~ /[a-z]/i)
	{
	  my @tempAry = split(/\t/, $a);
	  if ($#tempAry > $#tableCount) { $maxString = $a; }
	  elsif ($#tempAry == $#tableCount) { $maxString .= $a; }
	  @tableCount[$#tempAry]++;
	}
  }
  if ($a !~ /[a-z]/)
  {
    if (!$table) { next; }
	$table = 0;
    if ($tableTab)
	{
	  print "$tableShort: ";
	  for (0..$#tableCount) { if (@tableCount[$_]) { print "$_ tabs: @tableCount[$_] "; } }
	  print "\n";
	  if (($maxString) && (@tableCount[$#tableCount] < @tableCount[$#tableCount - 1])) { print "Max string: $maxString"; }
	}
    if (!$quietTables)
	{
	  $tableList .= "$curTable";
	  if ($curTable ne $tableShort) { $tableList .= "($tableShort)"; }
	  $tableList .= ": $tableCount rows\n";
	}
	if ($rows{$tableShort}) { print "Tacking on $tableCount to $tableShort, up from $rows{$tableShort}.\n"; }
	$rows{$tableShort} += $tableCount;
	if ($majorTable) { $majorList .= "$curTable: $tableCount rows<br />"; } $majorTable = 0;
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

while ($a = <A>)
{
  if ($a =~ /^#/) { next; }
  if ($a =~ /^;/) { last; }
  chomp($a);
  @b = split(/\t/, $a);
  
  if (lc(@b[0]) ne lc($project)) { next; }
  
  if ($#b == 1) { $failCmd{$project} = @b[1]; next; }

  $ranOneTest = 1;

  if (@b[2] ne "\"")
  {
  open(F, @b[2]) || die ("Can't find release notes file @b[2].");
  $thisFile = $lastOpen = @b[2];
  }
  else
  {
  open(F, $lastOpen) || die ("Can't re-open $lastOpen.");
  }
  
  my $size = 0;
  
  if ($rows{@b[1]}) { $size = $rows{@b[1]}; } else { print "@b[1] has nothing.\n"; }
  
  $sizeX = $size+1;
  
  my $almost = @b[3]; $almost =~ s/\$[\+\$]//g;

  @b[3] =~ s/\$\$/$size/g;
  @b[3] =~ s/\$\+/$sizeX/g;
  print "Trying @b[3]\n";
  my $success = 0;
  my $nearSuccess = "";
  while ($f = <F>)
  {
    #print "@b[3] =~? $f";
    if ($f =~ /\b@b[3]/) { $success = 1; last; }
	if ($f =~ /$almost/) { $nearSuccess .= $f; }
  }
  close(F);
  if ($success)
  {
    print "$thisFile search for @b[3] PASSED:\n  $f\n";
  }
  else
  {
    $countMismatch++;
	print "$thisFile search for @b[3] FAILED\n";
	if (!$fileToOpen) { $fileToOpen = $thisFile; }
	$errLog .= "@b[3] needs to be in<br />\n";
	if ($nearSuccess)
	{
	  my $add = "Likely suspect(s): $nearSuccess";
	  print $add;
	  chomp($add);
	  $errLog .= "$add<br />\n";
    }
	$printFail = 1;
  }
}

if ($printFail)
{
  print "TEST RESULTS:(notes) $project-tables,0,1,0,Look <a href=\"file:///$thisFile\">here</a>\n$errLog";
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
  if ($fileToOpen)
  {
    print "Opening $fileToOpen\n";
    `$fileToOpen`;
  }
  else { print "No error files to open!\n"; }
}

if ($openTableFile) { system("start \"\" \"C:\\Program Files (x86)\\Notepad++\\notepad++.exe\" $tableFile"); }

sub usage
{
print<<EOT;
directory
csv = tables to highlight
-t specifies a CSV of important tables to track
-c specifies the writedir for tables.i7 as the current directory (default is writing\dict)
-e opens the i7t.pl file
-f opens the i7t.txt file
-o opens the offending file post-test
-ot opens the table file
-p specifies the project
-s specifies the project in shorthand
(directory) looks for story.ni in a different directory
(ra|nu)(r|s) does random text or nudges for roiling or shuffling
EOT
exit;
}