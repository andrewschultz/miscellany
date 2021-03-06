##########################################
#pch.pl
#
#punctuation checker for my Inform and data files
#

use strict;
use warnings;


##################globals
my $datFile = "c:/writing/scripts/pch.txt";
my $test = 0;
my $debug = 0;

##########################variables
my %dirs;
my %repl;
my %tables;
my %wcard;

my $success = 0;
my $fail = 0;
my $totalFail = 0;

my @failArray;

my $proj = "slicker-city";


my $count = 0;
my $curDir = "";
my $curTable = "";
my $gotProj = 0;
my $inProject = 0;
my $inTable = 0;

open(B, $datFile);

while ($count <= $#ARGV)
{
  $a = $ARGV[$count];
  for ($a)
  {
    /^-?t$/ && do { $test = 1; $count++; next; };
    /^-?d$/ && do { $debug = 1; $count++; next; };
    /^-?e$/ && do { `$datFile`; exit; };
	if ($gotProj) { print "Only one project allowed.\n"; usage(); }
	$proj = $ARGV[$count];
	$gotProj = 1;
	$count++;
  }
}

my @b1;
my @c;
my @d;

my $projYet = 0;

while ($b = <B>)
{
  if (($b =~ /->/) && (!$projYet)) { chomp($b); @b1 = split(/->/, $b); $repl{$b1[0]} = $b1[1]; next; }
  if (($b =~ /\*/) && (!$projYet)) { chomp($b); @b1 = split(/\*/, $b); $wcard{$b1[0]} = $b1[1]; next; }
  if ($b =~ /^#/) { next; }
  if ($b =~ /^project=/i)
  {
    $projYet = 1;
    $inProject = 0;
    chomp($b);
	@c = split(/=/, $b);
	if ($proj eq $c[2]) { $proj = $c[2]; $inProject = 1; next; }
	@d = split(/,/, $c[1]);
	for (@d) { if ($proj eq $_) { $proj = $c[2]; $inProject = 1; last; } }
	next;
  }
  if (!$inProject) { next; }
  if ($b =~ /->/) { @b1 = split(/->/, $b); $repl{$b1[0]} = $b1[1]; next; }
  if ($b =~ /^!table/)
  {
    chomp($b); $b =~ s/^!//g; $tables{$b} = 1; $dirs{$b} = 0;
	#print "Emptying $b\n";
	next;
  }
  if ($b =~ /^table/)
  {
    chomp($b); $tables{$b} = 1; $curTable = $b; next;
  }
  chomp($b);
  $dirs{$curTable} = $b;
}

close(B);

open(A, "c:/games/inform/$proj.inform/Source/story.ni") || die ("No $proj. -t, -d and -e are the only options.");

$success = 0; $fail = 0; my $tab = 0;

OUTER:
while ($a = <A>)
{
  if ($a !~ /[a-z]/i) { if ($inTable) { print "$success success $fail fail\n"; } $inTable = 0; next; }
  if ($a =~ /^table/)
  {
  chomp($a);
  #print "Data for $a:\n";
  for $tab (keys %dirs)
  {
    #print "Comparing $a and $tab.\n";
    if ($a =~ /^$tab/)
	{
	  if (!$dirs{$tab})
	  {
	    #print "Skipping $a/$tab.\n";
		next OUTER;
	  }
	  $curDir = $dirs{$tab};
	  $inTable = 1; <A>; print "====$a\n"; $success = 0; $fail = 0; last;
	}
  }
  if (!$inTable) { print "$a not accounted for.\n"; }
  next;
  }
  if ($inTable)
  {
    chomp($a);
	if ($a =~ /\[ok\]/) { next; }
    seeOkay($curDir, $a);
  }
}

if ($test)
{
  my $joinStr = "ALL PASSED";
  if ($totalFail) { $joinStr=join("<br />", @failArray); }
  print "TEST RESULTS:$proj punctuation,0,$totalFail,0,$joinStr\n";
}
#print "$success success, $fail fail in $. lines\n";

sub seeOkay
{
  my $r;
  my $tempVal;
  my $tempDir;
  my @sepDirs = split(/:/, $_[0]);
  my @sepCols = split(/\t/, $a);
  for (0..$#sepDirs)
  {
    if (!$sepDirs[$_]) { next; }
    $tempDir = $sepDirs[$_];
    $tempVal = $sepCols[$_];
    $tempVal =~ s/^\"//g;
    $tempVal =~ s/\".*//g;
	if ($tempVal =~ /\"/) { failReg("Hosed quotes for $tempVal, line $.\n"); next; }
	for $r (keys %repl) { if ($tempVal =~ /\[$r\]/) { $tempVal =~ s/(\[$r\])/$repl{$r}/g; } }
	for $r (keys %wcard) { if ($tempVal =~ /\[$r[^\]]+\]/) { $tempVal =~ s/\[$r[^]]+\]/$wcard{$r}/g; } }
	if (($tempDir =~ /ignore-blank/i) && ($tempVal eq "--")) { next; }
	if ($tempDir =~ /nocaps/i)
	{
	  if ($tempVal =~ /^[A-Z]/)
	  {
	    failReg("Bad uppercase start for $tempVal, line $.\n");
	  } else { $success++; }
	}
	if ($tempDir =~ /sentcase/i)
	{
	  $tempVal =~ s/^\[[^\]]*\]//g;
	  $tempVal =~ s/^'//g;
	  if ($tempVal !~ /^[A-Z]/)
	  {
	    failReg("Bad sentence case for $sepCols[$_] -> $tempVal, line $.\n");
	  } else { $success++; }
	}
	if ($tempDir =~ /allcaps/i)
	{
	  if ($tempVal =~ /[a-z]/)
	  {
	    failReg("Bad all caps for $tempVal, line $.\n");
	  } else { $success++; }
	}
	if ($tempDir =~ /qmark/i)
	{
	  if ($tempVal !~ /\?$/)
	  {
	    failReg("Need ?-end for $tempVal, line $.\n");
	  } else { $success++; }
	}
	if ($tempDir =~ /titlecase/i)
	{
	  $tempVal =~ s/^\[[^\]]*\]//g;
	  $tempVal =~ s/ (of|the|on|out|in|and|to) //g;
	  if ($tempVal =~ / [a-z]/)
	  {
	    failReg("Bad title case for $sepCols[$_] -> $tempVal, line $.\n");
	  } else { $success++; }
	}
    if ($tempDir =~ /nopunc/i)
	{
      if ($tempVal =~ /[\.!\?](')?$/)
	  {
	    failReg("excess punctuation: $tempVal, line $.\n", 0);
	  } else { $success++; }
	}
    if ($tempDir =~ /endpunc/i)
    {
      if (($tempVal !~ /[\.!\?](')?$/) && ($tempVal !~ /\['\]'$/))
	  {
	    failReg("Punctuation error: $tempVal, line $.\n", 0);
	  }
      else { $success++; }
    }
  }
}

sub printD
{
  if ($debug == 1) { print $_[0]; }
}

sub failReg
{
  push (@failArray, $_[0]);
  if ($_[1])
  {
  print $_[0];
  }
  $fail++;
  $totalFail++;
}

sub usage
{
print<<EOT;
-d debug
-t test output
EOT
exit;
}