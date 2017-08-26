############################################################
#gh.pl
#This copies over changed files to the github directory from various sources.
#It uses gh.txt.
#
#commands: gh.pl sts (stale tales slate) or gh.pl e (edit the list file)
#
# gh.pl c opens code, e opens gh.txt, p opens private file

use strict;
use warnings;
use lib "c:/writing/scripts";
use i7;

use File::Compare;
use File::Copy;
use File::Spec;
use File::stat;

##########################
#options
my $warnCanRun = 0;
my $alph       = 1;
my $procString = "";
my $defaultString;
my $testResults         = 0;
my $runTrivialTests     = 0;
my $byFile              = 0;
my $removeTrailingSpace = 0;
my $ignoreTrizbort      = 0;
my $backcopy            = 0;
my $whiteSpaceRun       = 0;
my $executeDontBail     = 0;
my $doPerlTidy          = 1;

my $execLevel = 1;

##########################
#constants
my $gh    = "c:\\users\\andrew\\Documents\\github";
my $ghl   = "c:\\writing\\scripts\\gh-last.txt";
my $ght   = "c:\\writing\\scripts\\gh.txt";
my $ghp   = "c:\\writing\\scripts\\gh-private.txt";
my $ghs   = "c:\\writing\\scripts\\gh.pl";
my $ghreg = "c:\\writing\\scripts\\gh-reg.txt";

###########################
#hashes
my %gws;
my %gwt;
my %repls;
my %repl2;
my %altHash, my %do, my %poss, my %postproc;
my %msgForProj;

#################options
my $executeBackCopy = 0;

my $justPrint   = 0;
my $verbose     = 0;
my $verboseTest = 1;
my $myBase      = "";

my $globalTS       = 0;
my $globalWarnings = 0;
my $globalStrict   = 0;

my $copyAuxiliary = 0;
my $copyBinary    = 0;
my $thisProj;

my $minLines = 0;
my $minFile  = "";

my $ignoreBackwardsTime = 0;
my $timeReverse         = 0;

my @trizFail;

########################
#variables
my $cmdYet   = 0;
my $warnYet  = 0;
my $zeroOkay = 0;

my $reverse = 0;

my $count = 0;

preProcessHashes($ght);
preProcessHashes($ghp);

