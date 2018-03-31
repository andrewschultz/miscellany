#gq.pl: stands for "grep quick"
#this shows where certain text I may've already used pops up in Roiling or Shuffling. It pegs them both as Shuffling << Roiling.
#-tb1 = table random, start with that word
#-tb = table random
#-t = table only
#usage
#gq.pl -tb rosco coors (matches both)
#gq.pl -tb rosco (matches one)
#gq.pl -tb1 rosco (matches starting with rosco)
#gq.pl -m 10 yes (matches 1st 10 yes's)
#
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
my $forceNum          = 1;
my $ignoreRand        = 0;
my $inQuotes          = 0;

my %foundCount;

@runs = ( toProj($pwd) ) if toProj($pwd);

while ( $count <= $#ARGV ) {
  $a = $ARGV[$count];
  $b = "";
  if ( defined( $ARGV[ $count + 1 ] ) ) {
    $b = $ARGV[ $count + 1 ];
  }

  for ($a) {
    /^0$/ && do { processNameConditionals(); exit; };
    /^1st$/ && do { $launchFirstSource = 1; $count++; next; };
    /^-?e$/ && do { `$gqfile`; exit; };
    /^\// && do {
      $thisAry[0] =~ s/^\///g;
      $onlyTables = 1;
      $onlyRand   = 1;
      $firstStart = 1;
      $count++;
      next;
    };
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
    /^-?(3d|3|4d|4|opo)$/i
      && do { @runs = ("opo"); $count++; next; };            # 3dop try
    /^(-?(btp|sc|pc|ss)|-as)$/i
      && do { @runs = ("as"); $count++; next; };             # Alec Smart?
    /^-?(r|roi|s|sa|sts)$/i
      && do { @runs = ("sts"); $count++; next; };  # roiling original? (default)
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
    / ^ -?ft$/ && do { $printUntabbed = 0; $count++; next; };
    /^-? zb $/ && do { $zapBrackets   = 1; $count++; next; };
    /^-?mo$/   && do {

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
    /^[\\0-9a-z'\.][\\0-9a-z'\.-]+$/i && do {
      $a =~ s/-$//;    # another way to avoid, say, as instead of AS
      if ( $i7x{$a} ) {
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
        push( @thisAry, $a );
      }
      $count++;
      next;
    };    # if we want to use AS as a word, it would be in upper case
    print "Argument $a failed.\n";
    usage();
  }

}

readLastRun() if ( !( scalar @runs ) );

if ( ( !$thisAry[0] ) && ( !$getClipboard ) ) {
  die("Need a process-able word for an argument.");
}

