##########################################
#prt.pl : python regression test copy over
#


use POSIX;
use lib "c:/writing/scripts";
use strict;
use warnings;
use i7proj;

findProj();

my $projToRead;
my $projName = getcwd();

$projName =~ s/\.inform.*//g;
$projName =~ s/.*[\\\/]//g;

if (($#ARGV >= 0) && ($proj{$ARGV[0]}))
{
  $projToRead = $proj{$ARGV[0]};
}
elsif ($gotProj{$projName}) { $projToRead = $projName; }

if ($projToRead)
{
  print "Copying over regression test suite\n";
  my $q = `copy c:\\games\\inform\\$projToRead.inform\\Source\\reg-*.txt c:\\games\\inform\\prt`;
  print $q;
  print "Copying over debug files\n";
  $q = `copy c:\\games\\inform\\$projToRead.inform\\Build\\output.ulx c:\\games\\inform\\prt\\debug-$projToRead.ulx`;
  print $q;
}
else { print "No project found.\n"; }