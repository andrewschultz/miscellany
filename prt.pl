##########################################
#prt.pl : python regression test copy over
#

use POSIX;
use lib "c:/writing/scripts";
use strict;
use warnings;
use i7;
use i7proj;
use File::Basename;
use File::Compare;
use File::Copy;

my %fileCopy;

findProj();

my $ignoreBinary = 0;
my $prt          = "c:\\games\\inform\\prt";
my $projToRead   = "";
my $projName     = getcwd();
my $defaultProj  = "ai";

if ( $projName =~ /\.inform/ ) {
  $projName =~ s/\.inform.*//g;
  $projName =~ s/.*[\\\/]//g;
}
else {
  $projName = "";
}

if ( $#ARGV >= 0 ) {
  my $arg = $ARGV[0];
  if ( $arg =~ /^-/ ) { $arg =~ s/^-//g; $ignoreBinary = 1; }
  $projToRead = $i7x{$arg};
  if ( !$projToRead && ( !$defaultProj ) ) {
    die("Couldn't find any project for $arg.\n");
  }
}
elsif ( $i7x{$projName} ) { $projToRead = $projName; }
elsif ($projName)         { $projToRead = $projName; }

if ( !$projToRead && $defaultProj ) {
  $projToRead = i7::to_proj($defaultProj);
  print "Going with default project $defaultProj/$projToRead.\n";
}

open( A, "c:/writing/scripts/prt.txt" );

while ( $a = <A> ) {
  if ( $a =~ /:/ ) {
    chomp($a);
    my @b = split( /:/, $a );
    $fileCopy{ $b[0] } = $b[1];
  }
}
close(A);

my $infBase = "c:\\games\\inform\\$projToRead.inform";

if ($projToRead) {
  my $news = 0;
  my $difs = 0;

  print "Copying over regression test suite\n";
  my $q = "";
  glob_over("reg");
  glob_over("rmo");
  if ( !$ignoreBinary ) {
    print "Looking for build file in $infBase\\Build.\n";
    my $temp = checkMyExt( "$infBase\\Build", $prt, "debug-$projToRead" );
    if ( $temp == 0 ) { print "Couldn't find any output binaries.\n"; }
    elsif ( $temp < 0 ) {
      print "Couldn't find any binaries that needed copying.\n";
    }
  }
  else { print "Ignoring any possible output binaries.\n"; }
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

##########################################################

# from dir, to dir, file main name
sub checkMyExt {
  my @ext_ary = ( "ulx", "z8", "z5" );
  my $skipped = 0;
  my $copied  = 0;
  for my $x (@ext_ary) {
    my $f1 = "$_[0]\\output.$x";
    my $f2 = "$_[1]\\$_[2].$x";
    if ( -f "$infBase\\Build\\output.$x" ) {
      if ( -f $f1 && ( !compare( $f1, $f2 ) ) ) {
        print "$f1 identical to $f2. Not copying over.\n";
        $skipped++;
      }
      else {
        my $xu = uc($x);
        print "Found $xu binary to copy over: $f1 to $f2.\n";
        my $q = `copy $infBase\\Build\\output.$x $prt\\debug-$projToRead.$x`;
        print $q;
        $copied++;
      }
    }
  }
  return $copied   if $copied > 0;
  return -$skipped if $skipped > 0;
  return 0;
}

sub glob_over {
  my $news = 0;
  my $difs = 0;
  my @g    = glob("$infBase\\Source\\$_[0]-*.txt");
  if ( scalar @g ) {
    print "REG files first.\n";
    for my $g2 (@g) {
      my $g3 = "$prt\\" . ( basename $g2);
      if ( !-f $g3 ) {
        copy( $g2, $g3 );
        print "Copying new file $g2 to $g3\n";
        $news++;
      }
      if ( compare( $g2, $g3 ) ) {
        copy( $g2, $g3 );
        print "Copying modified file $g2 to $g3\n";
        $difs++;
      }
    }
    print "$news new, $difs dif\n";
  }
  else {
    print "No $_[0] files.\n";
  }
}
