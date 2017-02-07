#####################################################################
#unco.pl
#
#uncomments sections of games.otl
#only deletes #'s and nothing else
#
#unco.pl btp  (y) <- only deletes if everything is commented out
#unco.pl btp 1 (y) <- deletes 1 layer of # to start
#unco.pl btp 2 (y) <- deletes all comments
#

use strict;
use warnings;

open(A, "c:\\writing\\games.otl");

my $gotOne = 0;
my $searchstring = "btp";
my $wildcard = 0;

if ($#ARGV < 1) { die ("Need a letter argument and a number: 1 to delete 1 # from the start of each line, 0 to delete only if they're all there, 2 to delete them all.\nGood ones include btp, sc, pc You can use + for all of them starting with btp etc.\n\nWe need a third argument to copy everything over."); }

$searchstring = $ARGV[0];

if ($searchstring =~ /\+/) { $wildcard = 1; $searchstring =~ s/\+//g; }
elsif ($searchstring =~ /^-/) { $wildcard = 0; $searchstring =~ s/^-//g; } # in case wildcard becomes default

open(B, ">c:\\writing\\temp\\games.otl");
while ($a = <A>)
{
  print B $a;
  if (($a =~ /^\\$searchstring[\|=]/) || ($wildcard && ($a =~ /^\\$searchstring.*=/)))
  { commentProcess(); $gotOne = 1; }
}

close(A);
close(B);

if ($gotOne == 0) { print "Didn't find anyone!\n"; die; }

if (defined($ARGV[2])) { print "Copying over.\n"; `copy /y \\writing\\games.otl \\writing\\temp\\games.otl`; }
else { print "Comparing.\n"; `wm \\writing\\games.otl \\writing\\temp\\games.otl`; }

sub commentProcess
{
  my @toComment = ();

  if ($ARGV[1] == 2)
  {
    while ($a = <A>) { $a =~ s/^#*//; print B $a; if ($a !~ /[a-z0-9]/i) { last; } }
  }
  elsif ($ARGV[1] == 1)
  {
    while ($a = <A>) { $a =~ s/^#//; print $a; print B $a; if ($a !~ /[a-z0-9]/i) { last; } }
  }
  elsif ($ARGV[1] == 0)
  {
    my $allComment = 1;
    while ($a = <A>)
    {
      push (@toComment, $a);
      if ($a !~ /[a-z0-9]/i) { last; }
      if ($a !~ /^#/) { $allComment = 0; print "Uncommented: $a"; }
    }
    for my $co (@toComment)
    {
      if ($allComment) { $co =~ s/^#//; }
      print B $co;
    }
  }

}