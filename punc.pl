# punc.pl
#
# e edits punc.txt
#
# can be redone to have a hash of arrays of commands for each table
# Inform 7 source scanning script
# with punc.txt, makes sure there are no gross punctuation errors in various table entries
# originally just for Stale Tales Slate random entries but now expanded to other projects
#
# punc.txt has more annotations on what things mean
# punc-priv.txt is for private projects I don't want to show the source for yet
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

use List::MoreUtils qw(uniq);
use lib "c:/writing/scripts";
use i7;
use warnings;
use strict;

######################options
my $showOK = 0;
my $printWarnings = 0;
my $getFirstError = 0;
my $launch = 0;
my $blankWarn = 0;

######################counters
my $errsYet = 0;
my $errs = 0;
my $allLines = 0;
my $matchQuotes = 0;
my $totalSuccesses = 0;
my $head = "";
my $noerr;
my $anyerr;
my $default;

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
my %fileLineOpen;

my $rf = "c:\\writing\\dict\\punc.txt";
my $rf2 = "c:\\writing\\dict\\punc-priv.txt";

# -cl used to be "fix checklist" where I tacked on periods
# now it can just be done with s/([^\.])\"/\.\"/
#

my @titleWords = ("but", "by", "a", "the", "in", "if", "is", "it", "as", "of", "on", "to", "or", "sic", "and", "at", "an", "oh", "for", "be", "not", "no", "nor", "into", "with", "from");
addTitles();

if (-f $rf)
{
open(A, "$rf") || die ("Can't open $rf.");
}
else
{
die ("No $rf. Need to specify another in the file.");
}

my $lineNum = 0;
my $gameVal = "";
my $c = "";

my $tempLine;
my $myLine;

my $count;

###############################
#first find the default project

