####################################
#wrong.pl
#
#looks for WRONG in test sscripts which I need to change;

use strict;
use warnings;
use POSIX;

my $test = 1;

my $wrongDefault = 0;
my $default = "buck-the-past";

my @myDirs = ();

if (-f "story.ni") { @myDirs = (getcwd()); }
else { @myDirs = ("c:/games/inform/$default/source"); }

my $count = 0;
while ($count <= $#ARGV)
{
  my $arg = $ARGV[$count];
  for ($arg)
  {
  /-t/ && do { $test = 1; $count++; next; };
  /-(nt|tn)/ && do { $test = 0; $count++; next; };
  usage();
  }
}

for (@myDirs) { readOneDir($_); }

###############################################
#subroutines
#

sub readOneDir
{
  opendir(DIR, "$_[0]");
  my @dir = readdir DIR;
  my %fileHash;

  my $short= $_[0];
  $short =~ s/\.inform.*//;
  $short =~ s/.*[\\\/]//;

  close(DIR);

  my $wrongDefault = 0;
  for (@dir)
  {
    if ($_ =~ /reg-.*\.txt$/)
    {
      open(A, "$_[0]/$_");
      while ($a = <A>)
      {
        if ($a =~ /^WRONG$/)
		{
		  $wrongDefault++;
		  $fileHash{$_}++;
		  if (!$lineErr{$_})
		  {
		    $lineErr{$_} = $.;
		  }
		}
      }
    }
  }
  my $results = join($test ? "<br />" : "\n", map { "$_ $fileHash{$_}" } sort { $a cmp $b } keys %fileHash);
  if ($test)
  {
    print "TEST RESULTS: $short-wrongs,$wrongDefault,0,0,$results\n";
  }
  else
  {
    if (scalar keys %fileHash)
    {
      print $results;
    }
    else
    {
      print "No WRONG appears in reg-*.txt\n";
    }
  }
}