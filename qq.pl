############################################
#qq.pl
#
#quick question (double question) finding script for source files
#

use POSIX;
use strict;
use warnings;

##############################options
my $test = 0;
my $gotYet = 0;

##############################variables
my @fileArray = ();
my $mainFile;
my $shortName;
my $count;

while ($count < $#ARGV)
{
  my $arg = $ARGV[$count];
  for ($arg)
  {
    /^-?t/i && do { $test = 1; $count++; next; };
    /^-?(nt|tn)/i && do { $test = 0; $count++; next; };
	if ($gotYet) { die ("Only one project at a time."); }
    $mainFile = "c:/games/inform/$arg.inform/Source/story.ni";
    $shortName = lc($arg);
	$count++;
	$gotYet = 1;
  }
}

if (!$mainFile && (-f "story.ni"))
{
  $mainFile = "story.ni";
  $shortName = getcwd();
  $shortName =~ s/\.inform.*//g;
  $shortName =~ s/.*[\\\/]//g;
}

if (! -f $mainFile) { die ("No file $mainFile."); }

scanForQs($mainFile, 1);

my $inc;

for $inc (@fileArray)
{
  scanForQs($inc, 0);
}

######################################
#subroutines
#

sub scanForQs
{

my $line;
my $count = 0;
my @badLines;
my $comment = 0;
my @dele;
my $deletables = 0;
my $sweepIncludes = $_[1];

if (! -f $_[0]) { die ("No file $_[0]."); }

open(A, "$_[0]");

while ($line = <A>)
{
  if ($sweepIncludes && ($line =~ /^include.*by Andrew Schultz/i))
  {
    my $temp = $line;
	chomp($temp);
	$temp =~ s/ by .*//;
	$temp =~ s/include +//;
	$temp = "c:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions\\Andrew Schultz\\$temp.i7x";
	push (@fileArray, $temp);
  }
  if (($line =~ /\[/) && ($line !~ /\]/)) { $comment = 1; }
  if ($line =~ /\[(todo|expound)/i)
  {
    $count++;
	$line =~ s/.*\[(todo|expound)//i;
	print "$.: $line\n";
	push(@badLines, $line);
  }
  if ($line =~ /\[[^\]]*\?\?/)
  {
    $count++;
	$line =~ s/\t/>/g;
	print "Line $line coding question #$count: $line\n";
	push (@badLines, $line);
  }
  elsif (($line =~ /\?\?/) && ($comment))
  {
    $count++;
	$line =~ s/\t/>/g;
	print "Line $line coding question #$count: $line\n";
	push (@badLines, $line);
  }
  if ($line =~ /\]\s*$/) { $comment = 0; }
  if (($line =~ /\]/) && ($line !~ /\[/)) { $comment = 0; }
  if ($line =~ /\tdl/)
  {
    $deletables++;
	print "Line $. deletable text #$deletables\n";
	push (@dele, $line);
  }
}

close(A);

my $errs = $#badLines + 1;
if ($test)
{
print "TEST RESULTS:$shortName double-question/todo/expound,2,$errs,0," . join(" / ", @badLines) . "\n";
if ($deletables)
{
print "TEST RESULTS:$shortName deletable debug text,0,$deletables,0," . join(" / ", @dele) . "\n";
}
}
close(A);

}