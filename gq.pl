# gq.pl: stands for "grep quick"
# this shows where certain text I may've already used pops up in a project.
# useful if I want to wipe a project of certain objects/names.
# originally for roiling/shuffling but expanded to other projects and project-groups.
#
# (old)
# -tb1 = table random, start with that word
# -tb = table random
# -t = table only
# usage
# gq.pl -tb rosco coors (matches both)
# gq.pl -tb rosco (matches one)
# gq.pl -tb1 rosco (matches starting with rosco)
# gq.pl -m 10 yes (matches 1st 10 yes's)
#
# todo: quick check for if in quotes
#

use POSIX;

use strict;
use warnings;
use lib "c:/writing/scripts";
use i7;

use Win32::Clipboard;

################constants
( my $gqfile   = __FILE__ ) =~ s/pl$/txt/i;
( my $gqdir    = $gqfile ) =~ s/\\[^\\]+$//g;
( my $readFile = __FILE__ ) =~ s/.pl$/-r.txt/i;

#################vars
my @availRuns = ();
my @thisAry   = ();
my $pwd       = getcwd();
my @runs      = ();
my $count     = 0;
my %map;
my %cmds;
my @errStuff;
my $blurby         = "";
my $myHeader       = "";
my $foundSomething = 0;
my $thisTable      = "";
my $shortName      = "";
my $totalFind      = 0;
my $lastHeader     = "";
my $othersToo      = 0;
my $foundTotal     = 0;
my $stringAtEnd    = "";
my $skippedAny     = 0;
my $verbose        = 0;

my @ignore_array = ();

my $fileToOpen = "";
my $lineToOpen = 0;

#################options
my $printTabbed       = 1;
my $printUntabbed     = 1;
my $onlyTables        = 0;
my $onlyRand          = 0;
my $firstStart        = 0;
my $runAll            = 0;
my $showRules         = 0;
my $showHeaders       = 0;
my $headersToo        = 0;
my $dontWant          = 0;
my $maxOverallFind    = 100;
my $maxFileFind       = 25;
my $getClipboard      = 0;
my $zapBrackets       = 0;
my $launchFirstSource = 0;
my $launchLastSource  = 0;
my $forceNum          = 1;
my $ignoreRand        = 0;
my $inQuotes          = 0;

my %foundCount;

my $pwd_runs = toProj($pwd);

