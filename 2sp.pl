######################################
#2sp.pl
#
#checks for double spaces and edits them back

use POSIX;
use strict;
use warnings;

#####################options
my $difference = 0;
my $copy = 0;
my $makeDifFile = 1;

#####################variables
my $inI6 = 0;
my $inComment = 0;
my $count = 0;

my $projYet = 0;
my $dir = ".";
my $projToParse;
my %ignoreHash;
my $myProj = initGuess();
my $foundDif = 0;

while ($count <= $#ARGV)
{
  my $arg = $ARGV[$count];
  print "$count $arg\n";
  for ($arg)
  {
  /^-?d$/ && do { $difference = 1; $copy = 0; $makeDifFile = 1; $count++; next; };
  /^-?c$/ && do { $difference = 0; $copy = 1; $makeDifFile = 0; $count++; next; };
  /^-?m$/ && do { $difference = 0; $copy = 0; $makeDifFile = 1; $count++; next; };
  /^-?\?$/ && do { usage(); };
  if ($projYet) { print "unknown flag/double project $arg\n"; usage(); }
  $myProj = $ARGV[0];
  $dir = "c:\\games\\inform\\$myProj.inform\\Source";
  $projYet = 1;
  $count++;
  }
}

###################constants
my $ignore = __FILE__;
$ignore =~ s/pl$/txt/i;

my $in = "$dir\\story.ni";
my $out = "$dir\\story.nsp";
my $dif = "$dir\\story.dif.txt";

open(A, $ignore);
while ($a = <A>)
{
  if ($a =~ /^#/) { next; }
  if ($a =~ /^;/) { last; }
  chomp($a);
  if ($a =~ /^PROJ=/i) { $projToParse = $a; $projToParse =~ s/^proj=//i; next; }
  $ignoreHash{$projToParse}{$a} = 1;
}

close(A);

open(A, $in);
open(B, ">$out");
if ($makeDifFile)
{
open(C, ">$dif");
}

while ($a = <A>)
{
  if ($a =~ /^-\)/) { $inI6 = 0; print B $a; next; }
  if (($a =~ /^\[/) && ($a !~ /\]/)) { $inComment = 1; print B $a; next; }
  if (($inComment) && ($a =~ /\]/)) { $inComment = 0; print B $a; next; }
  if ($a =~ /^Include \(-/i) { $inI6 = 1; print B $a; next; }
  if ($a =~ /^\[line break/) { print B $a; next; }

  $b = $a;

  if ((!$inI6) && (!$inComment))
  {
  if (($b =~ /  /) && !ignore($b))
  {
  $b =~ s/  +/ /g;
  if ($makeDifFile)
  {
  $a =~ s/  /\*\*\*\*\*\*  /;
  print C "$. before:$a" . "$. after:$b";
  $foundDif = 1;
  }
  }
  }
  print B $b;
}

close(A);
close(B);

if (!$foundDif)
{
  print "No difference found in story.ni.\n";
  return;
}

if ($difference)
{
  `wm \"$in\" \"$out\"`;
}

if ($makeDifFile)
{
  close(C);
  `$dif`;
}

if ($copy)
{
  print "Copying $in to $out\n";
  `xcopy /y \"$in\" \"$out\"`;
}

##############################
#subroutines

sub ignore
{
  for my $regex (keys %{$ignoreHash{$myProj}})
  {
    if ($_[0] =~ /$regex/) { return 1; }
  }
  return 0;
}

sub initGuess
{
  my $dir = getcwd();
  if ($dir =~ /\.inform[\\\/]Source/)
  {
    $dir =~ s/\.inform[\\\/]Source//;
	$dir =~ s/.*[\\\/]//;
	return $dir;
  }
}

sub usage
{
print<<EOT;
EOT
exit();
}