while ( $count <= $#ARGV ) {
  my $arg = lc( $ARGV[$count] );
  for ($arg) {
    /^gh\.pl/ && do {
      print "############################OOPS! You added the app name.\n";
      $count++;
      next;
    };
    /^-?e?r$/ && do {
      print
"Opening private file, -e opens external .txt file, -c opens code file, -r opens regex file.\n";
      system("start \"\" $np $ghreg");
      exit;
    };
    /^-?e?p$/ && do {
      print
"Opening private file, -e opens external .txt file, -c opens code file, -r opens regex file.\n";
      system("start \"\" $np $ghp");
      exit;
    };
    /^-?e$/ && do {
      print
"Opening external file, -c opens code, -p opens private file, -r opens regex file.\n";
      system("start \"\" $np $ght");
      exit;
    };
    /^-?c$/ && do {
      print
"Opening code, -e opens external .txt file, -p opens private file, -r opens regex file.\n";
      system("start \"\" $np $ghs");
      exit;
    };
    /^-?(ec|ce)$/ && do {
      print "Opening code/external.\n";
      system(
        "start \"\" \"C:\\Program Files (x86)\\Notepad++\\notepad++.exe\"  $ghs"
      );
      system(
        "start \"\" \"C:\\Program Files (x86)\\Notepad++\\notepad++.exe\"  $ght"
      );
      exit;
    };
    /^-?it$/i      && do { $ignoreBackwardsTime = 1;  $count++; next; };
    /^-?tr$/i      && do { $timeReverse         = 1;  $count++; next; };
    /^-?j$/i       && do { $justPrint           = 1;  $count++; next; };
    /^-?f$/i       && do { $byFile              = 1;  $count++; next; };
    /^-?v$/i       && do { $verbose             = 1;  $count++; next; };
    /^-?vt$/i      && do { $verboseTest         = 1;  $count++; next; };
    /^-?nvt$/i     && do { $verboseTest         = 0;  $count++; next; };
    /^-?bc$/i      && do { $executeBackCopy     = 1;  $count++; next; };
    /^-?rt$/i      && do { $runTrivialTests     = 1;  $count++; next; };
    /^-?nrt$/i     && do { $runTrivialTests     = -1; $count++; next; };
    /^-?(tp|pt)$/i && do { $doPerlTidy          = 1;  $count++; next; };
    /^-?(npt|ptn|ntp|tpn)$/i && do { $doPerlTidy = 0; $count++; next; };
    /^-?rts$/i && do { $removeTrailingSpace = 1; $count++; next; };
    /^-?wsr$/i && do { $whiteSpaceRun       = 1; $count++; next; };
    /^-?igt$/i && do { $ignoreTrizbort      = 0; $count++; next; };
    /^-?(sw|ws)(t)?/i && do {
      readReplace();
      strictWarn($ght);
      strictWarn($ghp);
      if ( $a =~ /t/ ) {
        printf(
          "TEST RESULTS: strict-warn,%d,0,0,gh.pl -sw(t),%s\n",
          ( scalar keys %gws ),
          join( "<br />", %gws )
        );
        printf(
          "TEST RESULTS: trailing-space,%d,0,0,gh.pl -rts -sw(t),%s\n",
          ( scalar keys %gwt ),
          join( "<br />", %gwt )
        );
        printf(
          "TEST RESULTS: triz-date-fail,%d,0,0,gh.pl -sw(t),%s\n",
          ( scalar @trizFail ),
          join( "<br />", @trizFail )
        );
      }
      else {
        print
"Total warnings needed $globalWarnings total strict needed $globalStrict total excess tab files $globalTS\n";
        if ($minFile) { print "Shortest file $minFile, $minLines lines.\n"; }
      }
      exit();
    };
    /^-?t$/i && do { $testResults = 1; $count++; next; };
    /^-?all$/i
      && do { $procString = allProjs( "$ght", "$ghp" ); $count++; next; };
    /^-?alb$/i && do { $procString    = allProjs("$ght"); $count++; next; };
    /^-?a$/i   && do { $copyAuxiliary = 1;                $count++; next; };
    /^-?b$/i   && do { $copyBinary    = 1;                $count++; next; };
    /^-?(d|ab|ba)$/i
      && do { $copyBinary = 1; $copyAuxiliary = 1; $count++; next; };
    /^-?reverse$/i && do { $reverse = 1; $count++; next; };
    /^[a-z34]+(=.*)?$/i && do {

      if ( $arg =~ /-$/ ) {
        $arg =~ s/-$//g;
        if   ( $altHash{$arg} ) { $postproc{ $altHash{$arg} } = 0; }
        else                    { $postproc{$arg}             = 0; }
      }    # sc- means you don't run trivials
      if ( $arg =~ /=/ ) {
        my @xtraRun = split( /=/, $arg );
        my $execArgs = defined( $xtraRun[1] ) ? $xtraRun[1] : "";
        if ( $altHash{ $xtraRun[0] } ) {
          $postproc{ $altHash{ $xtraRun[0] } } = 1;
        }
        else { $postproc{ $xtraRun[0] } = 1; }
        if ( $execArgs =~ /x/ ) { $executeDontBail = 1; }
        $execArgs =~ s/x//;
        $execLevel = $execArgs if $execArgs;
        $arg =~ s/=.*//;
      }    # sc= means you do run trivials
      if ( $altHash{$arg} ) {
        print "$arg => $altHash{$arg}\n";
        $procString .= ",$altHash{$arg}";
      }
      else {
        $procString .= ",$arg";
      }
      if ( $msgForProj{$arg} ) {
        print "NOTE for $arg: $msgForProj{$arg}\n";
      }
      $count++;
      next;
    };
    /^-?\?$/   && do { usage(); };
    /^-?\?\?$/ && do { usageDetail(); };
    print "$arg not recognized.\n";
    usage();
  }
}

if ( !$procString ) {
  if ( -f $ghl ) {
    open( A, "$ghl" );
    $procString = <A>;
    chomp($procString);
    close(A);
    print "Using last string from $ghl, **$procString**\n";
  }
  else {
    $procString = $defaultString;
    print "Using default string: $procString\n";
  }
}

$procString =~ s/^,//;

findTerms($ght);
findTerms($ghp);

my @procAry = split( /,/, $procString );

fillProc();

if ($verbose) {
  for my $k ( sort keys %poss ) {
    if ( $k =~ /,/ ) {
      print "$k is a valid key and maps to multiple others.\n";
    }
    else { print "$k is a valid key.\n"; }
  }
}

readReplace();

