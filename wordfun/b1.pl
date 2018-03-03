#####################################
#b1.pl
#
#this takes a sequence of hangman letters with correctly guessed places
#along with incorrect guesses and then looks through a dictionary
#
#then prints out results, with the most likely letters left
#
# +markup +markup = not there (command 2x in a row doesn't show it if you have say m.rkup)

# b1 if other already open - reject? Or say, delete file x?

# bug can't add word that isn't in the dictionary in first place (omeprazole)

use WWW::Mechanize;
use strict;
use warnings;
use List::MoreUtils qw(uniq);
use File::Stat;
use Date::Parse;

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
my $stdin   = 0;
my $lastCan = 0;
my $lastWord;
my $lastCheckPoints = 0;

# unimplemented option, must be set in file
my $justShow = 0;

my $del       = 0;
my $crossword = 0;

my $firstStuffString = "esirotlan";
my @firstStuff = split( "", $firstStuffString );

my @postproc = ();
my @argvmod  = ();

my $argcount = 0;

my $firstWrongGuess = "";
my $guessResult     = "";
my $addMiss         = "";

my $gplasttime   = 0;
my $gplastscore  = 0;
my $gpfirsttime  = 0;
my $gpfirstscore = 0;

my %allWords;

while ( $argcount <= $#ARGV ) {
  my $arg = lc( $ARGV[$argcount] );
  my $arg2 = $argcount < $#ARGV ? lc( $ARGV[ $argcount + 1 ] ) : "";

  for ($arg) {
    /b1\.pl/i && do {
      print "Oops, forgot to delete b1.\n" if $del == 0;
      $del = 1;
      $argcount++;
      next;
    };
    /^-?f/ && do {
      die("Need a word to force into the list.") if !$arg2;
      addToDict( $arg2, 1 );
      exit();
    };
    /^-?e$/i && do { `$misses`; exit(); };
    /^-?c$/i
      && do { my $cmd = 'start "" "notepad++.exe" ' . (__FILE__); exit(); };
    /^-?i$/i && do { $stdin = 1; $argcount++; next; };
    /^-?s$/i  && do { showMisses(); exit(); };
    /^-?\?^/i && do { usage();      exit(); };
    push( @argvmod, $arg );
    $argcount++;
  }

}

if ( !$stdin && ( ( scalar @argvmod ) == 0 ) ) {
  print "No arguments. Going with standard in.\n";
  $stdin = 1;
}

my $count = 0;

my $lastOne  = "";
my $firstOne = "";

my $wordBad = 0;

# read in the misses
my $line;
open( A, "$misses" ) || die("No misses file.");
while ( $line = <A> ) {
  chomp($line);
  my @q = split( /:/, $line );
  if ( defined( $miss{ lc( $q[0] ) } ) ) { print "$q[0] duplicated.\n"; }
  $miss{ lc( $q[0] ) } = $q[1];
}
close(A);

#for my $j (sort keys %miss) { print "$j $miss{$j}\n"; }; exit();

my $canAlphabetize = 0;

#if ($r =~ /$ARGV[1]/i) { die; }
#else { die ("$r !~ $ARGV[1]"); }

readOneLine(@argvmod) if ( ( scalar @argvmod ) > 0 );

exit() if ( !$stdin );

my $temp;

while ( $temp = getStdin() ) {
  $temp = lc($temp);
  chomp($temp);

  if ( $temp eq "" ) {
    print "See you later!\n";
    exit();
  }

  # get rid of errant b1 / text before question mark first
  if ( $temp =~ /b1\.pl/ ) {
    print "Wiping out everything before b1.pl.\n";
    $temp =~ s/.*b1\.pl *//i;
  }

  if ( $temp =~ /^.+\?/ ) {
    print "Cutting off text before question mark...\n";
    $temp =~ s/.*\?/\?/;
  }

  # run commands and ignore hangman processing, if applicable

  if ( $temp =~ /^'/ ) {
    $temp =~ s/^'//;
    print "Running command $temp\n";
    `$temp`;
    next;
  }
  my @cmdAry = split( " ", $temp );

  readOneLine(@cmdAry);
}

###########################################
#
# subroutines
#
#

