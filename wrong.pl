####################################
#wrong.pl
#
#looks for WRONG in test sscripts which I need to change;

use strict;
use warnings;
use POSIX;

###################options
my $test = 1;
my $testAll = 0;
my $testMajor = 0;

my $default = "buck-the-past";

my @myDirs = ();
my @majorDirs = ("shuffling", "roiling", "threediopolis", "fourdiopolis", "compound", "slicker-city", "buck-the-past");

my %lineErr;

if (-f "story.ni") { @myDirs = (getcwd()); }
else { @myDirs = ("c:/games/inform/$default.inform/source"); }

my $count = 0;
while ($count <= $#ARGV)
{
  my $arg = $ARGV[$count];
  for ($arg)
  {
  /^-a$/ && do { $testMajor = 1; $count++; next; };
  /^-aa$/ && do { $testAll = 1; $count++; next; };
  /^-t$/ && do { $test = 1; $count++; next; };
  /-(nt|tn)/ && do { $test = 0; $count++; next; };
  usage();
  }
}

if ($testAll && $testMajor) { die ("Conflicting options added."); }

if ($testAll)
{
}
elsif ($testMajor)
{
  for (@majorDirs)
  {
    readOneDir("c:/games/inform/$_.inform/source", 1);
  }
}
else
{
  for (@myDirs) { readOneDir($_, 0); }
}

###############################################
#subroutines
#

#############readOneDir
#1st arg = directory, 2nd = should we warn if nothing found

sub readOneDir
{
  opendir(DIR, "$_[0]");
  my @dir = readdir DIR;
  my %fileHash;

  my $short= $_[0];
  $short =~ s/\.inform.*//;
  $short =~ s/.*[\\\/]//;

  close(DIR);

  my $thisErr;
  my $success = 0;
  my $wrongDefault = 0;
  my $anyFile = 0;

  for (@dir)
  {
    if ($_ =~ /reg-.*\.txt$/)
    {
	  $thisErr = 0;
	  $anyFile = 1;
      open(A, "$_[0]/$_");
      while ($a = <A>)
      {
        if ($a =~ /^WRONG$/)
		{
		  $wrongDefault++;
		  $fileHash{$_}++;
		  $thisErr = 1;
		  if (!defined($lineErr{$_}))
		  {
		    $lineErr{$_} = $.;
		  }
		}
      }
	  close(A);
	  if (!$thisErr) { $success++; }
    }
  }
  my $results = join($test ? "<br />" : "\n", map { "$_ $fileHash{$_}($lineErr{$_})" } sort { $a cmp $b } keys %fileHash);
  if ($test)
  {
    print "TEST RESULTS: $short-wrongs,$wrongDefault,0,$success,$results\n";
  }
  else
  {
    if (scalar keys %fileHash)
    {
      print $results;
    }
    else
    {
      if ($_[1]) { print "No WRONG appears in reg-*.txt for $_[0]\n"; }
    }
  }
}