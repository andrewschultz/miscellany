#####################################
#b1.pl
#
#this takes a sequence of hangman letters with correctly guessed places
#along with incorrect guesses and then looks through a dictionary
#
#then prints out results, with the most likely letters left
#

# bug can't add word that isn't in the dictionary in first place (omeprazole)

use strict;
use warnings;
use List::MoreUtils qw(uniq);
use File::Stat;

use sigtrap 'handler', \&cleanup, 'normal-signals';

my $b1time = "c:/writing/dict/p1.txt";
my $misses = __FILE__;
$misses =~ s/pl$/txt/gi;
my @prevMiss = ();
my %miss;
my $wrongString;
my $endString = "";
my $missFound = 0;
my %freq;
my %f2;
my $stdin = 0;

my $del       = -1;
my $crossword = 0;

my $firstStuffString = "esirotlan";

for ( 0 .. $#ARGV ) {
  if ( $ARGV[$_] =~ /b1\.pl/i ) { $del = $_; }
}
if ( $del > -1 ) {
  print "Oops, it looks like you forgot to delete the command above.\n";
  @ARGV = @ARGV[ $del + 1 .. $#ARGV ];
}

if ( !defined( $ARGV[0] ) ) {
  die(
"Usage: found letters (.=blank), wrong letters. Use +(word) to add it to $misses. i = stdin.\n"
  );
}

my $argtrim = lc( $ARGV[0] );
$argtrim =~ s/^-//;

if ( ( lc( $ARGV[0] ) eq "-f" ) || ( lc( $ARGV[0] ) eq "f" ) ) {
  if ( !defined( $ARGV[1] ) ) { die("Need a word to force into the list."); }
  addToDict( $ARGV[1], 1 );
  exit();
}

if ( defined( $ARGV[2] ) ) {
  die("Only 2 arguments max: word and missed letters.\n");
}

if ( $argtrim =~ /^[\*#]/ ) { $argtrim =~ s/.//; $crossword = 1; }
if ( $argtrim eq "e" )      { `$misses`;         exit(); }
if ( $argtrim eq "c" ) {
  my $cmd = 'start "" "notepad++.exe" ' . (__FILE__);
  `$cmd`;
  exit();
}
if ( $argtrim eq "s" ) { showMisses(); exit(); }
if ( $argtrim eq "?" ) { usage();      exit(); }

my $justShow = 0;

if ( ( $argtrim =~ /^(-)?a[0-9]/i ) ) {
  my $delta = $argtrim;
  my @newfi;

  $delta =~ s/^(-)?a//i;

  open( A, $b1time );
  while ( $a = <A> ) {
    push( @newfi, $a );
  }
  $newfi[0] += $delta;
  $newfi[3] += $delta;
  $newfi[0] .= "\n";
  $newfi[3] .= "\n";
  close(A);
  open( A, ">$b1time" );
  print A $_ for (@newfi);
  close(A);
  print "Added $delta to start/end.\n";
}

if ( ( $argtrim =~ /^(-)?p[0-9]/i ) ) {
  my $newStart = $argtrim;
  $newStart =~ s/^(-)?p//;
  if ( !$newStart ) { $justShow = 1; }
  else {
    my $ns2 = $newStart + 750;
    open( A, ">c:/writing/dict/p1.txt" );
    print A "$newStart\n"
      . ( scalar localtime( time() ) ) . "\n"
      . ( scalar localtime( time() + 43200 ) )
      . "\n$ns2\n";
    close(A);
    $stdin = 1;
  }
}

elsif ( ( $argtrim eq "i" ) || ( $argtrim eq "1" ) ) { $stdin = 1; }
elsif ( $argtrim =~ /[0-9]+$/ ) {
  my $wordfile = "c:\\writing\\dict\\words-$argtrim.txt";
  if ( $argtrim == 0 ) { $wordfile = "c:\\writing\\dict\\brit-1word.txt"; }
  if ( !$wordfile ) { die("No word file $wordfile.") }
  `$wordfile`;
  exit();
}

my @firstStuff = split( "", $firstStuffString );

printTimeFile();

if ( $ARGV[0] =~ /^[-=\+]/i ) {
  if ( $ARGV[0] !~ /[a-z]/i ) {
    print "No spaces between +=- and a letter.\n";
    exit();
  }
  my $toAdd = $ARGV[0];
  $toAdd =~ s/^[-=+]+//;
  my $l      = length($toAdd);
  my $inDict = 0;
  open( A, "c:\\writing\\dict\\words-$l.txt" )
    || do { print "No file for words of length $l.\n"; exit(); };
  while ( $a = <A> ) {
    chomp($a);
    if ( lc($a) eq lc($toAdd) ) { $inDict = 1; }
  }
  close(A);
  if ( $inDict == 0 ) {
    if ( $ARGV[0] !~ /^[=+]{2}/ ) {
      die("Need extra =/+ for word not in dictionary.");
    }
  }
  if ( $toAdd =~ /[^a-z]/i ) {
    die("Bailing, $toAdd contains non-alphabetical characters.");
  }
  addToDict( $toAdd, 0 );
  addToErrs( $ARGV[0] );
  exit();
}

my $count = 0;

my $lastOne  = "";
my $firstOne = "";
my $whichf   = length( $ARGV[0] );

my $wordBad = 0;
my $wrongs  = "";

if ( defined( $ARGV[1] ) ) { $wrongs = $ARGV[1]; }

my $line;

open( A, "$misses" ) || die("No misses file.");
while ( $line = <A> ) {
  chomp($line);
  my @q = split( /:/, $line );
  if ( defined( $miss{ lc( $q[0] ) } ) ) { print "$q[0] duplicated.\n"; }
  $miss{ lc( $q[0] ) } = $q[1];
}
close(A);

my $canAlphabetize = 0;

#if ($r =~ /$ARGV[1]/i) { die; }
#else { die ("$r !~ $ARGV[1]"); }

if ( !$stdin ) { oneHangman( $ARGV[0], $wrongs ); }
else {
  my $temp;
  while ( $temp = getStdin() ) {
    chomp($temp);
    $temp =~ s/^[ \t]*//;
    if ( lc($temp) eq "t" ) {
      printTimeFile();
      next;
    }
    if ( $temp =~ /^[-=\+]/ ) { addToErrs($temp); next; }
    if ( $temp eq "?" )       { usage();          next; }
    if ( $temp =~ /^\?/ ) {
      $temp =~ s/^.//;
      print "Looking up definition of $temp...\n";
      `start http://www.thefreedictionary.com/$temp`;
      next;
    }
    if ( $temp =~ /b1\.pl/ ) {
      print "Wiping out everything before b1.pl.\n";
      $temp =~ s/.*b1\.pl *//i;
    }
    if ( ( $temp eq "q" ) || ( $temp eq "" ) ) {
      print("OK, see you later.\n");
      last;
    }
    my @tohang = split( / +/, $temp );
    if ( $#tohang == 0 ) { push( @tohang, "" ); }
    if ( $#tohang > 1 ) { print "Need 2 args.\n"; next; }
    $missFound = 0;
    oneHangman( $tohang[0], $tohang[1] );
  }
}

###########################################
#
# subroutines
#
#

sub cleanup {
  print "You hit ctrl-c.\n";
}

sub getStdin {
  print "Enter word-part or command (t to show time/score stuff) :\n";
  return ( my $temp = <STDIN> );
}

sub oneHangman {

  @prevMiss = ();
  $count    = 0;

#this is a step to save time. If we know the first letter, we don't look through the file and compare it, because anything with the 25 other letters to start it is wrong.
  my %val;
  %f2   = ();
  %freq = ();

  my $ignoreOverlap = ( $_[1] =~ /\// );
  $_[1] =~ s/[\\\/]//g;

  my $readFile = sprintf( "c:\\writing\\dict\\words-%d.txt", length( $_[0] ) );

  #print "Trying $readFile.\n";
  if ( length( $_[0] ) < 3 ) { print "$_[0] too short.\n"; return; }
  open( A, "$readFile" ) || die("No $readFile");
  my $canAlphabetize = 0;
  my $lastOne;
  my $firstOne;
  my $gotForced = "";

  if ( $_[0] =~ /[^a-z.,]/i ) { print "Bad characters in $_[0].\n"; return; }

  if ( $_[0] =~ /^[a-z]/i ) {
    $canAlphabetize = 1;
    $lastOne        = lc( $_[0] );
    $lastOne =~ s/[.,].*//g;
    $lastOne .= "zzz";
    $firstOne = uc( substr( lc( $_[0] ), 0, 1 ) );
  }

  my $wrongString = lc( $_[1] );

  if ( $wrongString && ( lc( $_[0] ) =~ /[$wrongString]/ ) ) {
    if ($ignoreOverlap) {
      print "Overlap, but wiping out extra characters.\n";
      $wrongString =~ s/[$_[0]]//g;
    }
    else {
      print
        "Oops, found string and wrong string overlap. Add / to ignore this.\n";
      return;
    }
  }

  my @dup = sort( split( //, $wrongString ) );
  my $lastDup = "";

  for ( 0 .. $#dup - 1 ) {
    if ( ( $dup[$_] eq $dup[ $_ + 1 ] ) && ( $dup[$_] ne $lastDup ) ) {
      print "$dup[$_] is duplicated in guessed-string.\n";
      $lastDup = $dup[$_];
    }
  }

  my @right = split( //, lc( $_[0] ) );
  my @wrong = split( //, $wrongString );
  my @toGuess;

  while ( $line = <A> ) {
    chomp($line);

    #if (length($line) != length($_[0])) { next; }
    if ($canAlphabetize) {
      if ( $line le $firstOne ) { next; }
      if ( $lastOne le $line )  { last; }
    }
    $line    = lc($line);
    @toGuess = split( //, $line );
    $wordBad = 0;
    for ( 0 .. $#toGuess ) {
      if ( ( $toGuess[$_] eq $right[$_] ) ) { next; }
      elsif ( ( $right[$_] ne "." ) && ( $right[$_] ne "," ) ) {
        $wordBad = 1;
        last;
      }
      for my $x ( 0 .. $#wrong ) {
        if ( $wrong[$x] eq "+" ) {
          print "+ should be at the start.\n";
          $wordBad = 1;
          last;
        }
        if ( $line =~ $wrong[$x] ) { $wordBad = 1; last; }
      }
    }
    if ( !$wordBad ) { checkForRepeats( $_[0], $line ); }
  }
  if ( $#prevMiss > -1 ) {
    print "MISSED BEFORE:\n";
    for (@prevMiss) {
      $count++;
      $missFound++;
      print "**** $count ($missFound) $_ $miss{$_}x\n";
    }
  }

  if ( $count > 1 ) {
    print "FREQUENCIES:";

    #for (@right) { if (defined($freq{$_})) { delete($freq{$_}); } }
    foreach my $val (
      sort { $f2{$b} <=> $f2{$a} or $freq{$b} <=> $freq{$a} or $a cmp $b }
      keys %freq
      )
    {
      if ( !$crossword ) {
        if ( $f2{$val} == $count ) {
          $gotForced .= "$val";
          print " **$val**";
          next;
        }
      }
      print " $val:$f2{$val}/$freq{$val}";
    }
    print "\n";
  }
  elsif ( $count + $missFound == 0 ) { print "Uh oh no matches.\n"; }
  else                               { print "Only one match found.\n"; }

  if ( $count > 1 ) {
    my $checkPopular = "";
    for (@firstStuff) {
      $checkPopular .= " $_" if ( "$_[0]$_[1]" !~ /$_/ );
    }
    if ($gotForced) {
      for ( split( //, $gotForced ) ) { $checkPopular =~ s/ $_//g; }
      print "FORCED MATCHES: $gotForced\n";
    }
    print "CHECK POPULAR:$checkPopular\n" if $checkPopular;
  }
  close(A);
}

sub checkForRepeats {
  my @a1 = split( //, lc( $_[0] ) );
  my @a2 = split( //, lc( $_[1] ) );

  if ( !$crossword ) {
    my $a3 = lc( $_[0] );
    $a3 =~ s/\.//g;

    for ( 0 .. $#a2 ) {
      if ( ( $a1[$_] ne "." ) && ( $a1[$_] ne "," ) ) { $a2[$_] = ""; }
    }

    my $a4 = join( "", @a2 );

    my @b3 = split( //, $a3 );

    #print "Now @a1 vs @a2 with @b3\n";

    for my $j (@b3) {
      if ( $a4 =~ /$j/ ) {

        #print "$_[0] contains extra guessed letters from $_[0] namely $j.\n";
        return;
      }
    }
  }
  for (@a2) {
    if ($_) { $freq{$_}++; }
  }
  my @a2a = uniq(@a2);
  for (@a2a) {
    if ($_) { $f2{$_}++; }
  }

  if ( $miss{$line} ) {
    push( @prevMiss, $line );
  }
  else {
    $count++;
    if    ( $count < 1000 )  { print "$count $line\n"; }
    elsif ( $count == 1000 ) { print "1000+.\n"; }
  }
}

sub addToErrs {
  my %val;
  my $addit = 0;
  if ( $_[0] =~ /^\+/ ) { $addit = 1; }
  if ( $_[0] =~ /^\-/ ) { $addit = -1; }
  my $gotIt = 0;
  my $toAdd = lc( $_[0] );
  $toAdd =~ s/^[-=\+]+//g;
  if ( !$toAdd ) { print("Added nothing."); die; }
  if ( $toAdd =~ /[^a-z]/i ) { die("Bad characters in what to add."); }
  open( A, "$misses" );

  while ( my $line = <A> ) {
    chomp($line);
    if ( $line =~ /:/ ) {
      my @this = split( /:/, $line );
      $val{ $this[0] } = $this[1];
      $line = $this[0];
    }
    else { $val{$line} = 1; }    # eg if a line is not word:#, make it word:1
    if ( $toAdd eq $line ) {
      if ( defined( $val{$line} ) ) {
        $val{$toAdd} += $addit;
        print "$line already in. Its weight is now $val{$line}.\n";
        $gotIt = 1;
      }
    }
  }
  close(A);
  if ( !$gotIt ) {
    if ( $addit == -1 ) {
      print "Did not find $toAdd, so I won't subtract an occurrence.\n";
      return;
    }
    print "Added $toAdd to misses file with value $addit.\n";
    $val{$toAdd} += $addit;
  }
  open( B, ">$misses" );
  for my $z ( sort keys %val ) { print B "$z:$val{$z}\n"; }
  close(B);
}

sub showMisses {
  my %amt;
  open( A, "$misses" );
  while ( $a = <A> ) {
    chomp($a);
    $a =~ s/.*://g;
    $amt{$a}++;
  }

  for my $am ( sort keys %amt ) {
    print "$am misses: $amt{$am}\n";
  }
}

sub addToDict {
  my $l           = length( $_[0] );
  my $uc          = uc( $_[0] );
  my $lc          = lc( $_[0] );
  my $wordfile    = "c:\\writing\\dict\\words-$l.txt";
  my $wordTo      = "c:\\writing\\dict\\words-new-hangman.txt";
  my $insertedYet = 0;
  open( A, $wordfile );
  open( B, ">$wordTo" );
  while ( $a = <A> ) {

    if ( ( !$insertedYet ) && ( $lc lt lc($a) ) ) {
      print B "$uc\n";
      $insertedYet = 1;
    }
    print B $a;
    chomp($a);
    if ( lc($a) eq lc( $_[0] ) ) {
      if ( $_[1] == 1 ) {
        print "$_[0] already in $wordfile.";
      }
      close(A);
      close(B);
      `erase $wordTo`;
      return;
    }
  }
  if ( !$insertedYet ) { print B "$uc\n"; }
  close(A);
  close(B);
  print "Added $_[0] to $wordfile.\n";
  `copy $wordTo $wordfile`;
}

sub printTimeFile {
  my $lmt = ( stat($misses) )[9];
  my $lmm = scalar localtime($lmt);
  my $lmd = $lmt - time() + 43200;

  open( A, $b1time );
  my $cur   = <A>;
  my $date  = <A>;
  my $date2 = <A>;
  my $can   = <A>;
  die("Maximum = $can") if $justShow;

  print "Start=$cur";
  print "LastDate=$date";
  print "NextDate=$date2";
  print "End=$can";
  print "LastModifiedMissed=$lmm\n";
  print( $lmd > 0
    ? "Won't get bonus yet (I think), $lmd seconds to go.\n"
    : "OK, hangman away.\n" );
}

sub usage {
  print <<EOT;
number opens words-(#).txt, 0 the whole big one
=(word) adds it without admitting wrong
+(word) adds word or increases its wrong count
-(word) decreases a word's wrong count
[#*](word) runs in crossword mode e.g. ad. can be add
e = open misses file b1.txt
c = open this code file
s = show misses
? = this usage
i = use stdin
EOT
}
