############################################
#say.pl: see about "say" in an inform 7 file
#with specifics for the Stale Tales Slate
#maybe a template later
#

use strict;
use warnings;

my %init, my %said, my %prefix, my %unused, my %fiLoc;
my %includeHash;

my $extDir = "c:/program files (x86)/Inform 7/Inform7/Extensions";

my @defAry = (
  "shuffling",     "roiling",       "compound", "slicker-city",
  "buck-the-past", "threediopolis", "ugly-oafs"
);

if ( $#ARGV == -1 ) {
  if ( !-f "story.ni" ) {
    print "story.ni not found. Printing usage.\n";
    usage();
    exit;
  }
  print "Searching for story.ni in current directory.\n";
  searchOne( "story.ni", 1 );

  my $i;

  for $i ( keys %includeHash ) {
    searchOne( $i, 1 );
  }

  printResults();
}

while ( $#ARGV > -1 ) {
  if ( $ARGV[0] =~ /,/ ) {
    my @ary = split( /,/, $ARGV[0] );
    for my $dir (@ary) { searchSay($dir); }
  }
  elsif ( $ARGV[0] eq "-a" ) {
    for my $dir (@defAry) { searchSay($dir); }
  }
  elsif ( $ARGV[0] eq "?" ) {
    usage();
  }
  else {
    searchSay( $ARGV[0] );
  }
  shift(@ARGV);
}

#############################################
#searchSay
#determines files to look through
#

sub searchSay {
  %init   = ();
  %said   = ();
  %prefix = ();
  %unused = ();
  print "Trying $_[0]\n";
  if ( ( $_[0] eq "roiling" ) || ( $_[0] eq "sa" ) ) {
    searchOne( "c:/games/inform/$_[0].inform/Source/story.ni", 1 );
    searchOne(
"c:/Program Files (x86)/Inform 7/Inform7/Extensions/Andrew Schultz/$_[0] Random Text.i7x",
      2
    );
    searchOne(
"c:/Program Files (x86)/Inform 7/Inform7/Extensions/Andrew Schultz/$_[0] Nudges.i7x",
      3
    );
  }
  else { searchOne( "c:/games/inform/$_[0].inform/Source/story.ni", "" ); }
  printResults();
}

###############################################
#searchOne
#just searches through one file
#

sub searchOne {
  open( A, "$_[0]" ) || do { print "Can't find $_[0].\n"; return; };

  print "Going through $_[0]...\n";

  my $prefix = "";
  my $dup    = 0;

  if ( $#_ >= 1 ) { $prefix = "$_[1]-"; }

  # print "SearchOne args: $#_ prefix = $prefix\n";

  ( my $shortfile = $_[0] ) =~ s/.*[\\\/]//g;

  while ( my $a = <A> ) {
    if ( $a =~ /^include.* by / ) {
      my $newFile = lc($a);
      chomp($newFile);
      $newFile =~ s/^include *//;
      $newFile =~ s/\..*//;
      $newFile =~ s/(.*) +by *(.*)/$2\/$1.i7x/;
      $newFile = "$extDir/$newFile";
      die("Can't find $newFile included file") if ( !-f $newFile );
      warn("Duplicate include of $newFile\n")  if $includeHash{$newFile};
      $includeHash{$newFile} = 1;
    }
    if ( $a =~ /^to say/ ) {
      my $b = $a;
      chomp($b);
      $b =~ s/^to say //g;
      $b =~ s/ of.*//g;
      $b =~ s/:.*//g;
      if ( $a =~ /\[unused[^\]]*\]/ ) { $unused{$b} = 1; }
      if ( $init{$b} ) {
        $dup++;
        print "$dup: Duplicate to-say for $b, $prefix$. to $init{$b}.\n";
      }
      $init{$b}   = "$.";
      $fiLoc{$b}  = "$shortfile";
      $prefix{$b} = "$prefix";
    }
  }

  # print "Finished $. lines in $_[0].\n";

  close(A);

  open( A, "$_[0]" );

  while ( $a = <A> ) {
    chomp($a);
    if ( $a !~ /\[/ ) { next; }
    $a =~ s/^[^\[]*//g;
    my @x = split( /\[/, $a );
    for (@x) {
      $_ =~ s/\].*//g;
      $_ =~ s/ of.*//g;
      $said{$_} = 1;
    }
  }

  close(A);

}

####################################
#sub printResults
#
#print the results
#

sub printResults {

  my $count = 0;
  my $uns   = 0;

  foreach my $q ( sort { $init{$a} <=> $init{$b} } keys %init )
  {    # add prefix{$q} whenever...
    if ( !$said{$q} ) {
      if ( $unused{$q} ) {
        print
"$q ($init{$q} $fiLoc{$q}) marked as unused but potentially useful.\n";
      }
      else {
        $uns++;
        print "$q ($init{$q} $fiLoc{$q}) is not accessed (#$uns).\n";
      }
    }
    if ( $said{$q} && $unused{$q} ) {
      print "$q ($init{$q}) marked as unused but actually used.\n";
    }
  }

  foreach my $q ( sort keys %said ) {

    #if (!$init{$q}) { print "$q is bracketed.\n"; }
  }

}

sub usage {
  print <<EOT;
==================USAGE==================
No argument given: say.pl tries story.ni in current directory
sa=shuffling
roiling=roiling
-a=all my recent games, shuffling, oafs, threediopolis, compound
EOT
}