sub readOneLine {
  my $argc     = 0;
  my $soFar    = "";
  my $wrongs   = "";
  my $amax     = ( scalar @_ );
  my $doneMeta = 0;

  if ( ( $amax == 0 ) && $stdin ) {
    print "Nothing in line. See you later!\n";
    exit();
  }

  my $arg;
  while ( $argc < $amax ) {
    $arg = $_[$argc];

    if ( lc($arg) =~ /^[ainp][0-9]+$/i ) {
      updateP1File($arg);
      $stdin = 1;
      $argc++;
      $doneMeta = 1;
      next;
    }
    elsif ( $arg eq "0" ) {
      open( A, ">>$misses" );
      close(A);
      print "Tweaked timestamp for $misses.\n";
      $doneMeta = 1;
      next;
    }
    if ( ( $arg eq "q" ) || ( $arg eq "" ) ) {
      print "This has no special meaning without stdin.\n" if !$stdin;
      print("OK, see you later.\n");
      exit();
    }
    elsif ( lc($arg) eq "s" ) {
      getPoints(0);
      return;
    }
    elsif ( lc($arg) eq "se" ) {
      getPoints(1);
      return;
    }
    elsif ( lc($arg) eq "sl" ) {
      system("start http://secure.thefreedictionary.com");
      return;
    }
    elsif ( lc($arg) eq "t" ) {
      printTimeFile();
      return;
    }
    elsif ( $arg =~ /^[0-=\+]/ ) { addToErrs($arg); return; }
    elsif ( $arg eq "?" ) {
      usage() if !$stdin;
      if ($lastWord) {
        print("Looking up last word $lastWord.\n");
        system("start http://www.thefreedictionary.com/$lastWord");
      }
      else {
        print("No determined last word.\n");
      }
      $doneMeta = 1;
    }
    elsif ( $arg =~ /^\?/ ) {
      ( my $arg2 = $arg ) =~ s/^\?//;
      print "Looking up $arg2.\n";
      system("start http://www.thefreedictionary.com/$arg2");
      return;
    }
    elsif ( $arg eq "??" ) {
      usage();
    }
    elsif ( $arg =~ /^[a-z]+$/ ) {
      if ($wrongs) {
        print "Two lists of wrong guesses: $wrongs and $arg.\n";
        return;
      }
      $wrongs = $arg;
    }
    elsif ( ( $arg =~ /^[a-z\.]+$/ ) && ( $arg =~ /\./ ) ) {
      if ($soFar) {
        print "Two guess-words: $soFar and $arg.";
        return;
      }
      $soFar = $arg;
    }
    $argc++;
  }
  return if ( !$soFar && $doneMeta );
  oneHangman( $soFar, $wrongs );
}

sub cleanup {
  print "You hit ctrl-c.\n";
  exit();
}

sub getStdin {
  print "Enter word-part or command (t to show time/score stuff) :\n";
  return ( my $temp = <STDIN> );
}

