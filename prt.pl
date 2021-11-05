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
use File::stat;
use mytools;

my %fileCopy;

findProj();

print("NOTE: THIS HAS BEEN SUPERSEDED BY prt.py!")

my $ignore_timestamps = 1;
my $ignoreBinary = 0;
my $prt          = "c:\\games\\inform\\prt";
my $projToRead   = "";
my $projName     = getcwd();
my $defaultProj  = "vv";

if ( $projName =~ /\.inform/ ) {
  $projName =~ s/\.inform.*//g;
  $projName =~ s/.*[\\\/]//g;
}
else {
  $projName = "";
}

my $arg_count = 0;
while ($arg_count <= $#ARGV)
{
  my $arg = $ARGV[$arg_count];
  print "$arg\n";
  if ($arg =~ /\?/) { print("ib = ignore binary, it = ignore timestamps."); exit(); }
  if ( $arg =~ /^(-)?ib/ ) { $arg =~ s/^-//g; $ignoreBinary = 1; $arg_count++; next;}
  if ( $arg =~ /^(-)?it/ ) {$ignore_timestamps = 1; $arg_count++; next;}
  if ( $arg =~ /^(-)?ni/ ) {$ignore_timestamps = 0; $arg_count++; next;}
  die ("Redefined proj-to-read.") if $projToRead;
  if (defined($i7x{$arg})) {
    $projToRead = $i7x{$arg};
	} elsif ( defined($i7x{$projName}) ) { $projToRead = $projName; }
	else { die("Couldn't find any project for $arg.\n") }
  $arg_count++;
}

$projToRead = $projName if $projName && !$projToRead;

if ( !$projToRead && $defaultProj ) {
  $projToRead = i7::to_proj($defaultProj);
  print "Going with default project $defaultProj/$projToRead.\n";
}

die("Couldn't locate or determine a project. Find a story.ni source directory or specify a project shortcut.") if !$projToRead;

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
	  my $bg = basename $g2;
      my $g3 = "$prt\\$bg";
      if ( !-f $g3 ) {
        copy( $g2, $g3 );
        print "Copying new file $g2 to $g3\n";
        $news++;
      }
	  $g2 = mytools::follow_symlink($g2);
	  $g3 = mytools::follow_symlink($g3);
      if ( compare( $g2, $g3 ) ) {
	    if ( stat($g2)->mtime < stat($g3)->mtime ) {
		if ($ignore_timestamps) {
		  print("Ignoring that the PRT directory timestamp for $g2 is after the source directory.\n");
		}
		else {
		print "SKIPPING--$bg timestamp is after the main file $g2. This may cause overwrites. -it ignores this.\n";
		next;
		}
		}
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
