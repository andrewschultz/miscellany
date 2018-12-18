########################################
#
# 2dy.pl
#
# opens today's file or the one before that
#
# creates a new daily file if one hasn't been created for a week
#

use strict;
use warnings;

my $maxback = 7;

my $printInitSections = 0;    # -ps prints sections and dies

my $theMinus = 0;

if ( $ARGV[0] =~ /^-?ps/i ) {
  $printInitSections = 1;
}
elsif ( defined( $ARGV[0] ) ) {
  my $arg = lc( $ARGV[0] );
  $arg =~ s/^-//;
  if ( $ARGV[0] =~ /^[0-9]+$/ ) {
    $theMinus = $ARGV[0];
  }
  elsif ( $ARGV[0] =~ /l/ ) {
    my $filesBack = 1;
    my $backSoFar = 0;
    if ( $ARGV[0] =~ /[0-9]$/ ) {
      $filesBack = $ARGV[0];
      $filesBack =~ s/.*[^0-9]//gi;
      $maxback = 100;
    }
    for ( 0 .. $maxback - 1 ) {
      if ( -f "c:/writing/daily/" . daysAgo($_) ) {
        $backSoFar++;
        if ( $backSoFar == $filesBack ) {
          $theMinus = $_;
          print( "Going back $theMinus days to get to " . daysAgo($_) . ".\n" );
          last;
        }
      }
      if ( -f "c:/writing/daily/done/" . daysAgo($_) ) {
        die("Everything is done. Use -lf to write a new file.")
          if ( $ARGV[0] !~ /f/ );
        $theMinus = 0;
        print "All done, opening today-ish.\n";
      }
    }
    die("Can only go $filesBack files back.")
      if ( $backSoFar < $filesBack ) && ( $backSoFar > 1 );
  }
}

my (
  $second,     $minute,    $hour,
  $dayOfMonth, $month,     $yearOffset,
  $dayOfWeek,  $dayOfYear, $daylightSavings
) = localtime( time - 86400 * $theMinus );

my $fileName = sprintf(
  "c:/writing/daily/%d%02d%02d.txt",
  $yearOffset + 1900,
  $month + 1, $dayOfMonth
);

my $fileDoneName = sprintf(
  "c:/writing/daily/done/%d%02d%02d.txt",
  $yearOffset + 1900,
  $month + 1, $dayOfMonth
);

if ( -f $fileDoneName ) {
  print(
    "You already threw that file ($fileDoneName) in a Done folder. Exiting.");
  exit;
}

if ( ( !-f $fileName ) || ( -s $fileName == 0 ) || $printInitSections ) {
  open( A, "c:/writing/scripts/2dy.txt" );
  my @subjArray = ();
  while ( $a = <A> ) {
    next if $a =~ /^#/;
    chomp($a);
    ( my $modLine = $a ) =~ s/=[^,]*//g;
    @subjArray = split( /,/, $modLine );
    die( join( ", ", @subjArray ) ) if $printInitSections;
    ; # example of default = ( "qui", "spo", "aa", "btp", "sh", "sp", "nam" ) printed in order on separate lines from qui=quick,spo=spo,aa,btp,sh,sp,nam;
    last;
  }
  open( A, ">>$fileName" );
  for (@subjArray) { print A "\n\\$_\n"; }
  close($fileName);
  if ( open( A, "c://nothing.txt" ) ) { close(A); }

  #`touch $fileName`;
}
else { print "$fileName is there. Opening with Notepad++.\n"; }

`"$fileName"`;
exit;

#`"C:/Program Files/Windows NT/Accessories/wordpad.exe" "$fileName"`;

sub daysAgo {
  (
    $second,     $minute,    $hour,
    $dayOfMonth, $month,     $yearOffset,
    $dayOfWeek,  $dayOfYear, $daylightSavings
  ) = localtime( time - 86400 * $_[0] );
  return
    sprintf( "%d%02d%02d.txt", $yearOffset + 1900, $month + 1, $dayOfMonth );
}
