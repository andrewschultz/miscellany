##################################
#salf.pl
#section alphabetizer
#
# currently only for smart.otl but it can be expanded
#
# usage salf.pl
#
# recommended: salf.pl pc, salf.pl sc, salf.pl btp

#todo: test case
#got stuff!!!
#got stuff!!!!

#use Data::Dumper qw(Dumper);
#use List::MoreUtils qw(uniq);
use POSIX;
use File::Compare (compare);

use strict;
use warnings;

########################constants
my $logFile = __FILE__;
$logFile =~ s/.pl$/-log.txt/i;

##########################
#options

my $runTest = 0;
my $undoQuestionComments = 0;
my $openDif = 0;

##########################
#variables

my $t = time();
my $didSomething = 0;
my $dupBytes = 0;
my %got = ();
my $noGlobals = 0;
my $dupes;
my @sects = ();
my $toSplit = "";
my $count = 0;
my $defDir = "";
my $myd = getcwd();

my %list;
$list{"pc"} = "pc";
$list{"sc"} = "sc,sc1,sc2,sc3,sc4,scfarm,sce,scd,scc,scb,sca";
$list{"btp"} = "btp-rej,btp,btp-dis,btp-book,btp1,btp2,btp3,btp4,btp-farm,btp-e,btp-d,btp-c,btp-b,btp-a";

if ($myd eq "C:\\games\\inform\\compound.inform\\Source") { $toSplit = $list{"pc"}; $defDir = "sc"; }
if ($myd eq "C:\\games\\inform\\slicker-city.inform\\Source") { $toSplit = $list{"sc"}; $defDir = "sc"; }
if ($myd eq "C:\\games\\inform\\buck-the-past.inform\\Source") { $toSplit = $list{"btp"}; $defDir = "btp"; }

my $defaultProj = "btp";
my $logFileEdit = $defaultProj;

