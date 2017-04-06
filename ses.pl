##############################
#
#ses.pl
#
#calculates the number of open and new files in Notepad++
#
#no cmd line arguments besides e and ?

use strict;
use warnings;

#######################constant(s)
my $outputFile = __FILE__;
$outputFile =~ s/pl$/txt/i;
my $npSes = "C:\\Users\\Andrew\\AppData\\Roaming\\Notepad++\\session.xml";
my $tabMax = 25;
my $newMax = 15;
my $tabMin = 10;
my $newMin = 5;

#######################variable(s)
my %sizes;

my $totalFiles=0;
my $newFiles=0;
my $tabsOverStreak = 0;
my $newOverStreak = 0;
my $lastTabs = 0;
my $lastNew = 0;
my $newInc = 0;
my $tabsInc = 0;

my $count = 0;

#########################option(s)
my $toOutput = 0;
my $analyze = 0;
my $htmlGen = 0;

while ($count <= $#ARGV)
{
  my $arg = $ARGV[$count];

  for ($arg)
  {
  /^-?e$/ && do { `$npSes`; exit(); };
  /^-?o$/ && do { $toOutput = 1; $count++; next; };
  /^-?a$/ && do { $analyze = 1; $count++; next; };
  /^-?h$/ && do { $htmlGen = 1; $count++; next; };
  usage();
  }
}

open(A, $npSes) || die ("Can't open $npSes");

while ($a = <A>)
{
  chomp($a);
  if ($a !~ /backupfilepath/i) { next; }
  my @b = split(/\"/, $a);
  my $fileName = $b[17];
  my $fileBackup = $b[19];
  if ($a =~ /^[ \t]*<File /)
  {
    $totalFiles++;
    if ($a =~ /\"new [0-9]+\"/)
    { $newFiles++; }
	if ($fileName =~ /^new [0-9]/ && (-f "$fileBackup"))
	{
	  $sizes{$fileName} = -s "$fileBackup";
	}
  }

}

my $news;

for my $x (sort {$sizes{$a} <=> $sizes{$b}} keys %sizes)
{
  $news .= "$x ($sizes{$x})<br />";
  $count++; if ($count == 5) { last; }
}

print "TEST RESULTS:Notepad++ tabs,25,$totalFiles,0,(none yet)\n";
print "TEST RESULTS:Notepad++ new files,15,$newFiles,0,$news\n";

if ($toOutput)
{
  open(A, ">>$outputFile");
  my ($second, $minute, $hour, $dayOfMonth, $month, $yearOffset, $dayOfWeek, $dayOfYear, $daylightSavings) = localtime(time());
  print A sprintf("%d-%02d-%02d %02d:%02d:%02d: $totalFiles total files, $newFiles new files.\n", $yearOffset+1900, $month+1, $dayOfMonth, $hour, $minute, $second);
  close(A);
}

if ($analyze)
{
  my @b;
  open(A, "$outputFile");
  while ($a = <A>)
  {
    chomp($a);
    $a =~ s/.*: //;
    @b = split(/, /, $a);
	for (@b) { $_ =~ s/ .*//g; }
	if ($b[0] > $tabMax) { $tabsOverStreak++; } else { $tabsOverStreak = 0; }
	if ($b[1] > $newMax) { $newOverStreak++; } else { $newOverStreak = 0; }
	if (($b[0] > $lastTabs) && ($lastTabs > $tabMin)) { $tabsInc++; } else { $tabsInc = 0; }
	if (($b[1] > $lastNew) && ($lastNew > $newMin)) { $newInc++; } else { $newInc = 0; }
	$lastNew = $b[1];
	$lastTabs = $b[0];
  }

  my @errs;
  if ($newOverStreak > 1) { push (@errs, "NEW TABS too big $newOverStreak days in a row."); }
  if ($newInc > 1) { push (@errs, "NEW TABS grew $newOverStreak days in a row."); }
  if ($tabsOverStreak > 1) { push (@errs, "OVERALL TABS too big $tabsOverStreak days in a row."); }
  if ($tabsInc > 1) { push (@errs, "OVERALL TABS grew $tabsOverStreak days in a row."); }
  if ($#errs > -1)
  {
    if ($htmlGen)
	{
	  open(B, ">c:\\writing\\scripts\\ses.htm");
	  print B "<html><title>Streak Error Stuff</title><body bgcolor=red>\n";
	  for (@errs) { print B "<font size=+3>$_</font>\n"; }
	  close(B);
	}
	else
	{
	  print join("\n", @errs);
	}
  }
  else
  {
    print "All good!\n";
  }
}

###############################

sub usage
{
print<<EOT;
-a = analyze
-h = to html
-o = output to file
-e = edit source file
EOT
exit;
}