while ( $count <= $#ARGV ) {
  $a = $ARGV[$count];
  $b = "";
  if ( defined( $ARGV[ $count + 1 ] ) ) {
    $b = $ARGV[ $count + 1 ];
  }

  for ($a) {
    /^0$/ && do { processNameConditionals(); exit; };
    /^(l1|1st)$/ && do { $launchFirstSource = 1; $count++; next; };
    /^(ll)$/     && do { $launchLastSource  = 1; $count++; next; };
    /^-?e$/ && do { `$gqfile`; exit; };
    /^\// && do {
      $thisAry[0] =~ s/^\///g;
      $onlyTables = 1;
      $onlyRand   = 1;
      $firstStart = 1;
      $count++;
      next;
    };
    /^-?v$/
      && do { $verbose = 1; $count++; next; }; # verbose e.g. show what files skipped
    /^-?a$/      && do { $runAll = 1;        $count++; next; };    # run all
    /^-?(o|oa)$/ && do { @runs   = ("oafs"); $count++; next; };    # oafs?
    /,/          && do {
      @runs = split( /,/, $a );
      if ( $runs[$#runs] eq "" ) { pop(@runs); }
      $count++;
      next;
    };
    /^-?fd$/
      && do { print "Reading default...\n"; readFile($readFile); $count++; next; };
    /^-?f$/ && do {
      my $rf2 = $readFile;
      $rf2 =~ s/-.\./$b/ if $b != "";
      readFile($rf2);
      $count++;
      next;
    };
    /^-?n$/ && do { @runs = ("names"); $count++; next; };    # names
    /^-?sno$/i && do {
      @runs = ("sno");
      $count++;
      next;
    };
    /^-?(3d|3|4d|4|opo)$/i
      && do { @runs = ("opo"); $count++; next; };            # 3dop try
    /^-?as[0-9]*$/i
      && do {
      @runs = ("as");
      if ( $a =~ /[0-9]/ ) {
        if ( $a !~ /1/ ) { push( @ignore_array, "compound" ); }
        if ( $a !~ /2/ ) { push( @ignore_array, "slicker" ); }
        if ( $a !~ /3/ ) { push( @ignore_array, "buck" ); }
        if ( $a !~ /4/ ) { push( @ignore_array, "seeker" ); }
      }
      $count++;
      next;
      };                                                     # Alec Smart?
    /^-?btp$/i && do {
      @runs = ("as");
      @ignore_array = ( @ignore_array, "compound", "slicker", "seeker" );
    };
    /^-?sc$/i && do {
      @runs = ("as");
      @ignore_array = ( @ignore_array, "compound", "buck", "seeker" );
    };
    /^-?pc$/i && do {
      @runs = ("as");
      @ignore_array = ( @ignore_array, "buck", "slicker", "seeker" );
    };
    /^-?ss$/i && do {
      @runs = ("as");
      @ignore_array = ( @ignore_array, "compound", "slicker", "buck" );
    };
    /^-?(r|roi|s|sa|sts)[0-9]*$/i
      && do {
      @runs = ("sts");
      if ( $a =~ /[0-9]/ ) {
        if ( $a !~ /2/ ) {
          push( @ignore_array, "roiling" );
          push( @ignore_array, "roi.txt" );
        }
        if ( $a !~ /1/ ) { push( @ignore_array, "shuffling" ); }
      }
      $count++;
      next;
      };    # roiling original? (default)
    /^-?(odd)$/i
      && do { @runs = ("odd"); $count++; next; };    # odd games
    /^-?(pu|up|ai)$/i
      && do { @runs = ("ai"); $count++; next; };     # Put It Up
    /^-?sr$/
      && do { $showRules = 1; $count++; next; };     # show the rules text is in
    /^-?h$/ && do { $showHeaders = 1; $count++; next; };
    /^-?ha$/ && do { processListFile(); openHistory(@availRuns); exit(); };
    /^-?hi$/ && do { openHistory( split( /,/, $b ) ); exit(); };
    /^-?c$/ && do {
      $getClipboard = 1;
      $othersToo    = 1;
      $count++;
      print
"WARNING: using clipboard invalidates command line text. Use -x for deluxe anagramming.\n";
      next;
    };
    /^-?x$/  && do { $othersToo   = 1;  $count++; next; };
    /^-?p$/  && do { $headersToo  = 1;  $count++; next; };
    /^-?iq$/ && do { $inQuotes    = 1;  $count++; next; };
    /^-?oq$/ && do { $inQuotes    = -1; $count++; next; };
    /^-?nt$/ && do { $printTabbed = 0;  $count++; next; };
    /^-?w$/  && do { $dontWant    = 1;  $count++; next; };
    /^-?ir$/ && do { $ignoreRand  = 1;  $count++; next; };
    /^-?nd$/ && do { newDefault($b); $count++; next; };
    /^-?#$/    && do { $forceNum      = 1; $count++; next; };
    /^-?ft$/   && do { $printUntabbed = 0; $count++; next; };
    /^-? zb $/ && do { $zapBrackets   = 1; $count++; next; };
    /^-mo$/    && do {

      if ( $b < 0 ) {
        print
"Changing negative to positive. Use 0 to remove max overall limits.\n";
      }
      $maxOverallFind = abs($b);
      $count += 2;
      next;
    };
    /^-?mf$/ && do {
      if ( $b < 0 ) {
        print
          "Changing negative to positive. Use 0 to remove max file limits.\n";
      }
      $maxFileFind = abs($b);
      $count += 2;
      next;
    };
    /^-?mu$/ && do { $maxFileFind = $maxOverallFind = 0; $count += 2; next; };
    /^-?t$/
      && do { $onlyTables = 1; $count++; next; }; #not perfect, -h + -t = conflict
    /^-?tb$/
      && do { $onlyTables = 1; $onlyRand = 1; $count++; next; }; #not perfect, -h + -t = conflict
    /^-?tb1$/
      && do { $onlyTables = 1; $onlyRand = 1; $firstStart = 1; $count++; next; }; #not perfect, -h + -t = conflict

    /^(=?)[\\0-9a-z'\.\/ ][-\\0-9a-z'\.\/ ]*([-=])?$/i && do {
      $a =~ s/^=//
        ;   # starting with = is one way to avoid a word clashing with an option
      $a =~ s/[-=]$//;    # ending with - is another
      if ( defined( $map{$a} ) ) {
        print "$a -> $map{$a}, use upper case to avoid\n";
        push( @thisAry, $map{$a} );
      }
      else {
        if ( $a =~ /[0-9]/ && !$forceNum ) {
          print
            "WARNING don't need/want number in array, to include it, add a #\n";
          $count++;
          next;
        }

        # print "$a into word array.\n";
        $a =~ s/\// /g
          ; # we can transform forward slashes into spaces so we don't have to use quotes
        push( @thisAry, $a );
      }
      $count++;
      next;
    };    # if we want to use AS as a word, it would be in upper case
    print "Argument $a failed.\n";
    usage();
  }

}

if ( $pwd_runs && !( scalar @runs ) ) {
  @runs = ($pwd_runs);
  print("Going with default current directory $pwd_runs.\n");
}
readLastRun() if ( !( scalar @runs ) );

if ( ( !$thisAry[0] ) && ( !$getClipboard ) ) {
  die("Need a process-able word for an argument.");
}

if ( ( $#runs == -1 ) && ( $#ARGV > 1 ) ) {
  print
    "NOTE: if a project name overlaps a flag, use the comma to detect it.\n";
}

die("Must print either tabbed or untabbed.")
  if ( !$printTabbed && !$printUntabbed );

processListFile();

my $myrun;

if ($runAll) {
  @runs = @availRuns;
}

if ($getClipboard) {
  my $clip    = Win32::Clipboard::new;
  my $cliptxt = $clip->Get();
  my @sets    = split( /[\n\r]+/, $cliptxt );
  for my $clipLine (@sets) {
    @thisAry = split( / /, $clipLine );
    tryOneAry();
  }
}
else {
  tryOneSet();
}

writeLastRun();

#################################################subroutines

sub tryOneSet {

  foreach $myrun (@runs) {
    processFiles($myrun);
    if ( $launchFirstSource || $launchLastSource ) {
      `$np $fileToOpen -n$lineToOpen`;
    }
    if ($othersToo) {
      if ( !grep( /^sts$/, @runs ) ) { next; }
      my $thisclump = join( "", @thisAry );

      #print "anan.pl $thisclump=\n";
      #print "myan.pl $thisclump=\n";
      print `anan.pl $thisclump=`;
      print `myan.pl $thisclump=`;
    }
  }

}

sub addSaveFile {
  my $saveFile = "c:\\writing\\scripts\\gq-$_[1].txt";
  my @saveData;
  my %saveHash;
  my $q = $_[0];
  $q =~ s/ //g;
  my $dontrewrite = 0;
  my $skipRead    = 0;
  push( @saveData, $_[0] );
  $saveHash{$q} = 1;

  open( A, $saveFile ) || do {
    warn("No save file $saveFile.");
    $skipRead = 1;
  };
  if ( !$skipRead ) {
    while ( $a = <A> ) {
      chomp($a);
      $a = lc($a);
      if ( $a =~ /[ \.-]/ ) {
        my @words = split( /[ \.-]/, lc $a );
        if ( $saveHash{"$words[1]$words[0]"} ) {
          print "$a already in save list.\n";
          $dontrewrite = 1;
          last;
        }
        if ( $saveHash{"$words[1]s$words[0]"} ) {
          print "$a already in save list.\n";
          $dontrewrite = 1;
          last;
        }
        if ( $saveHash{"$words[1]$words[0]s"} ) {
          print "$a already in save list.\n";
          $dontrewrite = 1;
          last;
        }
        if ( $saveHash{"$words[1]s$words[0]s"} ) {
          print "$a already in save list.\n";
          $dontrewrite = 1;
          last;
        }
        if ( $saveHash{"$words[0]$words[1]"} ) {
          print "$a already in save list.\n";
          $dontrewrite = 1;
          last;
        }
        if ( $saveHash{"$words[0]s$words[1]"} ) {
          print "$a already in save list.\n";
          $dontrewrite = 1;
          last;
        }
        if ( $saveHash{"$words[0]$words[1]s"} ) {
          print "$a already in save list.\n";
          $dontrewrite = 1;
          last;
        }
        if ( $saveHash{"$words[0]s$words[1]s"} ) {
          print "$a already in save list.\n";
          $dontrewrite = 1;
          last;
        }
      }
      else {
        if ( $saveHash{$a} || $saveHash{"${a}s"} ) {
          print "$a already in save list.\n";
          $dontrewrite = 1;
          last;
        } # trick/reference: how to separate perl variables from interpolated strings
      }
      $a =~ s/ //g;
      if ( $a eq $q ) {
        print "$a already in save list.\n";
        $dontrewrite = 1;
        last;
      }
      $saveHash{$a} = 1;
      if ( $#saveData == 99 ) { last; }
      push( @saveData, $a );
    }
    close(A);
  }
  if ($dontrewrite) { return; }
  open( A, ">$saveFile" );
  for (@saveData) {
    print A "$_\n";
  }
  close(A);
  print "Wrote $_[0] to $saveFile.\n";
}

sub processListFile {
  my $line;
  my $defaultString;
  my $currentLedger;
  my $match;

  open( A, $gqfile ) || die("Can't find $gqfile.");

OUTER:
  while ( $line = <A> ) {
    if ( $line =~ /^#/ ) { next; }
    if ( $line =~ /^;/ ) { last; }
    for $match (@ignore_array) {
      if ( $line =~ /$match/i ) {
        $skippedAny = 0;
        print("Skipping $line") if $verbose;
        next OUTER;
      }
    }

    if ( $line =~ /^MAP=/ ) {
      chomp($line);
      $line =~ s/^MAP=//;
      my @b = split( /:/, $line );
      my @c = split( /,/, @b );
      for (@c) { $map{$_} = $b[1]; }
    }
    if ( $line =~ /^DEFAULT=/ ) {
      $defaultString = $line;
      chomp($defaultString);
      $defaultString =~ s/DEFAULT=//;
    }
    if ( $line =~ /^run=/ ) {
      chomp($line);
      $line =~ s/.*=//g;
      $currentLedger = $line;
      push( @availRuns, $line );
      next;
    }
    if ( $line !~ /[a-z]/i ) { $currentLedger = ""; next; }
    if ($currentLedger) {
      $cmds{$currentLedger} .= $line;
    }

  }
  close(A);
  if ( $#runs == -1 ) {
    if ($defaultString) { @runs = ($defaultString); }
    else {
      die(
"No default string specified in $gqfile, and no project specified in the command line. Bailing.\n"
      );
    }
  }
}

sub processFiles {
  my @x;
  if ( defined( $cmds{ $_[0] } ) ) { @x = split( /\n/, $cmds{ $_[0] } ); }
  if ( !@x ) {
    print "Using only story file for $_[0].\n";
    @x = ("story.ni");
  }

  #for my $q (sort keys %cmds) { print "$q...$cmds{$q}\n"; } return;

  foreach my $cmd (@x) {
    if ( $foundTotal == $maxOverallFind ) { print "Skipping $cmd\n"; next; }
    my @fileAndMarkers = split( /\t/, $cmd );
    processOneFile(@fileAndMarkers);
  }
  print "IMPORTANT END STRING STUFF:\n$stringAtEnd" if $stringAtEnd;
  my @blanks = ();
  my @gots   = ();
  for my $x ( sort keys %foundCount ) {
    if ( $foundCount{$x} == 0 ) {
      push( @blanks, $x );
    }
    else {
      push( @gots, $x );
    }
  }
  if ( $#gots == -1 ) {
    print
"No matches anywhere! This is good, if you're redacting, or bad, if you hoped to find something."
      . ( $skippedAny ? " (you skipped a few files, though)" : "" ) . "\n";
  }
  else {
    if ( $#blanks > -1 ) {
      print "FILES WITH NO MATCHES: " . join( ", ", @blanks ) . "\n";
    }
    print "FILES WITH MATCHES ("
      . ( scalar @gots )
      . "/$foundTotal): "
      . join( ", ", map { "$_=$foundCount{$_}" } @gots ) . "\n";
  }
  if ( $errStuff[0] ) {
    print "TEST RESULTS: $_[0],0,"
      . $#errStuff + 1 . ",0,"
      . join( "<br />", @errStuff ) . "\n";
  }
  addSaveFile( join( " ", @thisAry ), $_[0] );
}

sub processOneFile {
  my $inImportant     = 1;
  my $alwaysImportant = 1;
  my $inTable         = 0;
  my $line            = 0;
  my $currentTable    = "";
  my $foundOne        = 0;
  my $latestRule;
  my $thisImportant = 0;
  my $idx;
  my @importants;
  my @quoteAry;

  if ( $_[1] ) {
    $inImportant     = 0;
    $alwaysImportant = 0;
    @importants      = split( /,/, $_[1] );
  }
  my $modFile = $_[0];
  if ( $modFile =~ /inform[\\\/]source/i ) {
    $modFile =~ s/.*[^\\\/][\\\/]([a-z0-9-]*).inform.source[\\\/]/$1:/i;
    $modFile =~ s/.*[\\\/]//;
  }
  if ( $modFile =~ /\.trizbort/ ) { $modFile =~ s/.*[\\\/]/TRIZ /g; }
  if ( $modFile =~ /\.i7x/ )      { $modFile =~ s/.*[\\\/]/EXT /g; }

  # print "$_[0] => $modFile\n"; return;
  open( A, "$_[0]" ) || die("No $_[0]. Create it or remove it from gq.txt.");
  while ( $a = <A> ) {
    my $temp = $a;
    if ( $inQuotes && ( $a =~ /\"/ ) ) {
      my $temp = $a;
      @quoteAry = split( "\"", $a );
      $a = join( " ",
        @quoteAry[ grep { 2 * ( $_ % 2 ) == ( $inQuotes + 1 ) }
          0 .. $#quoteAry ] );
    }
    if ($zapBrackets) { $a =~ s/\[[^\]]*\]/ /g; }
    if ( ( $a =~ /^[a-z]/ ) && ( $a !~ /\t/ ) ) { $latestRule = "$a"; }
    if ($inImportant) { $idx++; }
    if ( $a =~ /^\\/ ) {
      if ( $_[1] ) {
        for (@importants) {
          if ( $a =~ /^\\$_[=\|]/ ) {
            $idx           = 0;
            $inImportant   = 1;
            $thisImportant = $a;
            chomp($thisImportant);
            $thisImportant =~ s/[\|=].*//g;
          }
        }
      }
      else {
        $thisImportant = $a;
        $thisImportant =~ s/^\\//g;
        $thisImportant =~ s/[=\\].*//g;
        chomp($thisImportant);
      }
    }
    $line++;
    if ( ( $a =~ /^table of / ) && ( !$currentTable ) ) {
      $idx          = -1;
      $currentTable = $a;
      $currentTable =~ s/ *\[.*//g;
      $currentTable =~ s/\t//g;
      chomp($currentTable);
      $inTable = 1;
    }
    if ( ( $a !~ /[a-z]/i ) || ( $a =~ /^\[/ ) ) {
      $currentTable = "";
      $inTable      = 0;
      if ( !$alwaysImportant ) { $inImportant = 0; $thisImportant = ""; }
    }
    ( my $a2 = $a ) =~ s/[!\.\?:; -]+/ /g;
    my $crom = cromu( $a2, $_[0] );
    if ( $inImportant && $crom && ( !$inTable || !$ignoreRand ) ) {
      my $tempString = "";
      my $sbl        = shouldBeLast($a);
      chomp($a);
      if ($dontWant) { push( @errStuff, "$modFile L$idx" ); }
      $foundOne++;
      $foundTotal++;
      ( my $a2 = $a ) =~ s/^\t+/\|\| /g;
      $tempString = "$modFile($line";
      $tempString .= ",$currentTable"        if $currentTable;
      $tempString .= ",$thisImportant,L$idx" if $thisImportant;
      $tempString .= "): $a2";
      $tempString .= " **PLURAL**"           if $crom == 2;
      $tempString .= "\n";
      $tempString .= "RULE=$latestRule"      if $showRules;
      if ($sbl) { $stringAtEnd .= $tempString; next; }
      $tempString = "Results for $modFile:\n" . $tempString if $foundOne == 1;
      print $tempString;

      if ( $maxFileFind && ( $foundOne == $maxFileFind ) ) {
        print
"----------Max $maxFileFind matches found per file. Use -mf to increase.\n";
        last;
      }
      if ( $maxOverallFind && ( $foundTotal == $maxOverallFind ) ) {
        print
"----------Max $maxOverallFind total matches found. Use -mo to increase.\n";
        last;
      }
      if ( $_[0] =~ /story.ni/ ) {
        $fileToOpen = $_[0];
        $lineToOpen = $. if !$lineToOpen || $launchLastSource;
      }
    }
  }
  close(A);
  $foundCount{$modFile} = $foundOne;
}

sub cromu {
  if ($firstStart) {
    if ( ( $_[0] !~ /^\"$thisAry[0]/i ) && ( $_[0] !~ /'$thisAry[0]'/i ) ) {
      return 0;
    }
  }

  $a =~ s/\[one of\]/\[\]/g;
  $a =~ s/\[end if\]/\[\]/g;

  return 0 if $_[0] =~ /^(volume|chapter|book|part|section)/i;

  return 0 if ( $_[0] =~ /^test/i ) && ( $_[1] !~ /test/i );

  #lumped together
  if ($#thisAry) {
    if ( $_[0] =~ /\b$thisAry[0]$thisAry[1]\b/i )  { return 1; }
    if ( $_[0] =~ /\b$thisAry[1]$thisAry[0]\b/i )  { return 1; }
    if ( $_[0] =~ /\b$thisAry[0]$thisAry[1]s\b/i ) { return 2; }
    if ( $_[0] =~ /\b$thisAry[1]$thisAry[0]s\b/i ) { return 2; }
    if ( ( $_[0] =~ /\b$thisAry[0]\b/i ) && ( $_[0] =~ /\b$thisAry[1]s\b/i ) ) {
      return 2;
    }
    if ( ( $_[0] =~ /\b$thisAry[0]s\b/i )
      && ( $_[0] =~ /\b$thisAry[1](s)?\b/i ) )
    {
      return 2;
    }
  }
  elsif ( $#thisAry == 0 ) {
    if ( $_[0] =~ /\b$thisAry[0]s\b/i ) { return 2; }
    if ( $_[0] =~ /\b$thisAry[0]\b/i )  { return 1; }
  }

  #words apart
  for my $tomatch (@thisAry) {
    if ( $_[0] !~ /\b$tomatch\b/i ) {
      if ( ($headersToo) && ( $myHeader =~ /\b$tomatch\b/i ) ) { next; }
      return 0;
    }
  }
  return 1;
}

sub newDefault {
  my @array;
  open( A, "$gqfile" );
  my $newDefLine = "DEFAULT=$_[1]";
  while ( $a = <A> ) {
    if ( $a =~ /^DEFAULT/ ) {
      push( @array, $newDefLine );
    }
    else {
      push( @array, $a );
    }
  }
  close(A);
  open( A, ">$gqfile" );
  print A join( "\n", @array );

}

sub processNameConditionals {
  open( A, "C:/games/inform/roiling.inform/Source/story.ni" )
    || die("Can't open Roiling source.");

  my $line;
  my $l2;
  my $l3;
  my $processTo;

  while ( $line = <A> ) {
    if ( $line =~ /section gender specific stubs/ ) {
      print "List of gender-says:\n";
      $processTo = 1;
      next;
    }
    if ($processTo) {
      if ( $line =~ /^section/ ) { last; }
      if ( $line =~ /^to / ) {
        $l2 = $line;
        chomp($l2);
        $l2 =~ s/to say //g;
        $l2 =~ s/:.*//g;
        $l3 = <A>;
        if ( $l3 =~ /\[one of\]/ ) {
          $l3 =~ s/.*one of\]//g;
          $l3 =~ s/\[in random.*//g;
          $l3 =~ s/\[or\]/\//g;
        }
        else {
          $l3 =~ s/\[end if.*//g;
          $l3 =~ s/.*if [^\]]*\]//g;
          $l3 =~ s/\[else\]/\//g;
        }
        print "$l2 = $l3";
      }
    }

  }
  close(A);

}

sub openHistory {
  if ( $#_ == -1 ) { die("Need an argument.\n"); }
  for (@_) {
    my $thisfile = "$gqdir\\gq-$_.txt";
    if ( -f "$thisfile" ) {
      `$thisfile`;
    }
    else { print "Oops no file $thisfile\n"; }
  }
}

sub shouldBeLast {
  return 1 if ( $_[0] =~ /understand.*howto.*gtxt/i );
  return 0;
}

sub readLastRun {
  ( my $gqlast = $gqfile ) =~ s/.txt$/-last.txt/i;
  open( A, $gqlast ) || do {
    print "You need a last file $gqlast.\n";
    return;
  };

  while ( $a = <A> ) {
    chomp($a);
    next unless ( $a =~ /,/ );
    @runs = split( /,/, $a );
    print "For reference: last run was $gqlast: $a\n";
    close(A);
    return;
  }
}

sub writeLastRun {
  ( my $gqlast = $gqfile ) =~ s/.txt$/-last.txt/i;
  open( A, ">$gqlast" );
  print A join( ',', @runs );
}

sub readFile {
  my %dupes;
  open( A, $_[0] ) || die("Can't read $_[0]");
  print "Opened $_[0]...\n";
  while ( $a = <A> ) {
    if ( toProj($a) ) {
      @runs = ( toProj($a) );
      continue;
    }
    chomp($a);
    ( my $a2 = $a ) =~ s/[^a-z]//g;
    if ( defined( $dupes{$a2} ) ) {
      print "Line $. of $_[0]: Duplicate $a\n";
      continue;
    }
    $dupes{$a2} = 1;
    @thisAry = split( / /, $a );
    tryAry();
  }
}

sub tryAry {
  if ( $#thisAry > 1 ) {
    print "Too many arguments in @thisAry.\n";
    return;
  }
  tryOneSet();
}

sub toProj {
  if    ( $_[0] =~ /oafs/i )                          { return "oafs"; }
  elsif ( $_[0] =~ /(threed|fourd)/i )                { return "opo"; }
  elsif ( $_[0] =~ /(compound|slicker|buck|past)/i )  { return "as"; }
  elsif ( $_[0] =~ /ailihphilia/i )                   { return "ai"; }
  elsif ( $_[0] =~ /(roiling|shuffling)/i )           { return "sts"; }
  elsif ( $_[0] =~ /(tragic|vvff|vf|vv|very-vile)/i ) { return "tm"; }
  ( my $cproj = $pwd ) =~ s/\.inform.*//;
  $cproj =~ s/.*[\\\/]//;
  return $cproj if ( -f "story.ni" );
  return "";
}

sub use_cases {
  print <<EOT;
DETAILED USE CASES:
ga, gq and gr are batch files for quick use: they correspond to gq.pl as (args), gq.pl (args), gq.pl sts (args).
gr r1 intro will look for "intro" only in Shuffling Around's files. r2 is only roiling.
ga as14 stuff will look for "stuff" only in Problems Compound and Seeker Status and not Slicker City/Buck the Past.
gq wonk/no will look for "wonk no" with spaces
gq as- or gq =as will look for as instead of going to the Alec Smart suite
EOT
  exit;
}

sub usage {
  print <<EOT;
0 = process Roiling name conditionals
-1st/l1 = launch 1st in source
-ll = launch last
-e = open manifest file of which group checks what
-h = show headers
-ha = history of all, -hi = specific history
-p = headers too
-iq/-oq = inside/outside quotes
-n = look through names
-nt = print tabbed
-nd = change default if we don't specify -opo etc
-ft = print untabbed
-t = only in tables tb=only random 1=1st start
-x = run others too e.g. anan and myan
-w = push line numbers to err files
-c = clipboard (invalidates comand line)
-f = use outside file gq-r.txt for input, -f (letter) = use gq-arg.txt
-v = verbose output e.g. tell what we skipped
-mo = maximum to find overall (default=100, 0=no limit)
-mf = maximum to find in file (default=25, 0=no limit)
-mu = unset both maximums above
-hi = open history of specified groups, -ha = open history of all
-sr = show rules, if text shows up in a rule
-z = zap bracketed text
/3d = only look in tables of (for instance) 3d
-? = usage, -?? = use cases
as, opo, sts are the main ones. -a runs all. You can split with 3d,sa if you want. r(1,2) or as(1,2,3,4) also can focus on certain projects.
EOT
  exit;
}
