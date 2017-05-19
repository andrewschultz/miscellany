############################################
#qq.pl
#
#quick question (double question) finding script for source files
#
#TODO: look for header files as well
#
#TODO: also allow for TODO with separate test

use POSIX;
use strict;
use warnings;

my @fileArray = ();
my $mainFile;
my $shortName;

if ($ARGV[0])
{
  $mainFile = "c:/games/inform/$ARGV[0].inform/Source/story.ni";
  $shortName = lc($ARGV[0]);
}
elsif (-f "story.ni")
{
  $mainFile = "story.ni";
  $shortName = getcwd();
  $shortName =~ s/\.inform.*//g;
  $shortName =~ s/.*[\\\/]//g;
}

push(@fileArray, $mainFile);

for (@fileArray)
{
  scanForQs($_);
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

if (! -f $_[0]) { die ("No file $_[0]."); }

open(A, "$_[0]");

while ($line = <A>)
{
  if (($line =~ /\[/) && ($line !~ /\]/)) { $comment = 1; }
  if ($line =~ /\[todo/i)
  {
    $count++;
	$line =~ s/.*todo//;
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

my $errs = $#badLines + 1;
print "TEST RESULTS:$shortName double-question/todo,2,$errs,0," . join(" / ", @badLines) . "\n";
if ($deletables)
{
print "TEST RESULTS:$shortName deletable debug text,0,$deletables,0," . join(" / ", @dele) . "\n";
}
close(A);

}