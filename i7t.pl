#############################################
#i7t.pl
#reads in i7 source and sees all the tables
#and potentially matches them up with release notes
#determined by a log file i7t.txt
#i7t.pl -s pc
#or run it in a directory with story.ni
#
#now you can launch writing with -w

use POSIX qw/getcwd/;
use Win32;

use strict;
use warnings;

my $newDir  = ".";
my $project = "Project";

#######################################varaiables
my @popupLines  = ();
my $popupString = "";
my $sum         = "";
my $tables      = 0;
my $count       = 0;
my $curTable    = "";
my @important   = ();
my $majorTable  = 0;
my $tableList   = "";
my $noAct       = 0;
my $actLog      = "";
my $testCount   = 0;

my $tabfile     = "c:/writing/scripts/i7t.txt";
my $tabfilepriv = "c:/writing/scripts/i7tp.txt";

my %xtraFiles;

###################hashes for verifying source
my %optActivate;
my %notFound;
my %tableName;
my %readFileName;
my %regex;
my %regexMod;
my %delta;
my %dataFiles;
my %minRows;

###################duplicate detector hashes
my %tableDup;
my %extraRows;
my %ignoreDup;
my %ignoreBlankCols;

my @tableReadFiles = ( $tabfile, $tabfilepriv );

my @filesToRead = ();

################################
# options
my $tableTab       = 0;    # this lists how many tables have how many tabs
my $printSuccesses = 0;
my $quietTables    = 1;
my $openTableFile  = 0;
my $openPost       = 0;
my $maxString      = 0;
my $spawnPopup     = 0;
my $verbose        = 0;
my $writeRight     = 0;
my $superVerbose   = 0;

my %rows;
my %falseRows;
my %trueRows;
my %smartIdeas;
my %exp;
my %failCmd;

my %filesToOpen;
my %doubleErr;

my @tableCount = ();

################very bad hard coding but it will have to do for now

$exp{"3d"}  = "threediopolis";
$exp{"4d"}  = "fourdiopolis";
$exp{"pc"}  = "compound";
$exp{"sc"}  = "slicker-city";
$exp{"btp"} = "buck-the-past";
$exp{"bs"}  = "btp-st";
$exp{"r"}   = "roiling";
$exp{"sa"}  = "shuffling";
$exp{"sts"} = "stale-tales-slate";

my $countMismatch = 0;
my $writeDir      = "c:\\writing\\dict";

if ( getcwd() =~ /\.inform/ ) {
  $project = getcwd();
  $project =~ s/\.inform.*//g;
  $project =~ s/.*[\\\/]//g;
  $project = lc($project);
}

my $fileName;

OUTER:
while ( $count <= $#ARGV ) {
  my $arg = $ARGV[$count];
  $b = $ARGV[ $count + 1 ];
  for ($arg) {
    /^-?tt$/ && do { $tableTab = 1; $count++; next; };
    /^-?t$/ && do {
      $b = $ARGV[ $count + 1 ];
      my $important = split( /,/, $b );
      $count += 2;
      next;
    };
    /^-?c$/ && do {
      print
        "Opening source. -e opens the data file, -ec/ce both, -pr private.\n";
      system(
"start \"\" \"C:\\Program Files\\Notepad++\\notepad++.exe\" c:\\writing\\scripts\\i7t.pl"
      );
      exit;
    };
    /^-?e$/ && do {
      print
        "Opening data file. -c opens the source, -ec/ce both, -pr private.\n";
      `$tabfile`;
      exit;
    };
    /^-?(ec|ce)$/ && do {
      print "Opening data and source.\n";
      `c:\\writing\\scripts\\i7t.txt`;
      `c:\\writing\\scripts\\i7t.pl`;
      next;
    };
    /^-?pr$/ && do {
      print
        "Opening private file. -e opens the source, -ef both. -p private.\n";
      `$tabfilepriv`;
      exit;
    };
    /^-?i$/ && do { @important = split( /,/, $b ); $count += 2; next; };
    /^-?sp$/ && do { $spawnPopup     = 1; $count++; next; };
    /^-?ps$/ && do { $printSuccesses = 1; $count++; next; };
    /^-?q$/  && do { $quietTables    = 1; $count++; next; };
    /^-?tl$/ && do { $quietTables    = 0; $count++; next; };
    /^-?v$/  && do { $verbose        = 1; $count++; next; };
    /^-?(vs|sv)$/ && do { $superVerbose = $verbose = 1; $count++; next; };
    /^-?w$/  && do { $writeRight    = 1; $count++; next; };
    /^-?o$/  && do { $openPost      = 1; $count++; next; };
    /^-?ot$/ && do { $openTableFile = 1; $count++; next; };
    /^-?rar$/
      && do { $maxString = 1; $tableTab = 1; $fileName = ""; $count++; next; };
    /^-?\.$/ && do { $writeDir = "."; $count++; next; };
    /^-?[ps]$/ && do {
      $project = $b;
      $newDir  = "c:/games/inform/$project.inform/Source";
      $count += 2;
      if ( $exp{$project} ) {
        print "Found brief project, so changing $project to $exp{$project}.\n";
        $project = $exp{$project};
      }
      next;
    };
    /[\\\/]/ && do { $newDir = $arg; $count++; next; };
    for ( sort keys %exp )    #catch for if we forget -p/-s
    {
      if ( lc($arg) eq $_ ) {
        $project = lc( $exp{$arg} );
        $count++;
        next OUTER;
      }
      if ( defined( $exp{$_} ) && ( lc($arg) eq $exp{$_} ) ) {
        $project = lc($arg);
        $count++;
        next OUTER;
      }
    }
    usage();
  }
}

