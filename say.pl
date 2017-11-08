############################################
#say.pl: see about "say" in an inform 7 file
#with specifics for the Stale Tales Slate
#maybe a template later
#

# todo: sort by what appears when
# recursion

use lib "c:/writing/scripts";
use i7;
use strict;
use warnings;

my @sources;

my %init, my %said, my %prefix, my %unused, my %fiLoc;
my %includeHash;
my %needCheckHash;
my $fileCount = 1;    # 1 = main story.ni

my $extDir = "c:/program files (x86)/Inform 7/Inform7/Extensions";

if ( $#ARGV == -1 ) {
  if ( !-f "story.ni" ) {
    print "story.ni not found. Printing usage.\n";
    usage();
    exit;
  }
  print "Using story.ni in current directory.\n";
  @sources = ("story.ni");
}
else {
  for (@ARGV) {
    my $temp = sourceFile($_);
    die("No $temp") if ( !-f $temp );
    push( @sources, $temp );
  }
}

for my $story (@sources) {
  $fileCount             = 1;
  %includeHash           = ();
  %needCheckHash         = ();
  $includeHash{$story}   = 1;
  $needCheckHash{$story} = 1;

  # searchOne( "story.ni", 1 );

  my $i;

  my $iterations = 0;

  while ( ( scalar keys %needCheckHash > 0 ) && ( $iterations < 1 ) ) {
    $iterations++;

# print "Iteration $iterations\n";
# print(join("\n", sort { $needCheckHash{$a} <=> $needCheckHash{$b} } keys %needCheckHash) . "\n");
    for $i ( sort { $needCheckHash{$a} <=> $needCheckHash{$b} }
      keys %needCheckHash )
    {
      searchOne( $i, 1 );
    }
  }

  printResults();
}

# functions below

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

  $needCheckHash{ $_[0] } = 0;

  # print("Removing $_[0] from newCheckHash.\n");

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
      if ( $includeHash{$newFile} ) {
        warn("Duplicate include of $newFile\n");
      }
      else {
        $fileCount++;
        $includeHash{$newFile} = $fileCount;

        # print("Adding $newFile to newCheckHash.\n");
        $needCheckHash{$newFile} = $fileCount;
      }
    }
    if ( $a =~ /^to say/ ) {
      my $b = $a;
      chomp($b);
      $b =~ s/^to say //g;
      $b =~ s/ of.*//g;
      $b =~ s/:.*//g;
      $b =~ s/, say.*//g;
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
