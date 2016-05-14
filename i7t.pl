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

$exp{"pc"} = "Compound";
$exp{"sc"} = "Slicker-City";

my $countMismatch = 0;

if (getcwd() =~ /\.inform/) { $project = getcwd(); $project =~ s/\.inform.*//g; $project =~ s/.*[\\\/]//g; }

while ($count <= $#ARGV)
{
  $a = @ARGV[$count];
  $b = @ARGV[$count+1];
  for ($a)
  {
    /-t/ && do { $b = @ARGV[$count+1]; @important = split(/,/, $b); $count+= 2; next; };
    /^-?e$/ && do { `c:\\writing\\scripts\\i7t.txt`; exit; };
	/^-q$/ && do { $quietTables = 1; $count++; next; };
	/^-o$/ && do { $openPost = 1; $count++; next; };
    /-p/ && do { $b = @ARGV[$count+1]; $project = $b; $newDir = "c:/games/inform/$project.inform/Source"; $count+= 2; next; };
	/-s/ && do { if ($exp{$b}) { $project = $exp{$b}; } else { $project = $b; } $newDir = "c:/games/inform/$project.inform/Source"; $count+= 2; next; };
    /[\\\/]/ && do { $newDir = $a; $count++; next; };
	usage();
  }
}

open(A, "$newDir/story.ni") || die ("$newDir/story.ni doesn't exist.");
open(B, ">tables.i7");

while ($a = <A>)
{
  if ($a =~ /^table /)
  {
    $table = 1; $tables++; $curTable = $a; chomp($curTable); $tableShort = $curTable;
	$curTable =~ s/ *\[.*//g; $tableCount = -3;
	$curTable =~ s/ - .*//g;
	if ($tableShort =~ /\[x/) { $tableShort =~ s/.*\[x/x/g; $tableShort =~ s/\]//g; } else { $tableShort = $curTable; }
	for $x (@important)
	{
	  if ($a =~ /\b$x\b/i) { $majorTable = 1; }
	}
  }
  if ($table) { print B $a; $count++; $tableCount++; }
  if ($a !~ /[a-z]/)
  {
    if (($table) && (!$quietTables)) { $tableList .= "$curTable: $tableCount rows\n"; } $table = 0; $rows{$tableShort} = $tableCount;
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
  chomp($a);
  @b = split(/\t/, $a);
  
  if (lc(@b[0]) ne lc($project)) { next; }
  
  if ($#b == 1) { $failCmd{$project} = @b[1]; next; }

  $ranOneTest = 1;

  if (@b[2] ne "\"")
  {
  open(F, @b[2]) || die ("Can't find @b[2].");
  $thisFile = $lastOpen = @b[2];
  }
  else
  {
  open(F, $lastOpen) || die ("Can't re-open $lastOpen.");
  }
  
  my $size = "";
  
  if ($rows{@b[1]}) { $size = $rows{@b[1]}; } else { print "@b[1] has nothing.\n"; }
  
  my $almost = @b[3]; $almost =~ s/\$\$//g;

  @b[3] =~ s/\$\$/$size/g;
  print "Trying @b[3]\n";
  my $success = 0;
  my $nearSuccess = "";
  while ($f = <F>)
  {
    #print "@b[3] =~? $f";
    if ($f =~ /@b[3]/) { $success = 1; last; }
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
	if ($nearSuccess) { print "Likely suspect(s): $nearSuccess"; }
	print "TEST RESULTS:(notes) $project-@b[3],0,1,0,Look <a href=\"file:///$thisFile\">here</a>\n";
	$printFail = 1;
  }
}

if ($majorList)
{
  $majorList =~ s/,//g;
  print "TEST RESULTS:$project table count,0,$countMismatch,0,$majorList\n";
}

if ($printFail && $failCmd{$project}) { print "RUN THIS: $failCmd{$project}\n"; }

if ($ranOneTest && !$printFail) { print "EVERYTHING WORKED! YAY!\n"; }

if (($openPost) && ($fileToOpen))
{
  print "Opening $fileToOpen\n";
  `$fileToOpen`;
}

sub usage
{
print<<EOT;
directory
csv = tables to highlight
-t specifies a CSV of important tables to track
-e opens the i7t.txt file
-o opens the offending file post-test
-p specifies the project
-s specifies the project in shorthand
(directory) looks for story.ni in a different directory
EOT
exit;
}