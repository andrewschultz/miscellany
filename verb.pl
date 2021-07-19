####################################
#verb.pl
#
#lets you write code for a verb
#

use strict;
use warnings;

use Win32::Clipboard;

my $clip = Win32::Clipboard::new();
my @verbs;

my $chapSec = "chapter";

if ( !defined( $ARGV[0] ) ) { usage(); }
if ( $ARGV[0] =~ /\?/ )     { usage(); }
if ( $ARGV[0] =~ /^s-/) {
  $ARGV[0] =~ s/^..//;
  $chapSec = "section";
}
elsif ( $ARGV[0] =~ /^p-/) {
  $ARGV[0] =~ s/^..//;
  $chapSec = "part";
}

elsif ( $ARGV[0] =~ /^b-/) {
  $ARGV[0] =~ s/^..//;
  $chapSec = "book";
}

if ( $ARGV[0] =~ /,/ ) { @verbs = split( /,/, lc( $ARGV[0] ) ); }
else {
  @verbs = map { lc($_) } @ARGV;
}

my $v;
my $code = "";
my $oow;

for $v (@verbs) {

  if ( $v =~ / / ) {
    print "In *$v* spaces should be hyphens. It's easier that way. No need for quotes.\n";
    $v =~ s/ /-/;
  }
  my $applyTo = "";
  my $inBrax  = "";
  my $vo      = $v;
  $v =~ s/^[a-zA-Z0-9#]{1,2}-//gi;
  $v =~ s/\./ /g;

  if ( $vo =~ /\brf-/ ) {
    print("Adding fail rule $v.\n");
    $code =
      sprintf( "%sthis is the %s rule:\n\tthe rule fails.\n\n", $code, $v );
    next;
  }
  elsif ( $vo =~ /\brs-/ ) {
    print("Adding success rule $v.\n");
    $code =
      sprintf( "%sthis is the %s rule:\n\tthe rule succeeds.\n\n", $code, $v );
    next;
  }
  elsif ( $vo =~ /\brn-/ ) {
    print("Adding no-result $v.\n");
    $code =
      sprintf( "%sthis is the %s rule:\n\tmake no decision.\n\n", $code, $v );
    next;
  }

  ( my $vn = $v ) =~ s/-/ /;
  $v =~ s/-//;

  if ( $vo =~ /\bw-/ ) { $applyTo = "out of world"; }
  elsif ( $vo =~ /\ba-/ ) {
    print "Defining instead rule for $v.\n";
    $code = sprintf(
"%sinstead of doing something with $v:\n\tif action is procedural:\n\t\tcontinue the action;\n\tsay \"[fill-in-here\]\";\n\n",
      $code );
  }
  elsif ( $vo =~ /\bd-/ ) {
    $applyTo = "applying to one direction";
    $inBrax  = "[any thing]";
  }
  elsif ( $vo =~ /\bo-/ ) {
    $applyTo = "applying to one thing";
    $inBrax  = " [thing]";
  }
  elsif ( $vo =~ /\bov-/ ) {
    $applyTo = "applying to one visible thing";
    $inBrax  = " [any thing]";
  }
  elsif ( $vo =~ /\bp-/ ) {
    $applyTo = "applying to one person";
    $inBrax  = " [person]";
  }
  elsif ( $vo =~ /\b[n#]-/ ) {
    $applyTo = "applying to one number";
    $inBrax  = " [number]";
  }
  else { $applyTo = "applying to nothing"; }

  print "Defining action $applyTo: ${v}ing.\n";

  $oow = "applying to nothing";
  if ( $vo =~ /w-/ ) { $oow = "out of world"; }

  #print "$b from $v\n"; next;

  if ($applyTo) {
    $code = sprintf(
      "%s%s %sing\n\n%sing is an action %s.

understand the command \"%s\" as something new.

understand \"%s%s\" as %sing.

carry out %sing:
	the rule succeeds.

", $code, $chapSec, $v, $v, $applyTo, $vn, $vn, $inBrax, $v, $v
    );
  }
  elsif ( ( $vo =~ /^ts-/ ) || ( $vo =~ /^t-/ ) ) {
    $code =
      sprintf( "%s%s is a truth state that varies. %s is usually false.\n\n",
      $code, $v, $v );
  }
  elsif ( $vo =~ /^rm-/ ) {
    print "Defining blocked room $v.\n";
    $code = sprintf(
"%s%s %s\n\n%s is a room. \"DESCRIPTION PLEASE\".\n\ncheck going in %s:\n\tcontinue the action;\n\n",
      $code, $chapSec, $v, $v, $v );
  }
  elsif ( $vo =~ /^r-/ ) {
    print "Defining room $v.\n";
    $code = sprintf(
"%s%s %s\n\n%s is a room. %s is DIR of ??.\n\n %s is in region ??.\n\n",
      $code, $chapSec, $v, $v, $v, $v );
  }
  else {
    print("Couldn't find anything to do.\n");
  }

}

$clip->Set($code);

##########################################
#subroutines

sub usage {
  print
"The main thing to remember here is that dashes convert to spaces, e.g. full-feast -> \"full feast\" command and fullfeasting.\n";
  print "-rf/-rn/-rs = fail/no/succeed rules\n";
  print "-a = instead rule\n";
  print "-r = room, -rm = blocked room ('instead of going to X')\n";
  print "-a = instead rule\n";
  print "-ts/-t = truth state\n";
  print "o ov p # w = one, one visible, person, number, out of world\n";
  exit();
}
