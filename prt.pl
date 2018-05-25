##########################################
#prt.pl : python regression test copy over
#

use POSIX;
use lib "c:/writing/scripts";
use strict;
use warnings;
use i7;
use i7proj;

my %fileCopy;

findProj();

my $ignoreBinary = 0;
my $prt          = "c:\\games\\inform\\prt";
my $projToRead   = "";
my $projName     = getcwd();

$projName =~ s/\.inform.*//g;
$projName =~ s/.*[\\\/]//g;

if ( $#ARGV >= 0 ) {
  my $arg = $ARGV[0];
  if ( $arg =~ /^-/ ) { $arg =~ s/^-//g; $ignoreBinary = 1; }
  $projToRead = $i7x{$arg};
  if ( !$projToRead ) { die("Couldn't find any project for $arg.\n"); }
}
elsif ( $i7x{$projName} ) { $projToRead = $projName; }
elsif ($projName)         { $projToRead = $projName; }

open( A, "c:/writing/scripts/prt.txt" );

while ( $a = <A> ) {
  if ( $a =~ /:/ ) {
    chomp($a);
    my @b = split( /:/, $a );
    $fileCopy{ $b[0] } = $b[1];
  }
}
close(A);

if ($projToRead) {
  my $infBase = "c:\\games\\inform\\$projToRead.inform";
  print "Copying over regression test suite\n";
  my $q = "";
  my @g = glob("$infBase\\Source\\reg-*.txt");
  if ( scalar @g ) {
    print "REG files first.\n";
    $q .= `copy $infBase\\Source\\reg-*.txt c:\\games\\inform\\prt`;
  }
  else {
    print "No REG files.\n";
  }
  @g = glob("$infBase\\Source\\rmo-*.txt");
  if ( scalar @g ) {
    print "Now RMO files.\n";
    $q .= `copy $infBase\\Source\\rmo-*.txt c:\\games\\inform\\prt`;
  }
  else {
    print("No RMO files.\n");
  }
  print $q;
  if ( !$ignoreBinary ) {
    print "Looking for build file in $infBase\\Build.\n";
    if ( -f "$infBase\\Build\\output.ulx" ) {
      print
        "Found ULX binary to copy over: output.ulx to debug-$projToRead.ulx.\n";
      $q = `copy $infBase\\Build\\output.ulx $prt\\debug-$projToRead.ulx`;
      print $q;
    }
    elsif ( -f "$infBase\\Build\\output.z8" ) {
      print
        "Found Z8 binary to copy over: output.z8 to debug-$projToRead.z8.\n";
      $q = `copy $infBase\\Build\\output.z8 $prt\\debug-$projToRead.z8`;
      print $q;
    }
    elsif ( -f "$infBase\\Build\\output.z5" ) {
      print
        "Found Z5 binary to copy over: output.z5 to debug-$projToRead.z5.\n";
      $q = `copy $infBase\\Build\\output.z5 $prt\\debug-$projToRead.z5`;
      print $q;
    }
    else { print "Couldn't find any output binaries.\n"; }
  }
  else { print "Ignoring output binary.\n"; }
  if ( $fileCopy{$projToRead} ) {
    my @c = split( /,/, $fileCopy{$projToRead} );
    print "Copying over additional specified files.\n";
    for (@c) {
      print "$_...\n";
      `copy $infBase\\Source\\$_ $prt`;
    }
  }
}
else { print "No project found.\n"; }