if ( ( $#runs == -1 ) && ( $#ARGV > 1 ) ) {
  print
    "NOTE: if a project name overlaps a flag, use the comma to detect it.\n";
}

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
    if ($launchFirstSource) {
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
  push( @saveData, $_[0] );
  $saveHash{$q} = 1;

  open( A, $saveFile ) || warn("No save file $saveFile.");
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
  if ($dontrewrite) { return; }
  open( A, ">$saveFile" );
  for (@saveData) {
    print A "$_\n";
  }
  close(A);
  print "Wrote to $saveFile.\n";
}

sub processListFile {
  my $line;
  my $defaultString;
  my $currentLedger;

  open( A, $gqfile ) || die("Can't find $gqfile.");

  while ( $line = <A> ) {
    if ( $line =~ /^#/ ) { next; }
    if ( $line =~ /^;/ ) { last; }
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
  my @x = split( /\n/, $cmds{ $_[0] } );

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
  if ( $#blanks > -1 ) {
    print "FILES WITH NO MATCHES: " . join( ", ", @blanks ) . "\n";
  }
  if ( $#gots > -1 ) {
    print "FILES WITH MATCHES: "
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
  open( A, "$_[0]" ) || die("No $_[0]");
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
    if ( ( $a =~ /^table of / ) && ( $currentTable !~ /megachatter/ ) ) {
      $idx          = -1;
      $currentTable = $a;
      $currentTable =~ s/ *\[.*//g;
      $currentTable =~ s/\t//g;
      chomp($currentTable);
      $inTable = 1;
    }
    if ( $a !~ /[a-z]/i ) {
      $currentTable = "";
      $inTable      = 0;
      if ( !$alwaysImportant ) { $inImportant = 0; $thisImportant = ""; }
    }
    my $crom = cromu( $a, $_[0] );
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
        $lineToOpen = $. if !$lineToOpen;
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

sub processStory {
  my $fileName;
  my $tabrow;

  if ( $_[0] =~ /trizbort/i ) {
    $fileName = $_[0];
  }
  else {
    $shortName = $_[0];
    if ( $_[1] == 1 ) {
      $fileName =
"c:/Program Files (x86)/Inform 7/Inform7/Extensions/Andrew Schultz/$_[0] Random Text.i7x";
    }
    else { $fileName = "c:/games/inform/$_[0].inform/Source/story.ni"; }
  }
  open( A, "$fileName" ) || die("No $fileName.");
  $foundSomething = 0;
  $count          = 0;
  while ( $a = <A> ) {
    chomp($a);
    if ( ( $a =~ /^[a-z].*: *$/i ) || ( $a =~ /^table of / ) ) {
      $myHeader = $a;
      $tabrow   = 0;
      $blurby   = 0;
    }
    if ( $a =~ /^blurb/ ) { $blurby = 1; }
    $count++;
    $tabrow++;
    if ( $a =~ /`/ ) { print "WARNING: Line $count has back-quote!\n$a"; }
    if ( $a =~ /^table of /i ) {
      $a =~ s/ *\[[^\]]*\].*//g;
      $thisTable = "($a) ";
    }
    elsif ( $a !~ /[a-z]/i ) { $thisTable = ""; }
    my $tmp = cromu( $a, $fileName );
    if ($tmp) {
      if ( $a =~ /list of text variable/i ) { processList($a); }
      else {
        if ($showHeaders) {
          if ( $myHeader ne $lastHeader ) {
            print "======================$myHeader\n";
            $lastHeader = $myHeader;
          }
        }
        if ( isPrintable() ) {
          if ( !$foundSomething ) { print "In $fileName:\n"; }
          print "$shortName L$count ";
          $totalFind++;
          if ($thisTable) { my $tr2 = $tabrow - 2; print "/$tr2"; }
          if ($showHeaders) { print ": $a\n"; }
          else {
            print ": $thisTable$a";
            if ( $tmp == 2 ) { print "****PLURAL****"; }
            print "\n";
          }
          if ( $maxOverallFind == $totalFind ) {
            print "Hit the limit.\n";
            last();
          }
          $foundSomething = 1;
        }
      }
    }
  }

  close(A);
  if ( !$foundSomething ) { print "Nothing in $fileName.\n"; }

}

sub isPrintable {
  if ( ($maxOverallFind) && ( $maxOverallFind <= $totalFind ) ) { return 0; }
  if ( !$onlyTables ) { return 1; }
  if ( ($thisTable) && ($blurby) && tabCheck($a) ) {
    return 1 if $onlyRand;
    return 0 if $ignoreRand;
  }
  if ( tabCheck($a) && ($thisTable) && ( !$onlyRand ) ) { return 1; }
  return 0;
}

sub tabCheck {
  if ( ( $_[0] =~ /^\t/ ) && ($printUntabbed) ) { return 1; }
  if ( ( $_[0] !~ /^\t/ ) && ($printTabbed) )   { return 1; }
  return 0;
}

sub processList {
  my $listName = $a;
  $listName =~ s/.is a list of.*//gi;
  my $yep = 0;
  if ( $a =~ /\{/ ) {
    $a =~ s/^[^\"]*.//g;
    $a =~ s/\" *\}.*//g;
    my @b = split( /\", \"/, $a );
    for (@b) {
      my $temp = cromu( $_, "" )
        ;    # lists will never occur in a test file, so we can skip this
      if ($temp) {
        $yep            = 1;
        $foundSomething = 1;
        print "$listName (L$count): $_";
        if ( $temp == 2 ) { print " (PLURAL)"; }
        print "\n";
      }
    }
    return;
  }
  print "$a\n";
  if ( !$yep ) {
    print "$shortName had $ARGV[0]/$ARGV[1] but not in same entry.\n";
  }
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
    @runs = split( /,/, $a );
    print "For reference: last run was $gqlast: $a\n";
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
  if    ( $_[0] =~ /oafs/i )                         { return "oafs"; }
  elsif ( $_[0] =~ /(threed|fourd)/i )               { return "opo"; }
  elsif ( $_[0] =~ /(compound|slicker|buck|past)/i ) { return "as"; }
  elsif ( $_[0] =~ /ailihphilia/i )                  { return "ai"; }
  elsif ( $_[0] =~ /(roiling|shuffling)/i )          { return "sts"; }
}

sub usage {
  print <<EOT;
0 = process Roiling name conditionals
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
-mo = maximum to find overall (default=100, 0=no limit)
-mf = maximum to find in file (default=25, 0=no limit)
-mu = unset both maximums above
-hi = open history of specified groups, -ha = open history of all
-sr = show rules, if text shows up in a rule
-z = zap bracketed text
/3d = only look in tables of 3d (for instance{)
as, opo, sts are the main ones. -a runs all. You can split with 3d,sa if you want.
EOT
  exit;
}
