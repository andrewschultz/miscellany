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

if ( !defined( $ARGV[0] ) ) { usage(); }
if ( $ARGV[0] =~ /\?/ )     { usage(); }
if ( $ARGV[0] =~ /,/ ) { @verbs = split( /,/, lc( $ARGV[0] ) ); }
else {
  @verbs = map { lc($_) } @ARGV;
}

my $v;
my $code = "";
my $oow;

for $v (@verbs) {

  if ( $v =~ / / ) {
    print "In *$v* spaces should be hyphens. It's easier that way.\n";
    $v =~ s/ /-/;
  }
  my $applyTo = "";
  my $inBrax  = "";
  my $vo      = $v;
  $v =~ s/^[a-zA-Z0-9#]{1,2}-//gi;
  $v =~ s/\./ /g;

  if ( $vo =~ /^rf-/ ) {
    print("Adding fail rule $v.\n");
    $code =
      sprintf( "%sthis is the %s rule:\n\tthe rule fails.\n\n", $code, $v );
    next;
  }
  elsif ( $vo =~ /^rs-/ ) {
    print("Adding success rule $v.\n");
    $code =
      sprintf( "%sthis is the %s rule:\n\tthe rule succeeds.\n\n", $code, $v );
    next;
  }

  ( my $vn = $v ) =~ s/-/ /;
  $v =~ s/-//;

  if ( $vo =~ /w-/ ) { $applyTo = "out of world"; }
  elsif ( $vo =~ /a-/ ) {
    print "Defining instead rule for $v.\n";
    $code = sprintf(
"%sinstead of doing something with $v:\n\tif action is procedural:\n\t\tcontinue the action;\n\tsay \"[fill-in-here\]\";\n\n",
      $code );
  }
  elsif ( $vo =~ /^d-/ ) {
    $applyTo = "applying to one direction";
    $inBrax  = "[any thing]";
  }
  elsif ( $vo =~ /^o-/ ) {
    $applyTo = "applying to one thing";
    $inBrax  = " [thing]";
  }
  elsif ( $vo =~ /^ov-/ ) {
    $applyTo = "applying to one visible thing";
    $inBrax  = " [any thing]";
  }
  elsif ( $vo =~ /^p-/ ) {
    $applyTo = "applying to one person";
    $inBrax  = " [person]";
  }
  elsif ( $vo =~ /^#-/ ) {
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
      "%schapter %sing\n\n%sing is an action %s.

understand the command \"%s\" as something new.

understand \"%s%s\" as %sing.

carry out %sing:
	the rule succeeds.

", $code, $v, $v, $applyTo, $vn, $vn, $inBrax, $v, $v
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
"%schapter %s\n\n%s is a room. \"DESCRIPTION PLEASE\".\n\ncheck going in %s:\n\tcontinue the action;\n\n",
      $code, $v, $v, $v );
  }
  elsif ( $vo =~ /^r-/ ) {
    print "Defining room $v.\n";
    $code = sprintf(
"%schapter %s\n\n%s is a room. %s is DIR of ??.\n\n %s is in region ??.\n\n",
      $code, $v, $v, $v, $v );
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
  exit();
}