if ( !processTerms( $ght, $ghp ) ) {
  if ( $byFile && ( $#procAry > -1 ) ) {
    fillProc();
    processTerms( $ght, $ghp );
  }
}

open( A, ">$ghl" );
print A $procAry[$#procAry];

##########################################
#the main function

sub processTerms {
  my @d;
  my $copies       = 0;
  my $unchanged    = 0;
  my $wildcards    = 0;
  my $badFileCount = 0;
  my $didOne       = 0;
  my $uncop        = 0;
  my $badFileList  = "";
  my $outName;
  my $quickCheck   = "";
  my $fileList     = "";
  my $uncopiedList = "";
  my $dirName      = "";
  my $fromBase     = "", my $toBase = "";
  my $fromShort    = "";
  my $maxSize      = 0;
  my $wildSwipes   = 0;
  my $temp;
  my %copto;

  my $xtraCmd;
  my $thisTestPriority = 0;

  for my $thisFile (@_) {
    open( A, $thisFile ) || die("No $thisFile");
    while ( $a = <A> ) {
      my $reverseCopy = 0;
      chomp($a);
      my $b        = $a;
      my $hashProj = $a;
      $hashProj =~ s/=.*//;
      $hashProj =~ s/^[^a-z0-9]*//gi;

      $xtraCmd = "";
      if ( $a =~ /&/ ) {
        $xtraCmd = $a;
        $xtraCmd =~ s/.*&//;
        $a =~ s/&.*//;
      }
      $maxSize = 0;

      if ( $a !~ /[a-z]/ ) { $dirName = ""; }

      if ( $a =~ /^#/ ) { next; }
      if ( $a =~ / sz:/ ) {
        $maxSize = $a;
        $maxSize =~ s/.* sz://g;
        $a =~ s/ sz:.*//g;
      }
      if ( $a =~ /^0/ ) { $a =~ s/^0//; $zeroOkay = 1; }
      else              { $zeroOkay = 0; }

      if ( $a =~ /^[0-9]*?>/ ) {
        $thisTestPriority = 1;
        if ( $a =~ /^[0-9]+/ ) {
          $thisTestPriority = $a;
          $thisTestPriority =~ s/>.*//;
        }
        if ( $thisTestPriority > $execLevel ) {
          $a =~ s/^.*?=//;
          print
"SKIPPING TEST COMMAND $a, priority is execLevel is $execLevel and needs to be $thisTestPriority.\n";
          next;
        }
        if ( $runTrivialTests == -1 ) { $warnCanRun = 1; next; }
        $b =~ s/^>//g;
        $b =~ s/=.*//g;
        if ( !hasHash($hashProj) ) { next; }
        if ( ( $runTrivialTests == 1 )
          || ( $postproc{$b} )
          ) # this is about running commands. Now the loop below should hit the FROMBASE= etc first
        {
          $b = $a;
          $b =~ s/.*=//g;
          $b = rehash($b);
          if ( $copies && !$warnYet ) {
            print
"WARNING: you are copying over before running modifying scripts.\n";
            $warnYet = 1;
          }
          if ($verboseTest) { $quickCheck .= "test command>>>>>$a\n"; }
          $quickCheck .= `$b`;
          $cmdYet = 1;
        }
        else { $warnCanRun = 1; next; }
        next;
      }

      if ( $a =~ / *< */ ) {
        if ( !hasHash($hashProj) ) { next; }
        $a =~ s/^[^=]*.//;
        my @timeArray = split( / *< */, rehash($a) );
        if ( $#timeArray != 1 ) { print("Bad split in line $.: $a\n"); next; }
        if ( !-f $timeArray[0] ) { die("$timeArray[0] is not a valid file."); }
        if ( !-f $timeArray[1] ) { die("$timeArray[1] is not a valid file."); }
        if ( stat( $timeArray[0] )->mtime > stat( $timeArray[1] )->mtime ) {
          if ( $executeDontBail && $xtraCmd ) {
            print
              "$timeArray[0]/$timeArray[1] are in the wrong order in time.\n";
            print
              "Running extra command $xtraCmd to set timestamps straight.\n";
            `$xtraCmd`;
          }
          else {
            die(
"$timeArray[0] has timestamp after $timeArray[1], which is a fatal build error"
                . (
                $xtraCmd ? " (try running $xtraCmd or adding =x to skip)" : ""
                )
            );
          }
        }
        next;
      }
      if ( $a =~ / *> */ ) {
        if ( !hasHash($hashProj) ) { next; }
        $a =~ s/^[^=]*.//;
        my @timeArray = split( / *> */, rehash($a) );
        if ( $#timeArray != 1 ) { print("Bad split in line $.: $a\n"); next; }
        if ( !-f $timeArray[0] ) { die("$timeArray[0] is not a valid file."); }
        if ( !-f $timeArray[1] ) { die("$timeArray[1] is not a valid file."); }
        if ( stat( $timeArray[0] )->mtime < stat( $timeArray[1] )->mtime ) {
          if ( $executeDontBail && $xtraCmd ) {
            print
              "$timeArray[0]/$timeArray[1] are in the wrong order in time.\n";
            print
              "Running extra command $xtraCmd to set timestamps straight.\n";
            `$xtraCmd`;
          }
          else {
            die(
"$timeArray[0] has timestamp before $timeArray[1], which is a fatal build error"
                . (
                $xtraCmd ? " (try running $xtraCmd or adding =x to skip)" : ""
                )
            );
          }
        }
        next;
      }
      ##################note prefix like -a (auxiliary) and -b (build)
      #this is because auxiliary or binary files could be quite large
      #format is -a:
      #-b:
      my $prefix = "";
      my $c      = $a;
      if ( $c =~ /^-.:/ ) {
        $c =~ s/(^..).*/$1/g;
        $prefix = $c;
        $b =~ s/^-.://g;
      }
      if ( $a =~ /FROMBASE=/ ) {
        $temp = $a;
        $temp =~ s/^FROMBASE=//g;
        $repl2{"fromBase"} = $temp;
      }
      if ( $a =~ /TOBASE=/ ) {
        $temp = $a;
        $temp =~ s/^TOBASE=//g;
        $repl2{"fromShort"} = $repl2{"toBase"} = $temp;
      }
      if ( $a =~ /FROMSHORT=/ ) {
        $temp = $a;
        $temp =~ s/^FROMSHORT=//g;
        $repl2{"fromShort"} = $temp;
      }
      if ( $a =~ /POSTPROC=/i ) {
        $a =~ s/^POSTPROC=//g;
        my @as = split( /,/, $a );
        for (@as) { $postproc{$_} = 1; }
      }

      $b =~ s/=.*//g;
      $thisProj = $b;
      if ( hasHash($b) ) {

        $didOne = 1;
        my $wc = "";
        my $c  = $a;
        $c =~ s/.*=//g;

        #print "Before $c\n";
        $c = rehash($c);

        #print "After $c\n";

        @d = split( /,/, $c );
        if ( $#d == 0 ) { push( @d, "" ); }
        my $fromFile = $d[0];
        my $toFile   = $d[1];
        my $short    = $fromFile;
        $short =~ s/.*[\\\/]//g;

        if ( $fromFile !~ /:/ ) { $fromFile = "$repl2{fromBase}\\$fromFile"; }
        if ( $repl2{"toBase"} ) {
          $toFile = "$repl2{toBase}";
          if ( defined( $d[1] ) && $d[1] ) { $toFile .= "\\$d[1]"; }
        }

        if ( ( !-f $fromFile ) && ( $fromFile !~ /\*/ ) ) {
          if ( -f $toFile ) {
            print "BACKCOPY: copy \"$toFile\" \"$fromFile\"\n";
            $backcopy++;
            next;
          }
          print "Oops $fromFile can't be found.\n";
          $badFileList .= "($.) $fromFile\n";
          $badFileCount++;
          next;
        }

        if ($toFile) { $dirName = $toFile; }
        elsif ( !$dirName ) {
          die("Need dir name to start a block of files to copy.");
        }
        else {
          print "$fromFile has no associated directory, using $dirName\n";
        }

        if ( -d "$gh\\$toFile" ) { $outName = "$gh\\$toFile\\$short"; }
        else {
          $outName = "$gh\\$toFile";
          my $outShort = $outName;
          $outShort =~ s/.*[\\\/]//;
          if ( $outShort =~ /\./ ) {
            $short = $outShort;
            $toFile =~ s/[^\\\/]+$//;
          }
        }
        if ( -f $fromFile && ( -s $fromFile == 0 ) ) {
          die(
"Uh oh. I found a 0 byte file: $fromFile\n\nI am bailing immediately, because this should never happen. It may've been deleted, so you'll need to pull it back up with git revert or something."
          ) if !$zeroOkay && shouldRun($a);
        }
        if ($whiteSpaceRun) {
          if ( $fromFile =~ /\*/ ) {
            my @fileList = glob($fromFile);
            for (@fileList) {
              checkWarnings( $_, 1 ) if -f $_ && shouldCheck($_);
            }
          }
          else {
            checkWarnings( $fromFile, 1 ) if shouldCheck($fromFile);
          }
          next;
        }
        if ( compare( $fromFile, "$outName" ) ) {
          if ( ($maxSize) && ( -s $fromFile > $maxSize ) ) {
            print "Oops $fromFile size is above $maxSize.\n";
            $badFileList .= "($.) (too big) $fromFile\n";
            $badFileCount++;
            next;
          }
          my $thisWild = 0;
          my $cmd      = "copy \"$fromFile\" \"$gh\\$toFile\"";
          if ( ( $copto{$toFile} ) && ( !-d "$gh\\$toFile" ) ) {
            print
"Warning! Copying two different files to the same location $gh\\$toFile (next is $fromFile). Check gh*.txt or create a directory.\n";
          }
          $copto{$toFile}++;
          if ($reverse) {
            if ( $short =~ /\*/ ) { next; }
            $cmd = "copy \"$gh\\$toFile\\$short\" \"$fromFile\"";
          }
          if ( $fromFile =~ /\*/ ) {
            my $ctemp = $c;
            $ctemp =~ s/,[a-z0-9-\\\/]*$//;
            my @fileList = glob($ctemp);
            if ( !( scalar @fileList ) ) {
              print "No matches for $ctemp.\n";
              next;
            }

            my $wild = $ctemp;
            $wild =~ s/.*[\\\/]//;
            my @fileList2 = glob "$gh\\$toFile\\$wild";
            my $ctempdir  = $ctemp;
            $ctempdir =~ s/[\\\/][^\\\/]*$//;

            for (@fileList2) {
              my ( $vol, $dir, $file ) = File::Spec->splitpath($_);
              if ( !-f "$ctempdir\\$file" ) {
                if ( wcBackcopy($file) ) {
                  if ($executeBackCopy) {
                    copy( "$_", "$ctempdir\\$file" );
                    print("$_ copied backwards to $ctempdir\\$file.\n");
                  }
                  else {
                    print(
                      "BACKCOPY (WILDCARD): copy \"$_\" \"$ctempdir\\$file\"\n"
                    );
                  }
                  $backcopy++;
                }
              }
            }

            $wildSwipes++;
            for (@fileList) {
              my ( $vol, $dir, $file ) = File::Spec->splitpath($_);
              if ( compare( "$_", "$gh\\$toFile\\$file" ) ) {
                if ( shouldCheck($_) ) {
                  checkWarnings( $_, 1 );
                }
                copy( "$_", "$gh\\$toFile\\$file" )
                  || die("Copy $_ to $gh\\$toFile\\$file failed");
                $fileList .= "$_\n";

#if ($cmdYet && !$warnYet) { print "You have run a command after copying files. This may make you have to run gh again.\n"; $warnYet = 1; }
                $wildcards++;
                $copies++;
              }
            }
            next;
          }
          if ($justPrint) { print "$cmd\n"; $fileList .= "$fromFile\n"; }
          else {
            if ( shouldCheck($fromFile) ) {
              checkWarnings( $fromFile, 1 );
            }
            if ( $fromFile =~ /\.trizbort$/ ) {
              trizCheck( $fromFile, 1, $xtraCmd );
            }
            if ( shouldRun($prefix) ) {

              #die "$fromFile to $gh\\$toFile\\$short";
              my $fileTo = "$gh\\$toFile\\$short";
              if ( -f $fileTo ) {
                if ( !-f $fromFile ) {
                  print "BACKCOPY: copy \"$fromFile\" \"$fileTo\"\n";
                }
                my $infoTo   = stat($fileTo);
                my $infoFrom = stat($fromFile);
                my $retMode  = $infoTo->mode & 0777;
                my $retMask  = $retMode & 0222;

                $reverseCopy = 0;

                if ( $infoTo->mtime > $infoFrom->mtime ) {
                  if ( !$ignoreBackwardsTime && !$timeReverse ) {
                    print(
"$fromFile is before $fileTo, skipping. Use -it to overlook this, -tr to reverse copy.\n"
                    );
                    next;
                  }
                  elsif ($timeReverse) {
                    $reverseCopy = 1;
                  }
                }
                if ( $retMask != 0222 ) {
                  chmod 0777, $fileTo;
                }
                copy( "$fromFile", "$gh\\$toFile\\$short" )
                  || die("Couldn't copy $fromFile to $gh\\$toFile\\$short")
                  if !$reverseCopy;
                copy( "$gh\\$toFile\\$short", "$fromFile" )
                  || die("Couldn't copy $gh\\$toFile\\$short to $fromFile")
                  if $reverseCopy;
                $fileList .=
                  "$fromFile" . ( $reverseCopy ? " (reversed)" : "" ) . "\n";

                if ( $retMask != 0222 ) {
                  chmod $retMode, $fileTo;
                }
              }
              else {
                copy( "$fromFile", "$gh\\$toFile\\$short" )
                  || die("Couldn't copy $fromFile to $gh\\$toFile\\$short");
              }
              if ( !$thisWild ) { $copies++; }
            }
            else {
              print "$cmd not run, need to set $prefix flags.\n";
              $uncopiedList .= "$fromFile\n";
              $uncop++;
            }
          }
        }
        else {
          $unchanged++;
        }

        #      `$cmd`;
      }
    }
    close(A);
  }
  if ( !$didOne ) {
    my $q = join( "/", @procAry );
    @procAry = checkForFile( $ght, $ghp );
    if ( $#procAry == -1 ) { print "Nothing found for $q.\n"; exit(); }
  }
  else {
    print
"Copied $copies file(s), $wildcards/$wildSwipes wild cards, $unchanged unchanged, $badFileCount bad files, $uncop uncopied files.\n";
    print "Also, "
      . ( $executeBackCopy ? "back-copied" : "use -bc to back-copy" )
      . " $backcopy file(s).\n"
      if ($backcopy);
    my $cbf = $copies + $badFileCount;
    my $proc2 = join( "/", split( /,/, $procString ) );
    if ( $testResults && $cbf ) {
      $fileList =~ s/\n/<br \/>/g;
      print
"TEST RESULTS:$proc2 file-copies,orange,$cbf,0,gh.pl $procString<br>$fileList\n";
    }
    if ($fileList)     { print "====FILE LIST:\n$fileList"; }
    if ($uncopiedList) { print "====UNCOPIED FILES ($uncop):\n$uncopiedList"; }
    if ($badFileCount) { print "====BAD FILES ($badFileCount):\n$badFileList"; }
  }
  if ($quickCheck) {
    printf( "\n========quick verifications%s\n$quickCheck",
      $verboseTest ? "" : " (-vt to show verbose)" );
  }
  if ($warnCanRun) {
    print "\nYou could have run code checking by tacking on an =.";
  }
  return $didOne;
}

##########################
# finds all valid terms in gh.txt or gh-private.txt
# not individual files, just pc, sa, etc

sub findTerms {
  open( A, $_[0] ) || die("Oops, couldn't open $_[0].");

  while ( $a = <A> ) {
    chomp($a);
    if ( $a =~ /~/ )      { next; }    #congruency
    if ( $a =~ /^d:/ )    { next; }    #default
    if ( $a =~ /^;/ )     { last; }
    if ( $a =~ /^#/ )     { next; }
    if ( $a !~ /[a-z]/i ) { next; }
    $a =~ s/=.*//g;
    $poss{$a} = 1;
  }

  close(A);
}

sub readReplace {
  my $line;
  open( A, $ghreg ) || die("Can't open regular expression replacement file.");
  while ( $line = <A> ) {
    if ( $line =~ /^;/ ) { last; }
    chomp($line);
    my @lines = split( /\t/, $line );
    $repls{ $lines[0] } = $lines[1];
  }
  close(A);
}

###############################
# this finds similarities e.g. pc~tpc

sub preProcessHashes {
  my $bail = 0;
  open( A, "$_[0]" ) || die("Can't open $_[0].");
  while ( $a = <A> ) {
    chomp($a);
    if ( $a =~ /^d:/ ) {
      $defaultString = $a;
      $defaultString =~ s/^d://gi;
    }
    if ( $a =~ /^MSG:/ ) {
      $a =~ s/^MSG://;
      my @ary  = split( /=/, $a );
      my @ary2 = split( /,/, $ary[0] );
      for (@ary2) {
        $msgForProj{$_} = $ary[1];
      }
      next;
    }
    if ( $a =~ /~/ ) {
      my @b = split( /~/, $a );
      my @c = split( /,/, $b[0] );
      for (@c) {
        if ( $altHash{$_} ) {
          print "$_ has duplicate hash: was $altHash{$_}, also found $b[1].\n";
          $bail = 1;
        }
        $altHash{$_} = $b[1];
      }

      #print "@b[0] -> @b[1]\n";
    }
  }
  close(A);
  if ( $bail > 0 ) { print "Fix duplicate hashes before continuing.\n"; exit; }
}

sub shouldRun {
  if ( ( $_[0] =~ /^-a/ ) && ($copyAuxiliary) ) { return 1; }
  if ( ( $_[0] =~ /^-b/ ) && ($copyBinary) )    { return 1; }
  if ( $_[0] eq "" ) { return 1; }
  return 0;
}

sub hasHash {
  if ( $do{ $_[0] } ) { return 1; }
  if ( ( $altHash{ $_[0] } ) && ( $do{ $altHash{ $_[0] } } ) ) { return 1; }
  return 0;
}

sub checkForFile {
  my $line;
  my @mb;
  my @mb2;
  my $curProj = "";
  my $last    = "";
  for my $thisfi (@_) {
    open( A, "$thisfi" );
    while ( $line = <A> ) {
      if ( $line =~ /\b$procString\b/ ) {
        chomp($line);
        push( @mb, $line );
        $last    = $line;
        $curProj = $last;
        $curProj =~ s/=.*//;
        if ( $curProj ne $last ) { push( @mb2, $curProj ); }
        $last = $curProj;
      }
    }
    close(A);
  }
  if ( ( $byFile == 1 ) && ( $#mb >= 0 ) ) {
    return @mb2;
    exit();
  }
  if ( $#mb >= 0 ) {
    print
"No project found, but there are close matches you may be able to run with -f:\n"
      . join( "\n", @mb ) . "\n";
    exit();
  }
  return ();
}

sub fillProc {
  my $stillChange = 1;
  my $d;

  for (@procAry) {
    $do{$_} = 1;
    if ( $_ eq "-a" ) { $alph = 1; }
  }
  while ($stillChange) {
    $stillChange = 0;
    for $d ( keys %do ) {
      if ( $altHash{$d} ) {

        #print "$d => $altHash{$d}\n";
        if ( $altHash{$d} !~ /,/ ) {
          if ( !defined( $do{ $altHash{$d} } ) ) { $stillChange = 1; }
          $do{ $altHash{$d} } = 1;
        }
        else {
          my @alts = split( /,/, $altHash{$d} );
          for my $al (@alts) {
            if ( !defined( $do{ $altHash{$al} } ) ) { $stillChange = 1; }
            $do{ $altHash{$al} } = 1;
          }
        }
      }
    }
  }
  for $d ( keys %do ) {
    if ( $d =~ /,/ ) { delete( $do{$d} ); print "Deleted $d\n"; }
    elsif ( $altHash{$d} ) {
      delete( $do{$d} );

      #print "Zapped reference $d\n";
    }
    else { print "Running $d\n"; }
  }
}

sub strictWarn {
  my $temp;
  open( A, "$_[0]" ) || die;
  my $line;
  while ( $line = <A> ) {
    chomp($line);
    if ( $line =~ /FROMBASE=/ ) {
      $temp = $line;
      $temp =~ s/^FROMBASE=//g;
      $repl2{"fromBase"} = $temp;
      next;
    }
    if ( $line =~ /TOBASE=/ ) {
      $temp = $line;
      $temp =~ s/^TOBASE=//g;
      $repl2{"fromShort"} = $repl2{"toBase"} = $temp;
      next;
    }
    if ( $line =~ /FROMSHORT=/ ) {
      $temp = $line;
      $temp =~ s/^FROMSHORT=//g;
      $repl2{"fromShort"} = $temp;
      next;
    }
    if ( $line !~ /=/ )     { next; }
    if ( $line =~ /^[>#]/ ) { next; }
    $thisProj = $line;
    $thisProj =~ s/=.*//;
    $line =~ s/.*=//;
    $line =~ s/,.*//;
    $line = rehash($line);

    if ( $line !~ /^c:/ ) {
      $line = $repl2{"fromBase"} . "\\$line";

      #print "$line\n";
    }
    if ( $line =~ /\.trizbort$/ ) {
      trizCheck( $line, 0, "" );
    }
    if ( shouldCheck($line) ) { checkWarnings( $line, 0 ); }
  }
  close(A);
}

###############file name, force remove trailing space
sub checkWarnings {
  my $gotWarnings   = 0;
  my $gotStrict     = 0;
  my $trailingSpace = 0;
  my $spaceThenTab  = 0;
  my $numLines;

  my $line2;

  #print "Warning-checking $_[0]\n";
  open( B, $_[0] ) || do { print "No $_[0], returning.\n"; return; };

  while ( $line2 = <B> ) {
    chomp($line2);
    if ( $line2 =~ /[\t ]+$/ )       { $trailingSpace++; }
    if ( $line2 =~ /^ +\t/ )         { $spaceThenTab++; }
    if ( $line2 eq "use warnings;" ) { $gotWarnings++; }
    if ( $line2 eq "use strict;" )   { $gotStrict++; }
  }
  $numLines = $.;
  close(B);

  if ( ( $removeTrailingSpace || $_[1] ) && ( $trailingSpace > 0 ) ) {
    print "$trailingSpace line(s) with trailing space(s) in $_[0].\n";
    $globalTS++;
  }
  if ( $_[0] =~ /\.pl$/i ) {
    if ($doPerlTidy) {
      print "Tidying $_[0]\n";
      system("perltidy -i=2 $_[0]");
      if ( ( -f "$_[0].tdy" )
        && ( -s "$_[0].tdy" > 0 )
        && ( compare( $_[0], "$_[0].tdy" ) ) )
      {
        copy( "$_[0].tdy", "$_[0]" );
      }
      else {
        print "PERLTIDY failed.";
      }
    }
    if ( !$gotStrict && $gotWarnings ) {
      print "Need strict in $_[0] ($numLines), project $thisProj\n";
      $globalStrict++;
    }
    if ( !$gotWarnings && $gotStrict ) {
      print "Need warnings in $_[0] ($numLines), project $thisProj\n";
      $globalWarnings++;
    }
    if ( !$gotWarnings && !$gotStrict ) {
      print "Need warnings/strict in $_[0] ($numLines), project $thisProj\n";
      $globalWarnings++;
      $globalStrict++;
    }
    if ( !$gotStrict || !$gotWarnings ) {
      $gws{ $_[0] } = 1;
      if ( ( !$minLines ) || ( $numLines < $minLines ) ) {
        $minFile  = $_[0];
        $minLines = $numLines;
      }
      elsif ( $numLines == $minLines ) {
        $minFile .= ", $_[0]";
      }
    }
  }
  if ( $trailingSpace || $spaceThenTab ) {
    $gwt{ $_[0] } = 1;
    if ( $removeTrailingSpace || $_[1] ) {
      my $tempfile = "c:\\writing\\scripts\\temp-perl.temp";
      my $origFile;
      my $strippedFile;
      my $isWin = openWinOrUnix( $origFile, "$_[0]" );

      open( $strippedFile, ">", $tempfile )
        || do { print "Can't write to $tempfile.\n"; close($origFile); return; };

      if ( !$isWin ) { binmode($strippedFile); }
      my $l;
      while ( $l = <$origFile> ) {
        $l =~ s/[ \t]+(\r)?$//g;
        $l =~ s/^ +\t/\t/g;
        print $strippedFile $l;
      }
      close($origFile);
      close($strippedFile);
      if ( compare( $tempfile, $_[0] )
        )    # probably not necessary, but just to check...
      {
        my $cmd = "copy \"$tempfile\" \"$_[0]\"";
        copy( "$tempfile", "$_[0]" );
      }
      delete( $gwt{ $_[0] } );

      #die("copy \"$tempfile\" \"$_[0]\"");
    }
  }
}

sub rehash {
  my $temp = $_[0];
  for my $repl ( sort keys %repls ) {

    #print "$repl $repls{$repl}\n";
    $temp =~ s/\$$repl/$repls{$repl}/g;
  }
  for my $repl ( sort keys %repl2 ) {

    #print "$repl $repl2{$repl}\n";
    $temp =~ s/\$$repl/$repl2{$repl}/g;
  }
  if ( $temp =~ /\$/ ) {
    print "WARNING $_[0] -> $temp still has \$ in it.\n";
  }
  return $temp;
}

sub shouldCheck {
  if ( $_[0] =~ /\.(pl|pm|py|txt|c|md|ni|cpp|ahs|nmr)$/i ) { return 1; }
  return 0;
}

sub trizCheck {
  my $pdf = $_[0];

  $pdf =~ s/trizbort$/pdf/;
  if ( !-f $pdf ) { return; }

  #printf("$_[0] %d %d\n", stat($pdf)->mtime, stat($_[0])->mtime);
  if ( stat($pdf)->mtime < stat( $_[0] )->mtime ) {
    my $delta = stat("$_[0]")->mtime - stat($pdf)->mtime;
    print(
"Oops! Latest $_[0] may not have been saved to PDF--$delta seconds ahead.\n"
    );
    if ( $_[2] ) { print "Recommended command: $_[2]\n"; }
    if ( $_[1] && !$ignoreTrizbort ) {
      die("Bombing out. Set -it to ignore trizbort fails.");
    }
    push( @trizFail, $_[0] );
  }
}

sub allProjs {
  my %projHash;

  for (@_) {
    open( A, $_ );
    while ( $a = <A> ) {
      if ( $a =~ /^[0-9a-z]+=/ ) {
        $a =~ s/=.*//;
        chomp($a);
        $projHash{$a} = 1;
      }
    }
    close(A);
  }
  return join( ",", keys %projHash );
}

sub wcBackcopy {
  my $short = $_[0];
  $short =~ s/.*[\\\/]//;
  return 1 if ( $short =~ /release.*notes/ );
  return 1 if ( $short =~ /reg-*.txt/ );
  return 0;
}

sub usageDetail {
  print <<EOT;
========USAGE DETAIL
-bc = executeBackCopy
-rt / -nrt = (don't) run trivial tests
-rts = remove trailing space (now default)
-wsr = whitespace run (only removes whitespace in the project)
-igt = ignore Trizbort
-pt/tp = forces PerlTidy for *.pl/*.pm, n added unforces it
EOT
  exit();
}

sub usage {
  print <<EOT;
========USAGE
-e edits gh.txt
-(e)c edits gh.pl
-(e)p edits private file
-(e)r edits regex file
-v = verbose output
-vt/nvt = verbose/not verbose test
-rt/-nrt = flag running trivial tests
-j = just print commands instead of executing
-t = print various test results
-a = copy auxiliary files, -d = copy binary files, -d/ab/ba = -a + -b (eg both)
-f doesn't look for a whole project but rather for a specific file, then runs that project
-sw/ws = search for need strict/warnings, -t = test, -it = ignore trizbort fails
Putting = after a command runs tests
-it ignores timestamps being wrong (to < from) and -tr copies (from) to (to)
-? = this
-?? = detailed commands
EOT
  exit();
}