while ($myLine = <A>)
{
  if ($myLine =~ /^DEFAULT=/) { $default = $myLine; $default =~ s/DEFAULT=//g; chomp($default); last; }
}
if (!$default) { print "WARNING no default set.\n"; }
close(A);

#################code kept so we can see mass-commenting later
=pod
=cut

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
$map{"as"} = "compound,slicker-city,buck-the-past";

if ($#ARGV == -1)
{
  if ($default)
  {
    print "Going with default, $default.\n";
	getTableList($default);
    storyTables($default);
  }
  else { print "No default. Define with DEFAULT=\n"; }
  exit();
}

my @projs = ();

my $argcount = 0;

while ($argcount <= $#ARGV)
{
  my $arg = $ARGV[$argcount];
  # print "$argcount $arg $#ARGV\n";
  for (lc($arg))
  {
  /^-?c$/ && do { my $thisfile = __FILE__; `$np $thisfile`; exit; };
  /^-?e$/ && do { `$rf`; exit; };
  /^-?ep$/ && do { `$rf2`; exit; };
  /^-?h$/ && do { usage(); };
  /^-?b$/ && do { $blankWarn = 0; $argcount++; next; };
  /^-?nb$/ && do { $blankWarn = 1; $argcount++; next; };
  /^-?l$/ && do { $launch = 1; $argcount++; next; };
  /^-?f$/ && do { $getFirstError = 1; $argcount++; next; };
  /^-?i$/ && do { $matchQuotes = 0; $argcount++; next; };
  my @tempProj = split(/,/, $arg);
  for (@tempProj) { if ($map{$_}) { $_ = $map{$_}; } }
  print ("Adding @tempProj\n");
  @projs = (@projs, @tempProj);
  $argcount++;
  }
}

@projs = uniq(@projs);

for my $myProj (@projs)
{
  getTableList($myProj);
  storyTables($myProj);
}

if ($launch)
{
  for (keys %fileLineOpen)
  {
    my $cmd = "start \"\" $np \"$_\" -n$fileLineOpen{$_}";
	print "RUNNING COMMAND: $cmd\n";
	`$cmd`;
  }
}

##################################################
# subdirectories

#################################
#this reads in what to do with the various tables from punc.txt, for whatever story.ni file
#

sub getTableList
{

%ignore = ();
%searches = ();

my $inCurrent = 0;
my $gotAny = 0;
my $readPrivYet = 0;

open(A, "$rf") || die ("Can't open $rf");

while ($myLine = <A>)
{
  $lineNum++;
  if ($myLine =~ /#/) { next; }
  if ($myLine =~ /;/)
  {
    if ($readPrivYet) { last; }
	$readPrivYet++;
	open(A, "$rf2") || die ("Couldn't open $rf2 after $rf.");
	next;
  }
  if ($myLine =~ /^DEFAULT=/) { next; }
  chomp($myLine);
  if (length($myLine) == 0) { next; }
  if (($inCurrent) && ($myLine =~ /^====/)) { last; }
  if ($myLine =~ /^-/) { $myLine =~ s/^-//g; $ignore{$myLine} = 1; next; }
  if ($myLine eq "VALUE=$_[0]")
  {
    $inCurrent = 1;
	$gotAny = 1;
	$myLine =~ s/VALUE=//g;
	$gameVal = $myLine;
	my @tempAry = ("c:\\games\\inform\\$gameVal.inform\\source\\story.ni");
	$myFile{$gameVal} = \@tempAry;
	next;
  }
  elsif ($myLine =~ /^VALUE=/i) { $inCurrent = 0; }
  if (!$inCurrent) { next; }
  if ($myLine =~ /^FILES=/)
  {
    $myLine =~ s/FILES=//g;
	my @tempAry = split(/,/, $myLine);
	$myFile{$gameVal} = \@tempAry;
	print "$gameVal -> $myLine\n"; next; }
  $myLine = lc($myLine);
  if ($myLine =~ /^table of /) { print "Don't need (table of) at line $lineNum, $myLine\n"; $myLine =~ s/^table of //g; }
  $tempLine = $myLine;
  $tempLine =~ s/^[^\t]*\t//;
  $c = $myLine; $c =~ s/\t.*//;
  my @grp = split(/\t/, $tempLine);
  for my $g (@grp)
  {
    if ($g =~ /[0-9]=TF/) { next; }
    $count = ($g =~ tr/,//);
	if ($count != 3) { print "$lineNum: $g wrong # of commas: $count\n"; }
  }
  $searches{$c} = $tempLine;
  if (!$tempLine) { print "Warning: No data for TABLE OF $c.\n"; }
}

close(A);
if (!$gotAny) { die("Found nothing for $_[0], exiting."); }
}

################################
#this processes the story tables
#

sub storyTables
{

my @fileArray = @{$myFile{$_[0]}};
my $fileToRead;

my $tableWarnings = 0;
my $totalErrors = 0;

for $fileToRead (@fileArray)
{

if (! -f $fileToRead) { die ("No file defined for $_[0]."); }

$totalSuccesses = 0;
my @parseAry = ();

open(A, $fileToRead) || die ("Can't open $fileToRead.");

$allLines = 0;

print "Table parsing for $fileToRead:\n";

my $inTable = 0;

my %alreadyWarn;

while ($a = <A>)
{
  $allLines++;
  if (($a =~ /^table of /) && ($inTable == 0))
  {
    chomp($a);
	$a =~ s/ \(continued\)//;
    $head = lc($a); $head =~ s/^table of //g; $head =~ s/[ \t]*\[.*//g;
	<A>; $allLines++;
    $errsYet = 0; $errs = 0;
    if (!$searches{$head})
	{
	  if (!$ignore{$head} && !$alreadyWarn{$head})
	  { print "Warning, no entry in punc.txt for $head at line $..\n"; $tableWarnings++; $alreadyWarn{$head} = $.; }
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
	  #print "Changing $head to @parseAry\n";
	  #print "Starting $head.\n";
	  }
	  next;
	}
  }
	if ($inTable == 1)
	{
	  if ($a =~ /\t\t/) { print "Warning: double tabs at line $..\n"; }
	  if (	($a !~ /\t\"/) && ($a !~ /^\"/))
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
	  #print "Trying $a/@parseAry\n";
	  if ($a =~ /\[p\]/) { $totalSuccesses++; next; }
	  if ($parseAry[0] =~ /[tf]/)
	  {
	    my @entryArray = split(/\t/, $a);
	    $myIndex = $parseAry[0];
		$myIndex =~ s/[tf]//g;
		if ($entryArray[$myIndex] !~ /(true|false)/i)
		{
		  print "True/False goof in line $. in $head.\n";
		}
	  }
	  for my $thisParse (@parseAry)
	  {
	    my @tempParse = split(/,/, $thisParse);
		$myIndex = $tempParse[0];
        $capCheck = $tempParse[1];
        $puncCheck = $tempParse[2];
        $quoCheck = $tempParse[3];
		my @entryArray = split(/\t/, $a);
		if ($myIndex > $#entryArray) { if ($printWarnings) { print "No element $myIndex at line $lineNum of $head, $#entryArray\n"; } next; }
        if ($entryArray[$myIndex] eq "\"\"" || $entryArray[$myIndex] eq "--")
        {
          if ($printWarnings) { print "Empty entry $myIndex empty.\n"; }
		  next;
        }
		#print "Looking up $a\n";
		if ($head =~ /ad slogans/)
	    {
	      if ($a =~ /!\"/)
		  {
		    if ((!defined($entryArray[1])) ||
			  ($entryArray[1] !~ /true/))
			{ err(); print "$allLines($lineNum): $a needs TRUE after tab.\n"; }
		    $capCheck = 1;
			if (lookUp($entryArray[$myIndex]))
			{
			}
			next;
		  }
	    }
		if (lookUp($entryArray[$myIndex]))
		{
		  $fileLineOpen{$fileToRead} = $. if (!$fileLineOpen{$fileToRead} || !$getFirstError);
		}
	  }
	}
}
close(A);
}

#now check to make sure everything in punc.txt is used
for my $key (sort keys %searches)
{
  #print "$key/$entry{$key} vs $_[1]/$ignore{$key}/$got{$key}\n";
  if ((!$ignore{$key}) && (!$got{$key}))
  { print "WARNING punc.txt pointed to table $key but I could not find it in the file list.\n"; }
}

if (!$anyerr) { print "No tables had errors!\n"; }
else
{
if ($showOK) { print "OK tables:$noerr.\n"; }
}
my $listOut = join(" / ", @lineList); if ($listOut) { $listOut = "Lines: $listOut"; }

print "TEST RESULTS:$_[0] punctuation,0,$totalErrors,$totalSuccesses,$listOut\n";

if ($tableWarnings) { print ("We need to flag $tableWarnings tables.\n"); }

close(A);

}

sub lookUp
{
      my $adNotTitle = 0;
      my $temp = $_[0];
	  my $temp2;
	  my $count;

	  if (($temp eq "--") && ($blankWarn))
	  {
	    print "WARNING: blank entry at line $..\n";
		return -1;
	  }

	  $temp =~ s/e\.g\. /eg /g;
	  $temp =~ s/etc\.([^\"])/etc $1/g;
	  $temp =~ s/a\.k\.a\. /aka /g;

	  if ($temp =~ /\ttrue/) { $adNotTitle = 1; }
      $temp =~ s/^\"//gi;
	  $temp =~ s/\[e[0-9]\]//gi;
      $temp =~ s/\".*//g;
	  $temp =~ s/[:,]//g;
	  $temp =~ s/' \/ '/ /g;
	  $temp =~ s/\[a-word-u\]/Ass/g;
	  $temp =~ s/\[d-word-u\]/Damn/g;
	  $temp =~ s/\[n-t\]/Nate/g;
	  $temp =~ s/\[['rbi]\]//g;
	  $temp =~ s/\[[^\]]\]/X/g;
	  #bracket out comments
	  $temp =~ s/^\[[^\]]+\]/X/;
	  $temp =~ s/\[[^\]]+\]$//g;
	  if ($head =~ /(random books|biopics)/)
	  {
	    if ($_[0] !~ /\[r\]/) { err(); print "$allLines($lineNum): $_[0] needs [r].\n"; return -1; }
	    if ($temp !~ / by /) { err(); print "$allLines($lineNum): $temp needs by.\n"; return -1; }
	  }
	  if ($temp =~ /\[\]/) { err(); print "$allLines($lineNum): $temp brackets with nothing in them.\n"; }
	  if (($temp =~ /[a-zA-Z][\.!\?] +[a-z]/) && ($temp !~ /[!\?] by/)) { if ($temp !~ /(i\.e|e\.g)\./i) { err(); print "$allLines($lineNum): $temp starts sentence with lower-case.\n"; } return -1; }
	  if ($temp =~ /â€œ/) { err(); print "$allLines($lineNum): $temp has smart quotes, which you may not want\n"; return -1; }
	  if (($capCheck == 3) && ($temp =~ /[a-z]/)) { err(); print "$allLines($lineNum): $temp needs to be ALL CAPS.\n"; return -1; }
	  if (($capCheck == 2) && ($adNotTitle == 0) && (!titleCase($temp))) { err(); print "$allLines($lineNum): $temp needs to be Title Case, change $wrongString.\n"; return -1; }
	  if (($capCheck == 1) && ($temp =~ /^[a-z]/)) { err(); print "$allLines($lineNum): $temp need caps.\n"; return -1; }
	  if (($capCheck == -1) && ($temp =~ /^[A-Z]/)) { err(); print "$allLines($lineNum): $temp wrong caps.\n"; return -1; }
	  if ($quoCheck == 1) { $count = ($temp =~ tr/'//); if (($count < 2) || (($temp !~ /^'/) && ($temp !~ /'$/))) { err(); print "$allLines($lineNum): $temp not enough quotes.\n"; return -1; } }
	  if ($quoCheck == -1) { if (($temp =~ /'$/) && ($temp =~ /^'/)) { err(); print "$allLines($lineNum): $temp too quotey.\n"; return -1; } }
      my $gotit = ($temp =~ /[\.\!\"\?]['\)]?$/);
      if ($gotit && ($puncCheck == -1)) { err(); print "$allLines($lineNum): $temp unnecc punctuation.\n"; }
      if (!$gotit && ($puncCheck==1) && ($temp !~ /\[(no line break|pre-lb|pre-brk)\]$/)) { err(); print "$allLines($lineNum): ($myIndex) missing punctuation.\n"; return -1; }
      if ($temp =~ /,[a-zA-Z]/) { err(); print "$allLines($lineNum): $temp comma no space.\n"; return -1; }
      if ($temp =~ /^!\./) { err(); print "$allLines($lineNum): $temp clashing punctuation.\n"; return -1; }
	  $temp2 = $temp; $temp2 =~ s/[a-z0-9\]]\.?'[a-z]//gi; $count = ($temp2 =~ tr/'//); if ($count % 2) { err(); print "$allLines($lineNum): $temp ($count apostrophe(s))\n"; return -1; }
      if (($temp =~ /[a-z]' /i) || ($temp =~ / '[a-z]/))
	  { # ?? shuffle to probably-ok in the future
	    $temp2 = $temp;
		$temp2 =~ s/'.+?(\.|\?|!)?'( |$)//gi;
	    if ($temp2 =~ /( '|' )/i)
		{ err(); print "$allLines($lineNum):\n$temp\n$temp2\npossible unbracketed apostrophe.\n"; return -1; }
      }
      if (($temp =~ /^'/) ^ ($temp =~ /'$/)) { $count = ($temp =~ tr/'//); if ($count == 1) { err(); print ("$allLines($lineNum): $temp unmatched quotes.\n"); return -1; } }
      if (($temp =~ /^'/) && ($temp =~ /'$/)) { $temp =~ s/'//g; }
      if ($temp =~ /^ /) { err(); print "$allLines($lineNum): $temp leading space.\n"; }
      if ($temp =~ /''/) { err(); print "$allLines($lineNum): $temp two single quotes.\n"; }
	  $totalSuccesses++;
	  return 0;
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
  my $temp = $_[0]; $temp =~ s/\[.*?\]//g; $temp =~ s/'[a-z]+//g; $temp =~ s/[\?!\.]//g;
  my @q = split(/[ -]/, $temp);
  my @wrongs = ();
  for my $word (@q)
  {
    if (($word =~ /^[a-z]/) && !defined($titleLC{$word})) { push(@wrongs, $word); }
  }
  if ($#wrongs == -1) { return 1; }
  $wrongString = join("/", @wrongs);
  return 0;
}

sub usage
{
print<<EOT;
See punc.txt for the syntax in the file.
-b/-nb = warn for blank entries (--) or not
-h help
-l launch after
-f launch first error, not last
-i don't bother to match quotes
EOT
exit;
}