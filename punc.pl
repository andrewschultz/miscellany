# punc.pl
#
# e edits punc.txt
#
# Inform 7 source scanning script
# with punc.txt, makes sure there are no gross punctuation errors in various table entries
# originally just for Stale Tales Slate random entries but now expanded to other projects
#
# punc.txt has more annotations on what things mean
#
#example
#hs - horrendous songs	0,1,-1,-1	1,1,-1,-1
#row 0 has 1 start capital, -1 punctuation -1 quotes (single)
#
# each table column check has field values: start capital, punctuation and quotes
#
# 3 means ALL CAPS
# 2 means Title Case
# 1 means yes, always
# 0 means doesn't matter
# -1 means no, never
#
# overridden by [p] in the source file
#
# -? gives usage
#

use warnings;
use strict;

######################options
my $showOK = 0;

######################counters
my $errsYet = 0;
my $errs = 0;
my $allLines = 0;
my $matchQuotes = 0;
my $totalSuccesses = 0;
my $head = "";
my $noerr;
my $anyerr;

my @lineList = ();

######################globals that don't need to be globals but I'm lazy
my $myIndex;
my $capCheck;
my $puncCheck;
my $quoCheck;

######################global I should really change, like, ASAP
my $wrongString;

######################hashes
my %titleLC;
my %myFile;
my %searches;
my %ignore;
my %got;
my %entry;

if (defined($ARGV[0]) && ($ARGV[0] eq "e")) { `c:\\writing\\dict\\punc.txt`; exit; }

# -cl used to be "fix checklist" where I tacked on periods
# now it can just be done with s/([^\.])\"/\.\"/
#

my @titleWords = ("but", "by", "a", "the", "in", "if", "is", "it", "as", "of", "on", "to", "or", "sic", "and", "at", "an", "oh", "for", "be", "not", "no", "nor", "into", "with", "from");
addTitles();

if (-f "punc.txt") 
{
open(A, "punc.txt") || die ("Can't open punc.txt.");
}
else
{
open(A, "c:/writing/dict/punc.txt") || do { print ("Can't open c:/writing/dict/punc.txt."); usage(); }
}

my $lineNum = 0;
my $gameVal = "";
my $c = "";

my $tempLine;
my $myLine;

