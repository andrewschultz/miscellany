######################################
#
#crv.pl
#formerly "check release version"
#
#now a way to do basic code checks so we aren't missing anything obvious
#

use strict;
use warnings;

use lib "c:\\writing\\scripts";
use i7;

use POSIX qw (getcwd);

##################options
my $testStubs = 1;

##################variables
my @commentNeed   = ();
my $needComment   = 0;
my $fillIn        = 0;
my @fillLines     = ();
my $NFRB          = 0;
my $betaBomb      = 0;
my $foundComments = 0;
my $inBeta        = 0;
my $inTest        = 0;
my $testSuccess   = 0;
my $lastChap;
my $newHeader;
my $linesToFix;
my $foundBeta  = 0;
my $foundStubs = 0;
my $foundTest  = 0;
my $lastHead   = 0;

print "Starting code testing.\n";

my $sourceFile = "./story.ni";

#1st argument can be either one of the abbrevs above or something longer
if ( defined( $ARGV[0] ) ) {
  $sourceFile = sourceFile( $ARGV[0] );
}

open( A, "$sourceFile" )
  || die(
"Can't open $sourceFile. Find a directory with story.ni in it or use a shortcut."
  );
open( C, ">crv.txt" );

my $shortDir = $sourceFile;
$shortDir =~ s/\.inform.*//gi;
$shortDir =~ s/.*[\/\\]//g;
$shortDir = lc($shortDir);

while ( $a = <A> ) {
  chomp($a);

  if ( $a =~ /\[fill-in-here\]/ ) {
    next if ( $a =~ /^\[.*\]$/ );
    print "FILLIN FOUND $.: $a\n";
    push( @fillLines, $. );
    $fillIn++;
    next;
  }

  if ( $a =~ /^volume/i ) {
    checkForComments();
    $newHeader = "";
    my $newVol = lc($a);
    $newVol =~ s/^volume *//g;
    $inBeta        = 0;
    $inTest        = 0;
    $foundComments = 0;

    if ( $newVol =~ /^stubs/ ) {
      $foundStubs = 1;
      if ($testStubs) {
        $inTest = 1;
      }
    }

    if ( $newVol =~ /^beta testing/ ) {
      if ( $newVol !~ /- not for release/ ) {
        print "WARNING! Mark $a as Not For Release.\n";
        $betaBomb = 1;
      }
      else { print "Yay, $a is NFR.\n"; $NFRB = 1; }
      print "========$a\n";
      $foundBeta = 1;
      $inBeta    = 1;
      print C "========BEGIN BETA\n";
    }
    if ( $newVol =~ /^(programmer )?testing/ ) {
      if ( $newVol !~ /- not for release/ ) {
        print "WARNING! Mark $a as Not For Release.\n";
      }
      else { print "Yay, $a is NFR.\n"; $NFRB = 1; }
      print "========$a\n";
      $inTest    = 1;
      $foundTest = 1;
      print C "========BEGIN TESTING\n";
    }
  }

  #if ($a =~ /\[ *\*/) { print "$inBeta/$inTest/$a\n"; }
  if ( ($inBeta) || ($inTest) ) {
    if ( $a =~ /^(book|part|chapter|section)/ ) {
      if ($newHeader) {
        if ( !$foundComments ) {
          if ( $. - $lastHead > 2 ) {
            checkForComments();
          }
          $newHeader = $a;
        }
      }
      $foundComments = 0;
      $lastHead      = $.;
      if ( $a =~ /not for release/ ) {
        print "********$a should not be NFR with a really good reason.\n";
      }
      $newHeader = $a;
      $lastChap  = $.;
    }

    #print "$a----\n";
    if ( $a =~ /^\[ *\*/ ) {
      $testSuccess++;
      my $debugString = "$newHeader: $a";
      print C "$debugString\n";
      if ($foundComments) {
        print
          "========DUPLICATE BELOW\n$debugString\n========DUPLICATE ABOVE\n";
      }
      $foundComments = 1;
    }
  }
}

checkForComments();

close(C);

if ( !$foundBeta )  { print "Need beta testing volume.\n"; }
if ( !$foundTest )  { print "Need regular testing volume.\n"; }
if ( !$foundStubs ) { print "Need stubs volume.\n"; }

if ( $foundBeta && $foundTest ) { print "Have both beta and regular tests.\n"; }

if   ( $#commentNeed == -1 ) { $linesToFix = "No lines"; }
else                         { $linesToFix = join( " / ", @commentNeed ); }

print "TEST RESULTS:$shortDir Fill-In-Here,0,$fillIn,"
  . join( "/", @fillLines ) . "\n";
print "TEST RESULTS:$shortDir Code Comments with crv.pl,1,$needComment,"
  . ( $testSuccess + $needComment )
  . ",$linesToFix\n";
if ( !$needComment ) { print "Yay! Success!\n"; }

if ($betaBomb) { print "COMMENT BETA TESTING OUT BEFORE RELEASE\n" x 5; }
if ( !$NFRB )  { print "FORGOT A BETA TEST SECTION\n" x 3; }

################################################
#subdirectories
#

sub checkForComments {
  if ( ($newHeader) && ( !$foundComments ) ) {
    my $fullStr = "NEEDS COMMENTS ($lastChap) : $newHeader\n";
    push( @commentNeed, $lastChap );
    print C "$fullStr";
    print "$fullStr";
    $needComment++;
  }
}