#####first we find all extra files
for (@tableReadFiles) {
  processInitData($_);
}

my $tableFile = "$writeDir\\tables-$project.i7";
open( B, ">$tableFile" );
close(B);

my $sourceFile;

if ( !defined( $projFiles{$project} ) ) {
  die("No project defined for $project.\n");
}

my @sourceFileList = @{ $projFiles{$project} };

my $tableShort;
my $table        = 0;
my $majorList    = "";
my $tableRow     = 0;
my $falseRow     = 0;
my $trueRow      = 0;
my $smartIdea    = 0;
my $thisTableRow = 0;

my $dupFail = 0;
my $dupLog  = "";

for $sourceFile (@sourceFileList) {

  print "Reading $sourceFile...\n";
  open( A, "$sourceFile" ) || die("$sourceFile in $project doesn't exist.");
  open( B, ">>$tableFile" );

  while ( $a = <A> ) {
    if (
      $a =~ /^(\[)?table / )  #we want to be able to make a fake table if we can
    {
      my $aorig = $a;
      @tableCount = ();
      if ( $curTable && ( !$ignoreDup{$curTable} ) ) {
        my @tempAry = split( /\t/, $a );
        my $unique = $tempAry[0];
        if ( $extraRows{$curTable} ) {
          if ( $#tempAry < $extraRows{$curTable} - 1 ) {
            print
"Warning: may be ignoring too many rows in $curTable, line $.: @tempAry\n";
            $extraRows{$curTable} = $#tempAry + 1;
          }
          $unique = join( "/", @tempAry[ 0 .. $extraRows{$curTable} - 1 ] );
        }
        if ( $tableDup{$curTable}{$unique} ) {
          print
"Duplicate at line $.: $curTable/$unique also at $tableDup{$curTable}{$unique}\n";
          $dupLog .= "$unique/$tableDup{$curTable}{$unique}<br />";
          $dupFail++;
        }
        $tableDup{$curTable}{$unique} = $.;
      }
      if ( $a =~ /^\[/ ) {
        $a =~ s/[\[\]]//g;

        #commented out for a non-table in BTP
        #print "--$a";
      }
      $a =~ s/ \(continued\).*?\[/ \[/g;

      #if ($aorig =~ /continued/) { print "#####################$a"; }
      $a =~ s/^\[//g;
      $table = 1;
      $tables++;
      $curTable = $a;
      chomp($curTable);
      $tableShort = $curTable;
      $curTable =~ s/ *\[.*//g;
      $falseRow = $trueRow = $smartIdea = 0;
      $curTable =~ s/ - .*//g;

      if ( $tableShort =~ /\[x/ ) {
        $tableShort =~ s/.*\[x/x/g;
        $tableShort =~ s/\]//g;
      }
      if ( $tableShort =~ / \[/ ) { $tableShort =~ s/ \[.*//g; }
      $tableShort =~ s/ - .*//g;
      $tableShort =~ s/ *\(continued\)//;
      for my $x (@important) {
        if ( $a =~ /\b$x\b/i ) { $majorTable = 1; }
      }
      $tableRow = 0;
      if ( $aorig =~ /^\[table/ ) {
        $thisTableRow = 0;
      }
      else {
        $a = <A>;
        $thisTableRow = ( scalar split( /\t+/, $a ) );
        print("WARNING 2 tabs in a row in line $.: $a") if ( $a =~ /\t\t/ );
      }
      next;
    }
    if ( $table && ( $a =~ /^\[/ ) ) { next; }
    if ( $a !~ /[a-z]/ ) {
      if ( !$table ) { next; }
      $table = 0;
      if ($tableTab) {
        print "$tableShort: ";
        for ( 0 .. $#tableCount ) {
          if ( $tableCount[$_] ) { print "$_ tabs: $tableCount[$_] "; }
        }
        print "\n";
        if ( ($maxString)
          && ( $#tableCount >= 1 )
          && defined( $tableCount[ $#tableCount - 1 ] )
          && ( $tableCount[$#tableCount] < $tableCount[ $#tableCount - 1 ] ) )
        {
          print "Max string: $maxString";
        }
      }
      if ( !$quietTables ) {
        $tableList .= "$curTable";
        if ( $curTable ne $tableShort ) { $tableList .= "($tableShort)"; }
        $tableList .= ": $tableRow rows\n";
      }

#if ($rows{$tableShort}) { print "Tacking on $tableRow to $tableShort, up from $rows{$tableShort}.\n"; }
      $smartIdeas{$tableShort} += $smartIdea;
      $rows{$tableShort}       += $tableRow;
      $falseRows{$tableShort}  += $falseRow;
      $trueRows{$tableShort}   += $trueRow;
      if ($majorTable) { $majorList .= "$curTable: $tableRow rows<br />"; }
      $majorTable = 0;
      $curTable   = "";
    }
    if ($table) {
      my @cols = split( "\t", $a );
      if ( $a =~ /(\"\"|--|\t\t)/ ) {
        for ( 0 .. $#cols ) {
          if ( ( $cols[$_] eq "--" ) || ( $cols[$_] eq "\|\|" ) ) {
            print "Empty entry at $tableShort, line $., column $_.\n"
              if !defined( $ignoreBlankCols{"$tableShort:$_"} );
          }
          if ( $cols[$_] eq "" ) {
            print "Double tab at $tableShort, line $., column $_-"
              . ( $_ + 1 ) . "\n";
          }
        }
      }
      if ($thisTableRow) {
        my $tempLine = $a;
        while ( $tempLine =~ /[\t ]\[[^\]]*\]$/i ) {
          $tempLine =~ s/[\t ]\[[^\]]*\]$//gi;
        }
        my $columnsThisRow = ( scalar split( /[\t]+/, $tempLine ) );
        if ( $columnsThisRow > $thisTableRow ) {
          print
"BIG PROBLEM: $curTable line $. ($tableShort) has $columnsThisRow rows, should have no more than $thisTableRow.\n";
        }
        elsif ( $columnsThisRow != $thisTableRow ) {
          print
"WARNING: $curTable line $. ($tableShort) has $columnsThisRow rows, should have $thisTableRow.\n"
            unless ( defined( $minRows{$tableShort} ) )
            && ( $columnsThisRow >= $minRows{$tableShort} );
        }
      }
      print B $a;
      $count++;
      $tableRow++;
      if ( $a =~ /^\[/ ) {
        print
"ROW MISMATCH: $curTable has a comment which may throw the counter off.\n";
      }
      if ( $a =~ /(false\t|\tfalse)/ ) { $falseRow++; }
      if ( $a =~ /(true\t|\ttrue)/ )   { $trueRow++; }
      my $y       = $a;
      my $tempAdd = ( $y =~ s/\[(activation of|e0|e1|e2|e3|e4|na\b)//g );
      if ( ( $tempAdd < 1 )
        && $smartIdea
        && ( !defined( $ignoreDup{$tableShort} ) )
        && !$optActivate{$tableShort} )
      {
        print
          "Line $. in $sourceFile ($tableShort) has no activations/e2/na.\n";
        $noAct++;
        $actLog .= " $.";
      }
      $smartIdea += $tempAdd;
      print "$smartIdea ideas now after $tableRow rows, $curTable, $a\n"
        if $superVerbose && $smartIdea;
      if ( ( $a =~ /[a-z]/i ) && ( $tableRow > -1 ) ) {
        my @tempAry = split( /\t/, $a );
        if ( $#tempAry > $#tableCount ) { $maxString = $a; }
        elsif ( $#tempAry == $#tableCount ) { $maxString .= $a; }
        $tableCount[$#tempAry]++;
      }
    }
  }

  if ( !$quietTables ) {
    $sum = "$tables tables, $count lines.\n$tableList";
    print $sum;
  }

  print B $sum;
  close(A);
  close(B);
}

my $ranOneTest = 0;
my $errLog     = "";
my $thisFile   = "";
my $lastOpen   = "";

for ( 1 .. $testCount ) {
  my $tn = $tableName{$_};
  my @tary = split( /\+/, $tn );

  my $origRegex = $regex{$_};
  $regexMod{$_} = $regex{$_};
  $regexMod{$_} =~ s/\$[\$cft]/[0-9]+/;

# this is a hack for Buddy Best's case basket in Problems Compound. We could fob this off to the final but it's too much programming for too little payoff
  if ( $tn eq "xxfln" ) {
    my $q = 3 * int( $rows{$tn} ) / 6;
    $regex{$_} = tableNumberDelta( $tn, $regex{$_}, $delta{$_} );
  }

  # print "Tweaking $_ / $regex{$_}\n";
  $regex{$_} =~ s/\$\$/multTableSums(\%rows, \@tary)+$delta{$_}/ge;
  $regex{$_} =~ s/\$c/multTableSums(\%smartIdeas, \@tary)+$delta{$_}/ge;
  $regex{$_} =~ s/\$f/multTableSums(\%falseRows, \@tary)+$delta{$_}/ge;
  $regex{$_} =~ s/\$t/multTableSums(\%trueRows, \@tary)+$delta{$_}/ge;

  print "Tweaked $_ / $regex{$_} / $regexMod{$_} from $origRegex\n";

  #print "$_ $tableName{$_}=$regex{$_} / $regexMod{$_}\n";

}

for my $dataFile ( keys %dataFiles ) {
  sortDataFile($dataFile);
}

if ( scalar keys %notFound ) {
  print ""
    . ( scalar keys %notFound )
    . " text tests not found, listed below.\n========================================\n";
  for ( keys %notFound ) {
    print "FAILED: No close match found for string $regex{$_}\n";
  }
}

if ($openPost) {
  my $myfi;
  for $myfi ( sort keys %filesToOpen ) {
    print "Opening $myfi, line $filesToOpen{$myfi}\n";
    my $openCmd =
      "start \"\" \"C:\\Program Files\\Notepad++\\notepad++.exe\" $myfi";
    if ( $filesToOpen{$myfi} ) { $openCmd .= " -n$filesToOpen{$myfi}"; }
    `$openCmd`;
    if ( $spawnPopup && $popupString ) {
      if ( scalar @popupLines ) {
        $popupString .= "Lines: " . join( ", ", sort(@popupLines) ) . "\n";
      }
      my $myShort = $myfi;
      $myShort =~ s/.*[\/\\]//;
      Win32::MsgBox(
        "Miscounts in $myShort\n" . ( '=' x 20 ) . "\n$popupString",
        0, "I7T.PL results" );
    }
  }
  if ( !scalar keys %filesToOpen ) { print "No error files to open!\n"; }
  if ( scalar keys %doubleErr ) {
    print "Files with >1 error:\n";
    for $myfi ( sort { $doubleErr{$a} <=> $doubleErr{$b} } keys %doubleErr ) {
      $doubleErr{$myfi}++;
      print "$myfi: $doubleErr{$myfi} total focus-able errors.\n";
    }
  }
}
elsif ($spawnPopup) {
  print
"'\nNOTE: The program forces you to type -o with spawnPopup (-sp), because otherwise you just see a popup and then have to type in the file to edit anyway.\n";
}

if ($openTableFile) {
  my $openCmd =
"start \"\" \"C:\\Program Files\\Notepad++\\notepad++.exe\" $tableFile";
  `$openCmd`;
}

if ($dupFail) {
  print "TEST RESULTS:(notes) $project-tabledup,0,$dupFail,0,$dupLog\n";
}

if ($noAct) {
  print
"TEST RESULTS:(notes) $project-activations,0,$noAct,0,Look <a href=\"file:///$thisFile\">here</a>\n$actLog\n";
}

if ($majorList) {
  $majorList =~ s/,//g;
  print "TEST RESULTS:$project table count,0,$countMismatch,0,$majorList\n";
}

if ( $ranOneTest && !$dupFail && !$noAct && !$majorList ) {
  print "EVERYTHING WORKED! YAY!\n";
}

exit();

####################################################
#subroutines below
#

sub multTableSums {
  my %hash = %{ $_[0] };
  my @ary  = @{ $_[1] };
  my $x;
  my $retVal = 0;

  # foreach my $key (keys %hash) { print "$key $hash{$key}\n"; }
  for $x (@ary) {
    $retVal += $hash{$x};
  }
  return $retVal;
}

sub tableNumberDelta    # 0=table name 1=regex 2=smart-string 3=formula
{
  my $newNum = 0;
  my $froms  = "";

  if ( $_[1] =~ /\$\$/ ) {
    $froms  = "\$\$";
    $newNum = $rows{ $_[0] };
  }
  elsif ( $_[1] =~ /\$c/ ) {
    $froms  = $_[1];
    $newNum = $smartIdeas{ $_[0] };
  }
  elsif ( $_[1] =~ /\$f/ ) {
    $froms  = $_[1];
    $newNum = $falseRows{ $_[0] };
  }
  elsif ( $_[1] =~ /\$t/ ) {
    $froms  = $_[1];
    $newNum = $trueRows{ $_[0] };
  }
  return $_[1] if !$froms;

  # for my $x (keys %rows) { print "$x $rows{$x}\n"; }

  # the default is just to add stuff
  return $newNum + $_[2] if ( $_[2] =~ /^[0-9]+$/ );
  my $func = $_[2];
  $func =~ s/!/$newNum/;
  my $evf    = eval($func);
  my $retval = $_[1];
  my $f2     = quotemeta($froms);
  $retval =~ s/$f2/$evf/g;
  return $retval;
}

####################################################
#this processes the i7t.txt / i7tp.txt files
#

sub processInitData {
  my $line;
  my $currentReadFile;

  open( A, "$_[0]" ) || die("No file $_[0]");
  while ( $line = <A> ) {
    if ( $line =~ /^#/ ) { next; }
    if ( $line =~ /^;/ ) { next; }
    if ( $line =~ /^$project\t/ ) {
      chomp($line);
      my @tabElts = split( /\t/, $line );
      if ( $tabElts[1] =~ /^igdup:/ ) {
        $tabElts[1] =~ s/^igdup://;
        $ignoreDup{ $tabElts[1] } = 1;
        next;
      }
      if ( $tabElts[1] =~ /^optact:/ ) {
        $tabElts[1] =~ s/^optact://;
        $optActivate{ $tabElts[1] } = 1;
        next;
      }
      if ( $tabElts[1] =~ /^igcol:/ ) {
        $tabElts[1] =~ s/^igcol://;
        if ( $tabElts[1] =~ /^[0-9]+:/ ) {
          print
"i7t.txt Line $.: $tabElts[1] reversed to put #s second in config file for IGCOL.\n";
          $tabElts[1] =~ s/^([0-9]+):(.*)/$2:$1/;
        }
        $ignoreBlankCols{ $tabElts[1] } = 1;
        next;
      }
      if ( $tabElts[1] =~ /^minrow(s)?:/ ) {
        $tabElts[1] =~ s/^minrow(s)?://;
        if ( $tabElts[1] =~ /^[0-9]+:/ ) {
          print
"i7t.txt Line $.: $tabElts[1] reversed to put #s second in config file for MINROW.\n";
          $tabElts[1] =~ s/^([0-9]+):(.*)/$2:$1/;
        }
        my @xrow = split( /:/, $tabElts[1] );
        $minRows{ $xrow[0] } = $xrow[1];
        next;
      }
      if ( $tabElts[1] =~ /^xrow(s)?:/ ) {
        $tabElts[1] =~ s/^xrow(s)?://;
        if ( $tabElts[1] =~ /^[0-9]+:/ ) {
          print
"i7t.txt Line $.: $tabElts[1] reversed to put #s second in config file for XROW.\n";
          $tabElts[1] =~ s/^([0-9]+):(.*)/$2:$1/;
        }
        my @xrow = split( /:/, $tabElts[1] );
        $extraRows{ $xrow[0] } = $xrow[1];
        next;
      }
      if ( scalar @tabElts == 2 ) {
        if ( defined( $failCmd{$project} ) ) {
          die(
"2 fail commands defined for $project: $failCmd{$project} overwritten by line $line"
          );
        }
        $failCmd{$project} = $tabElts[1];
      }
      elsif ( scalar @tabElts != 5 ) {
        die("Need project/table name/file name/regex/delta at $line");
      }
      else {
        $testCount++;
        $notFound{$testCount}  = 1;
        $tableName{$testCount} = $tabElts[1];
        if ( $tabElts[2] eq "\"" ) {
          $readFileName{$testCount} = $currentReadFile;
        }
        else {
          $readFileName{$testCount} = $currentReadFile = $tabElts[2];
        }
        if ( !defined( $dataFiles{$currentReadFile} ) ) {
          $dataFiles{$currentReadFile} = 1;
        }
        $regex{$testCount} = $tabElts[3];
        $delta{$testCount} = $tabElts[4];
      }
    }
    if ( $line =~ /^xtra/ ) {
      chomp($line);
      my @filemap = split( /\t/, $line );
      if ( $#filemap != 2 ) { warn "Need 3 fields in $.: $line\n"; next; }
      if ( !defined( $projFiles{ $filemap[1] } ) ) {
        $projFiles{ $filemap[1] } = [];
      }
      push( @{ $projFiles{ $filemap[1] } }, $filemap[2] );
    }
    if ( $line =~ /^story/ ) {
      chomp($line);
      my @filemap = split( /\t/, $line );
      if ( $#filemap != 1 ) { warn "Need 2 fields in $.: $line\n"; next; }
      if ( !defined( $projFiles{ $filemap[1] } ) ) {
        $projFiles{ $filemap[1] } = [];
      }
    }
  }
  close(A);
}

#####################################
#this processes the data files like x_release_1.txt
#

sub sortDataFile {
  my $line;
  my $tempOut           = "c:\\temp\\i7t-temp.txt";
  my $meaningfulChanges = 0;
  my $anyTest           = 0;

  open( A, $_[0] )       || die("Can't open data file $_[0]");
  open( B, ">$tempOut" ) || die("Can't open $tempOut for writing.");
OUTER:
  while ( $line = <A> ) {
    for ( keys %notFound ) {
      if ( $line =~ /$regex{$_}/ ) {
        $anyTest = 1;
        if ($verbose) { print "Line $.: MATCHED $_ $regex{$_} with $line"; }
        delete( $notFound{$_} );
      }
      elsif ( $line =~ /$regexMod{$_}/ ) {
        $anyTest = 1;
        print "Line $.: ALMOST MATCHED (FAILED"
          . ( $writeRight ? "/WILL BE UPDATED" : "" )
          . ") SHOULD BE regex ($regex{$_}) IS $line";
        $filesToOpen{ $_[0] } = $.;
        delete( $notFound{$_} );
        $meaningfulChanges = 1;
        $line =~ s/$regexMod{$_}/$regex{$_}/;
      }
    }
    print B $line;
  }
  close(A);
  close(B);
  print "Didn't find any lines in $_[0] to compare." if !$anyTest;

  if ( $writeRight && $meaningfulChanges ) {
    print "Copying modified file over...\n";
    my $cmd = "copy $tempOut $_[0]";
    $cmd =~ s/\//\\/g;
    print "$cmd\n";
    system($cmd);
  }
  elsif ($meaningfulChanges) {
    print "Run again with -w to fix target file $_[0].\n";
  }
  else {
    print "Nothing to write for $_[0].\n";
  }
}

sub usage {
  print <<EOT;
directory
csv = tables to highlight
-t specifies a CSV of important tables to track
-c specifies the writedir for tables.i7 as the current directory (default is writing\\dict)
-e opens the i7t.pl file
-f opens the i7t.txt file
-ef/fe opens both
-i lists important arrays
-o opens the offending file post-test
-ot opens the table file
-q quiets out the printing of tables
-v verbose, -sv/vs super verbose
-w writeRight option: write the right options in
-tl lists them (currently the default)
-ps prints out successes as well
-[ps] specifies the project, written out or in shorthand
-sp spawns a popup Windows message box to tell what to replace, if valid
(directory) looks for story.ni in a different directory
(ra|nu)(r|s) does random text or nudges for roiling or shuffling
EOT
  exit;
}