while ($myLine = <A>)
{
  $lineNum++;
  if ($myLine =~ /#/) { next; }
  if ($myLine =~ /;/) { last; }
  chomp($myLine);
  if (length($myLine) == 0) { next; }
  if ($myLine =~ /^VALUE=/) { $myLine =~ s/VALUE=//g; $gameVal = $myLine; $myFile{$gameVal} = "c:\\games\\inform\\$gameVal.inform\\source"; next; }
  if ($myLine =~ /^FILES=/) { $myLine =~ s/FILES=//g; $myFile{$gameVal} = $myLine; print "$gameVal -> $myLine\n"; next; }
  $tempLine = $myLine;
  $tempLine =~ s/^[^\t]*\t//;
  $c = $myLine; $c =~ s/\t.*//;
  $searches{$c} = $tempLine;
  if (!$tempLine) { print "Warning: No data for TABLE OF $c.\n"; }
}

close(A);

my %warning;
$warning{"shuffling"} = 1;
$warning{"roiling"} = 1;

my %map; # map shorthand to loghand
$map{"s"} = "shuffling";
$map{"sa"} = "shuffling";
$map{"roi"} = "roiling";
$map{"b"} = "shuffling,roiling";
$map{"pc"} = "compound";
$map{"sc"} = "slicker-city";
$map{"btp"} = "buck-the-past";
$map{"btp"} = "compound,slicker-city,buck-the-past";

for my $argnum (0..$#ARGV)
{
  my $proj;
  if ($ARGV[$argnum] eq "-h") { usage(); }
  if ($ARGV[$argnum] eq "-i") { $matchQuotes = 0; }
  if ($map{$ARGV[0]})
  { $proj = $map{$ARGV[$argnum]}; }
  else
  { $proj = $ARGV[$argnum]; }
  my @projs = split(/,/, $proj);
  for my $myproj(@projs) { storyTables($myproj); }
}

sub storyTables
{

my $fileToRead = $myFile{$_[0]}; if (!$fileToRead) { die ("No file defined for $_[0]."); }

my $totalErrors = 0;
$totalSuccesses = 0;
my @parseAry = ();

open(A, $fileToRead) || die ("Can't open $fileToRead.");

$allLines = 0;

print "Table parsing for $fileToRead:\n";

my $inTable = 0;

while ($a = <A>)
{
  $allLines++;
  if ($a =~ /^table of /)
  {
    if (($a =~ /\t/) || ($a =~ /megachatter/)) { next; }
    chomp($a);
    $head = lc($a); $head =~ s/^table of //g; $head =~ s/[ \t]*\[.*//g;
	<A>;
    $errsYet = 0; $errs = 0;
	#print "$head: $searches{$head}\n";
    if (!$searches{$head})
	{
	  if (!defined($warning{$_[0]}) || (defined($ignore{$head}) && $ignore{$head}))
	  { }
	  else
	  { print "Warning, no entry in punc.txt for $head.\n"; }
	}
	else
	{
	  if (!$ignore{$head})
	  {
      $got{$head} = 1;
      $inTable = 1;
	  my $currentParsing = $searches{$head};
	  @parseAry = split(/\t/, $currentParsing);
	  #if ($#parseAry < 3) { die("Bad # of arguments ($#parseAry) in cluster $currentParsing, line $allLines."); }
	  #print "Changing to @parseAry\n";
	  #print "Starting $head.\n";
	  }
	  next;
	}
  }
	if ($inTable == 1)
	{
	  if ($a !~ /^\"/i)
	  {
	    if ($errs)
		{ print "===============Finished $head. $errs errors.\n"; $totalErrors += $errs; }
		else
		{ $noerr .= " $head"; }
		$errsYet = 0; $errs = 0; $inTable = 0; $lineNum = 0; next;
	  }
	}
    if ($inTable)
	{
	  $lineNum++;
	  chomp($a);
	  #print "Trying @parseAry\n";
	  for my $thisParse (@parseAry)
	  {
	    my @tempParse = split(/,/, $thisParse);
		$myIndex = $tempParse[0];
        $capCheck = $tempParse[1];
        $puncCheck = $tempParse[2];
        $quoCheck = $tempParse[3];
		#print "Looking up $a\n";
		lookUp($a);
	  }
	}
}

#now check to make sure everything in punc.txt is used
for my $key (sort keys %entry)
{
  #print "$key/$entry{$key} vs $_[1]/$ignore{$key}/$got{$key}\n";
  if ((!$ignore{$key}) && (!$got{$key}) && ($entry{$key} eq $_[0]))
  { print "WARNING punc.txt pointed to table $key but story.ni did not.\n"; }
}

if (!$anyerr) { print "No tables had errors!\n"; }
else
{
if ($showOK) { print "OK tables:$noerr.\n"; }
}
my $listOut = join(" / ", @lineList);

print "TEST RESULTS:$_[0] punctuation,0,$totalErrors,$totalSuccesses,$listOut\n";

close(A);

}

sub lookUp
{
      my $adNotTitle = 0;
      my $temp = $_[0];
	  my $count;
	  
	  if ($temp =~ /\[p\]/i) { $totalSuccesses++; return; }
	  if ($temp =~ /\ttrue/) { $adNotTitle = 1; }
      $temp =~ s/^\"//gi;
      $temp =~ s/\".*//g;
	  $temp =~ s/' \/ '/ /g;
	  $temp =~ s/\[[^\]]\]//g;
	  $temp =~ s/\[a-word-u\]/Ass/g;
	  $temp =~ s/\[d-word-u\]/Damn/g;
	  $temp =~ s/\[n-t\]/Nate/g;
	  if ($head =~ /ad slogans/)
	  {
	    if ($_[0] =~ /!\"$/) { err(); print "$allLines($lineNum): $_[0] needs TRUE after tab.\n"; return; }
	  }
	  if ($head =~ /(random books|biopics)/)
	  {
	    if ($_[0] !~ /\[r\]/) { err(); print "$allLines($lineNum): $_[0] needs [r].\n"; return; }
	    if ($temp !~ / by /) { err(); print "$allLines($lineNum): $temp needs by.\n"; return; }
	  }
	  if ($temp =~ /\[\]/) { err(); print "$allLines($lineNum): $temp brackets with nothing in them.\n"; }
	  if (($temp =~ /[a-zA-Z][\.!\?] +[a-z]/) && ($temp !~ /[!\?] by/)) { if ($temp !~ /(i\.e|e\.g)\./i) { err(); print "$allLines($lineNum): $temp starts sentence with lower-case.\n"; }}
	  if ($temp =~ /â€œ/) { err(); print "$allLines($lineNum): $temp has smart quotes, which you may not want\n"; }
	  if (($capCheck == 3) && ($temp =~ /[a-z]/)) { err(); print "$allLines($lineNum): $temp needs to be ALL CAPS.\n"; }
	  if (($capCheck == 2) && ($adNotTitle == 0) && (!titleCase($temp))) { err(); print "$allLines($lineNum): $temp needs to be Title Case, change $wrongString.\n"; }
	  if (($capCheck == 1) && ($temp =~ /^[a-z]/)) { err(); print "$allLines($lineNum): $temp need caps.\n"; return; }
	  if (($capCheck == -1) && ($temp =~ /^[A-Z]/)) { err(); print "$allLines($lineNum): $temp wrong caps.\n"; return; }
	  if ($quoCheck == 1) { $count = ($temp =~ tr/'//); if (($count < 2) || (($temp !~ /^'/) && ($temp !~ /'$/))) { err(); print "$allLines($lineNum): $temp not enough quotes.\n"; return; } }
	  if ($quoCheck == -1) { if (($temp =~ /'$/) && ($temp =~ /^'/)) { err(); print "$allLines($lineNum): $temp too quotey.\n"; return; } }
      my $gotit = ($temp =~ /[\.\!\"\?]['\)]?$/);
      if ($gotit && ($puncCheck == -1)) { err(); print "$allLines($lineNum): $temp unnecc punctuation.\n"; }
      if (!$gotit && ($puncCheck==1)) { err(); print "$allLines($lineNum): $temp missing punctuation.\n"; }
      if ($temp =~ /,[a-zA-Z]/) { err(); print "$allLines($lineNum): $temp comma no space.\n"; }
      if ($temp =~ /^!\./) { err(); print "$allLines($lineNum): $temp clashing punctuation.\n"; }
	  my $temp2 = $temp; $temp2 =~ s/[a-z]\.?'[a-z]//gi; $count = ($temp2 =~ tr/'//); if ($count % 2) { err(); print "$allLines($lineNum): $temp ($count apostrophe(s))\n"; return; }
      if (($temp =~ /[a-z]' /i) || ($temp =~ / '[a-z]/)) { if ($temp !~ /'[a-z]+'/i) { err(); print "$allLines($lineNum): $temp possible unbracketed apostrophe.\n"; } }
      if (($temp =~ /^'/) ^ ($temp =~ /'$/)) { $count = ($temp =~ tr/'//); if ($count == 1) { err(); print ("$allLines($lineNum): $temp unmatched quotes.\n"); return; } }
      if (($temp =~ /^'/) && ($temp =~ /'$/)) { $temp =~ s/'//g; }
      if ($temp =~ /^ /) { err(); print "$allLines($lineNum): $temp leading space.\n"; }
      if ($temp =~ /''/) { err(); print "$allLines($lineNum): $temp two single quotes.\n"; }
	  $totalSuccesses++;
}

sub err
{
    if (!$errsYet) { print "ERRORS IN $head:=================================\n"; } $errs++;
    $errsYet = 1;
	$anyerr = 1;
	push (@lineList, $allLines);
}

sub addTitles
{
  for my $x (@titleWords) { $titleLC{$x} = 1; }
}

sub titleCase
{
  my $temp = $_[0]; $temp =~ s/\[.*?\]//g; $temp =~ s/'[a-z]+//g;
  my @q = split(/\b/, $temp);
  my @wrongs = ();
  for my $word (@q)
  {
    if (($word =~ /^[a-z]/) && ($titleLC{$word} == 0)) { push(@wrongs, $word); }
  }
  if ($#wrongs == -1) { return 1; }
  $wrongString = join("/", @wrongs);
  return 0;
}

sub usage
{
print<<EOT;
start capital/punctuation/quotes

Caps-only
3 = ALL CAPS 2 = title case

1 = necc 0 = either way -1 = *don't* include
EOT
exit;
}