sub oneHangman {

  @prevMiss  = ();
  $count     = 0;
  $missFound = 0;

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
  if ( scalar(@prevMiss) ) {
    print "MISSED BEFORE:\n";
    $missFound = 0;
    for ( sort { $miss{$a} <=> $miss{$b} || $a cmp $b } @prevMiss ) {
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

  if    ( $#prevMiss == 0 )          { $lastWord = $prevMiss[0]; }
  elsif ( $count + $missFound != 1 ) { $lastWord = ""; }

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

  $lastWord = $line;
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
  if ( $_[0] =~ /^\0/ ) { $addit = -2; }
  my $gotIt   = 0;
  my $toAdd   = lc( $_[0] );
  my $forceIt = ( $toAdd =~ /\+\+/ );
  $toAdd =~ s/^[-=\+0]+//g;
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
        if ( $addit == -2 ) {
          $val{$toAdd}  = 0;
          $miss{$toAdd} = 0;
        }
        else {
          $val{$toAdd}  += $addit;
          $miss{$toAdd} += $addit;
          print "$line already in. Its weight is now $val{$line}.\n";
        }
        $gotIt    = 1;
        $lastWord = $line;
      }
    }
  }
  close(A);

  # don't waste a second reading in until we need to check this 1st-missed word
  if ( !( scalar keys %allWords ) && !defined( $val{$toAdd} ) ) {
    print "Reading in word file for the first time...\n";
    open( A, "c:/writing/dict/brit-1word.txt" );
    while ( $line = <A> ) {
      chomp($line);
      $allWords{ lc($line) } = 1;
    }
    close(A);
  }

  if ( !$gotIt ) {
    if ( $addit == -1 ) {
      print "Did not find $toAdd, so I won't subtract an occurrence.\n";
      return;
    }
    if ( !$forceIt && !defined( $allWords{$toAdd} ) ) {
      print
"$toAdd not in the laundry list of words so I'm not adding it. Use ++ to force things.\n";
      return;
    }
    print "Added $toAdd to misses file with value $addit.\n";
    $val{$toAdd} += $addit;
    $lastWord = $toAdd;
  }
  open( B, ">$misses" );
  for my $z ( sort keys %val ) { print B "$z:$val{$z}\n" if $val{$z}; }
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

sub getPoints {
  my $mech = WWW::Mechanize->new();

  open( A, $b1time );
  my $cur  = <A>;
  my $date = <A>;
  chomp($date);
  my $date2 = <A>;
  my $can   = <A>;
  die("Maximum = $can") if $justShow;
  $lastCan = $can;
  chomp($lastCan);
  close(A);
  my $epochDate = str2time($date);
  my $ct        = time();
  my $timeDelta = $ct - $epochDate;

  my $link = "http://secure.thefreedictionary.com/user/Andrew_Schultz";
  print "Reading $link...\n";

  $mech->get("$link");
  my $c = $mech->content;
  my @d = split( "\n", $c );

  for (@d) {
    if ( $_ =~ /meta name="Description"/i ) {
      my $points = $_;
      $points =~ s/ points.*//i;
      $points =~ s/.* //;
      print "$points\n";
      my $left = $lastCan - $points;
      $lastCheckPoints = $points;
      my $pointDelta = $points - $cur;
      if ( $pointDelta <= 0 ) {
        print("Can't estimate end.\n");
        return;
      }
      elsif ( $pointDelta > 750 ) {
        print("Went past end\n");
        return;
      }
      print "$points points. Can get $lastCan. Left=$left\n";
      $pointDelta = winsDelta($pointDelta);
      my $pointSlope   = sprintf( "%.3f", 60 * $pointDelta / $timeDelta );
      my $timeGap      = $timeDelta * 700 / $pointDelta;
      my $finalTime    = $timeDelta * 700 / $pointDelta + $epochDate;
      my @projectArray = ( 5 .. 15 );
      @projectArray = ( 5, 6, 7.5, 10, 12, 15 ) if !$_[0];

      for my $x (@projectArray) {
        my $projTimeLeft = ( 700 - $pointDelta ) * 60 / $x;
        my $projTime     = localtime( $projTimeLeft + $ct );
        print "$x per minute means you end at $projTime.\n";
      }
      printf(
        "%d to go, $pointSlope per minute\nstart $date ETA "
          . localtime($finalTime)
          . ", total time so far=%d sec, projected = %d sec\n",
        ( scalar 700 - $pointDelta ),
        $timeDelta, $finalTime - $epochDate
      ) . ( $pointDelta < 50 ? " ... still in twofer range" : "" );
      if ( $gplasttime && ( $points - $gplastscore ) && ( $ct - $gplasttime ) )
      {
        my $pd = $pointDelta - winsDelta( $gplastscore - $cur );
        my $td = $ct - $gplasttime;
        my $slope          = $pd / $td;                      # points per second
        my $timeLeftRecent = ( 700 - $pointDelta ) / $slope;
        my $lastProjTime = localtime( $timeLeftRecent + $ct );
        $slope = sprintf( "%.3f", 60 * $slope );
        print
"Per-minute slope since last check: $slope($pd/$td), ETA = $lastProjTime\n";
      }
      $gpfirsttime  = $ct     if !$gpfirsttime;
      $gpfirstscore = $points if !$gpfirstscore;
      $gplasttime   = $ct;
      $gplastscore  = $points;
      return;
    }
  }

  print("Got nothing. Check to see if you need to enter a CAPTCHA.\n");

}

sub winsDelta {
  return ( $_[0] > 50 ? $_[0] - 50 : $_[0] / 2 );
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
  $lastCan = $can;
  chomp($lastCan);

  print "Start=$cur";
  print "LastDate=$date";
  print "NextDate=$date2";
  print "End=$can";
  print "LastCheckPoints=$lastCheckPoints\n" if $lastCheckPoints;
  print "LastModifiedMissed=$lmm\n";
  print( $lmd > 0
    ? "Won't get bonus yet (I think), $lmd seconds to go.\n"
    : "OK, hangman away.\n"
  );
}

sub updateP1File {
  my $delta = $_[0];
  $delta =~ s/^.//;
  my $ns2 = $delta + 750;

  if ( $_[0] =~ /^[ip]/ )    # change the delta
  {
    open( A, ">$b1time" );
    print A "$delta\n"
      . ( scalar localtime( time() ) ) . "\n"
      . ( scalar localtime( time() + 43200 ) )
      . "\n$ns2\n";
    close(A);
  }
  elsif ( $_[0] =~ /^[an]/ )    # adjust
  {
    my @newfi;
    $delta -= 750 if $_[0] =~ /^n/;
    open( A, $b1time );
    while ( $a = <A> ) {
      push( @newfi, $a );
    }
    close(A);
    $newfi[0] += $delta;
    $newfi[3] += $delta;
    $newfi[0] .= "\n";
    $newfi[3] .= "\n";
    open( A, ">$b1time" );
    print A $_ for (@newfi);
    close(A);
    print "Added $delta to start/end.\n";
    $gplasttime   += $delta if $gplasttime;
    $gplastscore  += $delta if $gplastscore;
    $gpfirsttime  += $delta if $gpfirsttime;
    $gpfirstscore += $delta if $gpfirstscore;
  }
  else {
    die(
"Need an a/i/p at the start of a number to modify in $b1time. (a=adjust, i/p=fixed)"
    );
  }
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