while ($count <= $#ARGV)
{
  my $arg = lc($ARGV[$count]);
  for ($arg)
  {
    /^-?e$/ && do { `$logFile`; exit(); };
    /^-?od$/ && do { $openDif = 1; $count++; next; };
    /^-?(c|tc|ct)$/ && do
	{
	  if ($arg =~ /t/) { $runTest = 1; }
	  checkLastRun(defined($ARGV[$count+1]) ? $ARGV[$count+1] : $defaultProj);
	  exit;
    };
    /^-?q$/ && do { $undoQuestionComments = 1; $count++; next; };
	if ($toSplit)
	{
	  die ("Second split-command $arg tried to overwrite $toSplit at $count.");
	}
	else
	{
	  $toSplit = $arg;
    }
  }
  if ($arg eq $defDir) { print "No need to specify project when you're in its directory.\n"; $count++; next; }
  $count++;
}

if (!$toSplit)
{
  print "Need to either\n1) be in a source directory, or\n2) -btp for all of BTP. -pc/-sc for PC and SC are also possible but won't do much."; exit;
}

if ($toSplit =~ /^-/) { $toSplit =~ s/^-//; }

@sects = split(/,/, $toSplit);

if ($#sects == -1) { print "Need a CSV of sections, or use -pc for ProbComp, -sc or BTP.\n"; exit; }

my $infile = "c:\\writing\\smart.otl";
my $outfile = "c:\\writing\\temp\\smart.otl";

open(A, "$infile");
open(B, ">$outfile");

my $mysect;

while ($a = <A>)
{
  print B $a;
  if ($a =~ /^\\/)
  {
    for $mysect (@sects)
	{
	  if ($a =~ /^\\$mysect[=\|]/) { print "Alphabetizing $a\n"; alfThis(); }
	}
  }
}

close(A);
close(B);

if (!compare($infile, $outfile)) { print "Nothing changed after sorting. No recopying done.\n"; exit(); }

if (!$didSomething) { print "Didn't sort anything!\n"; exit; }

my $outDup = (-s $outfile) + $dupBytes;

if ((-s $infile) != $outDup)
{
  print "Uh oh, $infile and $outfile(" . ($dupBytes < 0 ? "+" : "") . "$dupBytes) didn't match sizes. Bailing.\n";
  print "" . (-s $infile) . " for $infile, " . (-s $outfile) . " for $outfile, total $outDup.\n";
  print "" . lines($infile) . " lines for $infile, " . lines($outfile) . " liness for $outfile.\n";
  if ($openDif)
  {
  `sort $infile > c:\\writing\\temp\\smart-b4.otl`;
  `sort $outfile > c:\\writing\\temp\\smart-af.otl`;
  `wm c:\\writing\\temp\\smart-b4.otl c:\\writing\\temp\\smart-af.otl`
  }
  else
  {
    print "Run -od to see differences alphabetized.\n";
  }
  exit;
}

#die("$dupes duplicates $dupBytes bytes duplicated.");
my $cmd = "copy $outfile $infile";
print "$cmd\n";
`$cmd`;

#################################################
#subroutines

sub alfThis
{
  $didSomething = 1;
  my @lines = ();
  my @uniq_no_case = ();
  if ($noGlobals) { %got = (); }

  while ($a = <A>)
  {
    chomp($a);
	if ($undoQuestionComments && ($a =~ /^#\?/))
	{
	  $a =~ s/^#\?//;
	  $dupBytes -= 2;
    }
    if ($a !~ /[a-z0-9]/i)
    {
      #print "Last line $lines[-1]\n";
      last;
    }
    push(@lines, $a);
  }
  my @x = sort { comm($a) <=> comm($b) || "\L$a" cmp "\L$b" } @lines;
  #@x = @lines;

  for my $y (@x)
  {
    if (defined($got{simp($y)}) && ($got{simp($y)} == 1))
	{
	  print "Duplicate $y\n";
	  $dupBytes += length(lc($y))+2;
	  $dupes++;
	  #print "$dupBytes/$dupes total.\n";
	  next;
    }
	$got{simp($y)} = 1;
	push(@uniq_no_case, $y);
  }


  print B join("\n", @uniq_no_case);
  if ($#uniq_no_case > -1) { print B "\n"; }
  print B "$a\n";
  #print "$#lines ($#uniq_no_case unique) shuffled\n";
  return;
}

sub simp
{
  my $temp = $_[0];
  $temp = lc($_[0]);
  $temp =~ s/[\.!\/\?]//g;
  return $temp;
}

sub comm
{
  if ($_[0] =~ /^#/) { return 1; }
  return 0;
}

sub updateLogFile
{
  my $writeString = "";
  my $gotOne = 0;
  open(A, $logFile) || die("Can't update $logFile.");
  while ($a = <A>)
  {
    if ($a =~ /^#/) { next; }
    chomp($a);
    my @csv = split(/,/, $a);
    if ($a =~ /^$logFileEdit/)
	{
	  $writeString .= "$logFileEdit,$csv[1],$t\n";
	  $gotOne = 1;
	}
	else
	{
	  $writeString .= $a;
	}
  }
  close(A);
  open(A, ">$logFile") || die ("Can't open $logFile for editing.");
  if (!$gotOne) { print A "$logFileEdit,7,$t\n"; print "Got a new entry for $logFileEdit, put into $logFile.\n"; }
  print A $writeString;
  close(A);
}

sub checkLastRun
{
  my $line;

  open(A, $logFile) || die ("Can't open $logFile.");

  while ($line = <A>)
  {
    my @time = split(/,/, $line);
	if ($#time < 2) { print "Line $. ($_[0]) needs to be of the form project,okay wait time,last time run.\n"; }
	if ($time[2] < 500) { $time[2] *= 86400; } # can specify days not seconds
	my $delta = $t - $time[1] + $time[2];
	if ($delta > 0)
	{
	  if ($runTest) { print "TEST RESULTS: $t,0,1,0,$delta seconds overdue: salf.pl $t\n"; }
	  else { print "Project $t needs to be run. It is $delta seconds overdue.\n"; }
	}
  }
  close(A);
}