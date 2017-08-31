##############################################
#
#dsort.pl
#
#this sorts daily files into the (semi)-organized component files
#
#Usual usage is:
#dsort -home
#

use strict;
use warnings;

use File::Copy;
use Time::Local;

#############unix Files
my %whatWhereHash;
my %toPrimaryHash;
my %detailHash;

my $myNotesFile = "notes9.otl";
my $dailyLog    = "c:\\writing\\daily-log.txt";
my @outFiles;
my @inDirs;
my %writings;
my %skipReading;
my @fileArray = (
  "$myNotesFile", "hthws.otl", "sbnotes.txt", "limericks.otl",
  "lists.otl",    "sb.otl",    "names.otl",   "games.otl",
  "misc.otl",     "f.otl",     "smart.otl"
);

########options
my $daysBack       = 120;
my $readOnly       = 0;
my $outputHash     = 0;
my $skipOutput     = 0;
my $verifySections = 0;
my $intoDir;
my $debug           = 0;
my $verifyFirstLine = 0;
my $looseTest       = 0;
my $noMove          = 0;
my $quiet           = 0;
my $verbose         = 0;

##############variables
my $unixFiles = "";
my $procBytes = 0;
my $bigString = "";
my $nolet     = "";

#############counters
my $match;

my (
  $second,     $minute,    $hour,
  $dayOfMonth, $month,     $yearOffset,
  $dayOfWeek,  $dayOfYear, $daylightSavings
) = localtime();
my $todaysFile;

initializeGlobals();
readCmdLine();

my $lastDayString  = todayString(1);
my $firstDayString = todayString($daysBack);

preprocessFileList(@fileArray);

#print $detailHash{"das-par"};

#die($detailHash{"das-pkg"});

if ($outputHash) { rewriteHashFile(); }
if ($skipOutput) { exit; }

my $beforeTime = time();

my $finalString = "Before: ";
my $beforeBytes = readFileSizes();

my $foundOne = 0;
my $dailyDir;
for $dailyDir (@inDirs) {
  if ( -d $dailyDir ) { $foundOne = 1; }
}

if ( !$foundOne ) { die( "No valid dir in " . join( " ", @inDirs ) ); }

my $npSes = "C:\\Users\\Andrew\\AppData\\Roaming\\Notepad++\\session.xml";
open( X, $npSes ) || die("Can't open $npSes");

my $line;

while ( $line = <X> ) {
  if ( $line =~ /backupFilePath=\"c/i ) {
    $line =~ s/.* filename=.//;
    $line =~ s/\".*//g;

    #print "$line";
    chomp($line);
    if ( $line =~ /c:\\writing\\daily\\2[0-9]{7}\.txt/i ) {
      print "WARNING daily file $line needs to be saved before processing\n";
      $line =~ s/.*\\//g;
      $skipReading{$line} = 1;
    }
  }
}

for $dailyDir (@inDirs) {

  opendir( DIR, "$dailyDir" );

  my @dircontents = readdir(DIR);

  my $fi;

  open( DL, ">>$dailyLog" );

  for $fi (@dircontents) {
    if ( $fi !~ /txt$/i ) { next; }

    #print "Trying $dailyDir/$fi\n";
    if ( $fi !~ /^20[0-9]{6}\.txt/i ) { next; }
    if ( $skipReading{$fi} ) { print "Unsaved $fi, skipping.\n"; next; }
    if ( ($lastDayString) && ( $fi gt $lastDayString ) ) {
      print "$fi too soon\n";
      next;
    }

    #print "Trying $dailyDir/$fi\n";
    if ( ($firstDayString) && ( $fi lt $firstDayString ) ) {
      print "$fi too late\n";
      next;
    }

    #print "Making sure $fi is not 0-byte\n";
    if ( -s "$dailyDir/$fi" == 0 ) { print "$fi has 0 bytes\n"; next; }

    #print "Trying $dailyDir/$fi\n";
    if ( -d "$intoDir/$fi" ) { print "$fi is in output directory\n"; next; }

    #print "Trying $dailyDir/$fi\n";
    if ($verifyFirstLine) {
      if ( firstLineThereOrEmpty("$dailyDir/$fi") ) { next; }
    }

    #print "Reading $intoDir/$fi\n";
    if ( isUnix("$dailyDir/$fi") ) {
      print "$dailyDir/$fi is a Unix file.\n";
      $unixFiles .= "$dailyDir/$fi\n";
      next;
    }
    $procBytes += ( -s "$dailyDir/$fi" );
    chopDailyFile("$dailyDir/$fi");
    my $year  = substr( $fi, 0, 4 );
    my $month = substr( $fi, 4, 2 ) - 1;
    my $day   = substr( $fi, 6, 2 );
    my $time  = timelocal( 59, 59, 23, $day, $month, $year ) + 1;
    my $tdelt = ( time() - $time );
    my $delta = sprintf( "%d", $tdelt / 86400 );
    print DL "$fi took $delta day(s) rounded down, $tdelt seconds.\n";
  }

  close(DL);
  die();

}

my $unknownBefore = ( -s "$intoDir/undef.txt" );
cleanUpUnknown();
my $unknownAfter = ( -s "$intoDir/undef.txt" );
my $unknownDelta = $unknownAfter - $unknownBefore;

my $afterTime  = time() - $beforeTime;
my $afterBytes = readFileSizes();
print "Before $beforeBytes After $afterBytes Dif "
  . ( $afterBytes - $beforeBytes )
  . "\nBytes of files processed=$procBytes\nBytes of unknown=$unknownDelta added, $unknownAfter total.\nProcessing took $afterTime seconds.";

if ($bigString) {
  $bigString =~ s/\//\\/g;
  print "\n=============\nFILES TO RERUN:\n$bigString\n";
}
else { addStatsLine(); }

if ($unixFiles) {
  $unixFiles =~ s/\//\\/g;
  print "\n=============\nUNIX FILES:\n$unixFiles";
}

if ($nolet) {
  $nolet =~ s/\//\\/g;
  print "\n=============\nDOESNT START WITH LETTER/NUMBER:\n$nolet";
}

#print "This completed successfully, more or less.\n";
exit;

############################
############################subroutines
############################

sub cleanUpUnknown {
  open( C, ">>$intoDir/undef.txt" );

  my @stuff = localtime(time);
  printf C sprintf(
    "Unknown writings log for %02d-%02d-%02d %02d:%02d:%02d\n\n",
    $stuff[4] + 1, $stuff[3], $stuff[5] + 1900,
    $stuff[2],     $stuff[1], $stuff[0]
  );

  foreach my $qzz ( keys %writings ) {
    if ( !$whatWhereHash{$qzz} ) {
      print "Unknown WhatWhere \\$qzz.\n";    #====$writings{$qzz}====\n";
      print C "$qzz\n$writings{$qzz}\n";
      next;
    }

    #print "Zapping $qzz key.\n";
    delete $writings{$qzz};
  }

  close(C);

}

sub firstLineThereOrEmpty {
  my $d;

  if ( !$quiet ) {
    print "verifying if first line of $_[0] is in $myNotesFile:";
  }
  if ( -s "$_[0]" == 0 ) { print "Empty file $_[0].\n"; return 1; }
  open( B, "$_[0]" );
  $b = <B>;
  close(B);
  if ( $b !~ /[a-z0-9]/i ) {
    print "Doesn't contain a letter/number.\n";
    $nolet .= "$_[0]\n";
    return 1;
  }
  if ( $b !~ /^[a-z0-9\"\']/i ) {
    print "Doesn't start with a letter/number.\n";
    $nolet .= "$_[0]\n";
    return 1;
  }
  open( B, "$intoDir/$myNotesFile" )
    || die("Can't open $intoDir/$myNotesFile to verify $_[0] first line\n");
  while ( $d = <B> ) {
    if ( $b eq $d ) {
      close(B);
      print " yes, skipping\n";
      return 1;
    }
  }
  print "No, processing\n";
  return 0;
}

sub chopDailyFile {

  #print "Processing $_[0]...\n";
  preProcessDailyFile( $_[0] );

  #print "reading $_[0]\n";

  open( A, "$_[0]" ) || die("Can't open $_[0]");

  #%writings = ();
  my @temp;
  my $undefinedWritings = "";

  my %doubleCheck;
  my %origLines;

  #always start with basic ideas. At least for now.
  my $currentSection = "ide";

  my $returnIt = 0;
  my $hashval  = "";
  my $cr;

  while ( $a = <A> ) {
    chomp($a);
    if ( $a =~ /^\\/ ) {
      my $aa = chompy($a);
      if ( $toPrimaryHash{$aa} ) { $b = $toPrimaryHash{$aa}; die; }
      else                       { $b = $aa; }
      if ( defined( $doubleCheck{$b} ) && ( $doubleCheck{$b} == 1 ) ) {
        my $c = <A>;
        chomp($c);
        print(
"WARNING: $_[0] has duplicate section $b, 2nd line $c copies $origLines{$b}.\nRetry later.\n"
        );
        $c =~ s/ .*//g;
        if ( $returnIt == 0 ) { $bigString .= "$_[0]\n"; $returnIt = 1; }
        $bigString .= "$b == $c ($. copies $origLines{$b})\n";
      }
      $doubleCheck{$b} = 1;
      $origLines{$b}   = $.;
    }
    if ( ( $a =~ /[a-z][A-Z]/ ) && ( $a !~ /\t/ ) ) {
      print "WARNING possible run-on line: $a\n";
    }
  }

  if ($returnIt) { return; }

  close(A);

  open( A, "$_[0]" );

  #print "Reading $_[0]\n";

  #first, we read in from the individual file and sort everything.
  while ( $a = <A> ) {
    if ( $a =~ /^\\/ ) {
      $currentSection = chompy($a);
      if ( !$detailHash{$currentSection} ) {
        print "Undefined section $currentSection\n";
      }

      #print("Reading section $temp[0] aka '$detailHash{$temp[0]}' from $a\n");
      if ( $writings{$currentSection} ) {
        $b = <A>;
        chomp($b);
        print
"WARNING you have two sections '$detailHash{$currentSection}' starting with $b\n";
        $writings{$currentSection} .= $b;
      }
      next;
    }
    if ( $a !~ /[a-zA-Z0-9=]/ ) { $currentSection = ""; next; }

    #print "PROCESSING $a [using $currentSection]:";

    if ($currentSection) {

      #print "$currentSection====$a";
      if ( ( $currentSection ne "nam" ) && ( $a !~ /\n$/ ) ) {
        print "Warning $a==no carriage return.\n";
        $a .= "\n";
      }
      $writings{$currentSection} .= $a;
    }
    else { $undefinedWritings .= $a; }

  }

  close(A);

  #debug line to see if anything is printed
  #for $x ( keys %writings) { print "\n========$x $writings{$x}\n"; }

  foreach ( keys %whatWhereHash ) {
    if ( !defined( $writings{$_} ) ) { next; }
    if ( !"$writings{$_}" )          { next; }

    #print "Got $_ $whatWhereHash{$_}\n";

    $a = $whatWhereHash{$_};
    if ($verbose) {
      print "Adding $_, eg $detailHash{$_}, to $a\n";
    }
    if ( !isIn( $a, @outFiles ) ) { @outFiles = ( @outFiles, $a ); }
  }

  #for (@outFiles) { print "File $_ may be written to\n"; }

#foreach (keys %whatWhereHash) { if ($writings{$_}) { printDebug("put $_ in $whatWhereHash{$_}\n"); } }

  for (@outFiles) {

    #print "Looking at $_\n";

    open( A, "$intoDir/$_" );
    open( B, ">$intoDir/temp-$_" );
    while ( $a = <A> ) {
      if ( ( $a =~ /^\\/ ) && ( $hashval = haveWriting($a) ) ) {

        #print "OK, starting $hashval\n";
        print B $a;
        while ( ( $b = <A> ) ) {
          last if $b =~ /[a-zA-Z0-9=]/;
          print B $b;
        }

        #print "Adding $hashval\n";
        #print "Adding $hashval--\n$writings{$hashval}";
        if ( $hashval eq "nam" ) {
          $cr = "";

          #print "No CR for \\nam.\n";
          if ( $writings{$hashval} !~ /^\t/ ) {
            $writings{$hashval} = "\t$writings{$hashval}";
          }
        }
        else {
          $cr = "\n";
          if ( $writings{$hashval} !~ /\n$/ ) { $writings{$hashval} .= "\n"; }
        }
        print B "$writings{$hashval}$cr";

        #print "Put $a--$writings{$hashval}$cr==to temp-$_\n";
        #print "Deleting $hashval\n";

        #print "Deleting $hashval.\n";
        delete $writings{$hashval};
      }
      else { print B $a; }
    }

    close(A);
    close(B);

    #if ($_ =~ /notes/) { print "$_ size Before: " . ( -s "$intoDir/$_" ); }
    move( "$intoDir/temp-$_", "$intoDir/$_" );

    #if ($_ =~ /notes/) { print " After: " . ( -s "$intoDir/$_" ) . "\n"; }
  }

  foreach ( keys %writings ) { print "$_ not deleted.\n"; }

  #print "Unfound $_ should be in $whatWhereHash{$_}\n\\$_\n$writings{$_}\n";

  #print C "$whatWhereHash{$_}\n\\$_\n$writings{$_}\n";

  if ($undefinedWritings) {
    open( C, ">>undef.txt" );
    print C "========$_[0]\n$undefinedWritings\n";
    if ($verbose) { print "========$_[0]\n$undefinedWritings\n"; }
    close(C);
  }

  my @toFileAry = split( /[\\\/]/, $_[0] );
  my $temp = pop(@toFileAry);
  push( @toFileAry, "done" );
  push( @toFileAry, $temp );
  $temp = join( '\\', @toFileAry );
  if ( !$noMove ) { move( "$_[0]", "$temp" ); }

  #for $qz (keys %writings) { print "$qz = $writings{$qz}\n"; }

}    #end of chopDaily

#######################################

sub isIn {

  my ( $tofind, @array ) = @_;

  if ($looseTest) {
    foreach $match (@array) {
      if ( $tofind =~ /$match/ ) { return 1; }
    }
    return 0;
  }
  foreach $match (@array) {
    if ( $tofind eq $match ) { return 1; }
  }
  return 0;
}

sub haveWriting {
  my $temp = $_[0];
  chomp $temp;
  if ( $temp =~ /qui/ ) {    #print "?!?! QUI\n";
  }    #Popular tag used for testing when I want to add new
       #print "Testing $temp.\n";
  $temp =~ s/=.*//g;
  $temp =~ s/^\\//g;
  for ( split( /\|/, $temp ) ) {
    if ( $writings{$_} ) { return $_; }
  }
  return 0;
}

sub chompy {
  my $temp = $_[0];
  chomp($temp);
  $temp =~ s/^\\//g;
  $temp =~ s/=.*//g;

  #print "$temp...\n";
  if ( $toPrimaryHash{$temp} ) { return $toPrimaryHash{$temp}; }
  return $temp;
}

sub initializeGlobals {

  #change this if I get bored or pissed or realize 1 way or the other is better
  $verifyFirstLine = 1;

  @outFiles = ();

  $intoDir = "c:/writing";

  if (0) {
    $myNotesFile = "notes9.otl";

    %whatWhereHash = (
      "lim" => "limericks.otl",
      "ide" => $myNotesFile,
      "den" => "hthws.otl",
      "gil" => "gnj.otl",
      "smo" => "smoboynotes.txt",
      "s"   => $myNotesFile,
      "qui" => $myNotesFile,
      "w"   => $myNotesFile,
      "mag" => $myNotesFile,
      "nam" => "names.otl",
      "dai" => "booksread.otl",
      "boo" => "booksread.otl",
      "mov" => "booksread.otl",
      "zzz" => "nonexist.otl"
    );

  }

  #look for today's file
  $todaysFile =
    sprintf( "%d%02d%02d.txt", $yearOffset + 1900, $month + 1, $dayOfMonth );

}

sub preProcessDailyFile {
}

sub preprocessFileList {
  my $thisFile;
  my @descriptors;

  for $thisFile (@_) {
    open( A, "$intoDir/$thisFile" )
      || die("Can't open $intoDir/$thisFile")
      ;    #print "Go-go, $intoDir/$thisFile\n";
    while ( $a = <A> ) {
      chomp($a);
      if ( $a =~ /^\\[0-9a-z]/ ) {    #print "Trying $a in $thisFile\n";
        my @b = split( /=/, $a );
        if ( !$b[1] ) { push( @descriptors, "$b[0] ($.) in $thisFile" ); }
        $b[0] =~ s/^.//g;             #print "Adding $b[0]<->$b[1] $thisFile\n";
        my @c = split( /\|/, $b[0] );
        for (@c) {
          if ( $_ ne $c[0] ) {
            $toPrimaryHash{$_} = $c[0];    #print "$_ -> $c[0]\n";
          }
          else {
            $whatWhereHash{$_} = $thisFile;
            if ( $detailHash{$_} ) {
              die("Oops. We have 2 descriptors of $_.\n");
            }
            $detailHash{$_} = $b[1];
          }
        }
      }
    }
    close(A);
    die( "Need descriptors for " . join( ", ", @descriptors ) )
      if scalar @descriptors;

  }    #exit;

}

sub rewriteHashFile {
  my $x;
  open( X, ">$intoDir/ideahash.txt" );
  for $x ( sort keys %whatWhereHash ) {
    print X
      sprintf( "%-10s=%-20s [$whatWhereHash{$x}]\n", $x, $detailHash{$x} );
    if ( !$skipOutput ) {
      print STDOUT
        sprintf( "%-10s=%-20s [$whatWhereHash{$x}]\n", $x, $detailHash{$x} );
    }
  }
  for $x ( sort keys %toPrimaryHash ) {
    print X sprintf( "%-10s=%-20s\n", $x, $toPrimaryHash{$x} );
  }
  for $x ( sort keys %detailHash ) {
    if ( !$whatWhereHash{$x} ) { print "$x needs whatwhere\n"; }
  }
  for $x ( sort keys %whatWhereHash ) {
    if ( !$detailHash{$x} ) { print "$x needs detailhash\n"; }
  }
}

sub addStatsLine {
  my @x = ();
  open( STA, ">>c:/writing/dstat.txt" );
  my $localtime = gmtime( time() );
  my $newString = "$localtime: ";

  for my $x (@fileArray) {
    if ( !-f "c:/writing/$x" ) { print("Warning: No $x."); }
    $newString .= $x . "=" . ( -s "c:/writing/$x" ) . ",";
  }

  $newString =~ s/,$//g;

  print "$newString\n";
  print STA "$newString\n";
  close(STA);

  if ( $#fileArray > 0 ) {
    print "Added latest file stats to writing/dstat.txt.";
  }
}

sub printDebug {
  if ($debug) { print $_[0]; }
}

sub readCmdLine {

  if ( $#ARGV eq -1 ) { print "No arguments, giving usage.\n"; usage(); }

  my $count = 0;

  while ( $count <= $#ARGV ) {
    $a = $ARGV[$count];
    $b = $ARGV[ $count + 1 ];
    for ($a) {
      /^-?fi$/ && do { @fileArray = split( /,/, $b ); next; };
      /^-?q$/  && do { $quiet           = 1; $count++; next; };
      /^-?v$/  && do { $verbose         = 1; $count++; next; };
      /^-?vy$/ && do { $verifyFirstLine = 1; $count++; next; };
      /^-?vn$/ && do { $verifyFirstLine = 0; $count++; next; };
      /^-?vs$/
        && do { $verifySections = 1; $count++; next; }; #not sure what this does other than make sure sections are valid which seems to be done by default
      /^-?flash$/ && do {
        @inDirs = ( "e:/daily", "f:/daily", "g:/daily" );
        $intoDir = "c:/writing";
        $count++;
        next;
      };
      /^-?dc$/ && do { duplicateCheck(); exit(); };
      /^-?lt$/   && do { $looseTest     = 1;              $count++; next; };
      /^-?nt$/   && do { $lastDayString = todayString(1); $count++; next; };
      /^-?[2t]$/ && do { $lastDayString = todayString(0); $count++; next; };
      /^-?work$/ && do {
        $intoDir = "c:/coding/perl/daily/bak";
        @inDirs  = ($intoDir);
        $count++;
        next;
      };
      /^-?r$/ && do { $readOnly = 1; $count++; next; };
      /^-?!$/ && do { $debug    = 1; $count++; next; };
      /^-?d$/ && do { $intoDir = $b; $count += 2; next; };
      /^-?i$/ && do { @inDirs = split( /,/, $b ); $count += 2; next; };
      /^-?(w|home)$/ && do {
        @inDirs = ( "c:/writing/daily", "c:/users/andrew/dropbox/daily" );
        $intoDir = "c:/writing";
        $count++;
        next;
      };
      /^-?(db|bx)$/ && do {
        @inDirs  = ("c:/users/andrew/dropbox/daily");
        $intoDir = "c:/writing";
        $count++;
        next;
      };
      /^-?[efg]$/ && do {
        @inDirs = ("$a:/daily");
        $inDirs[0] =~ s/^-//g;
        $intoDir = "c:/writing";
        $count++;
        next;
      };
      /^-?oo$/ && do { $outputHash = 1; $skipOutput = 1; $count++; next; };
      /^-?o$/  && do { $outputHash = 1; $count++; next; };
      /^-?nm$/ && do { $noMove     = 1; $count++; next; };
      /^-?(bl)$/ && do { $lastDayString  = $b; $count += 2; next; };
      /^-?(af)$/ && do { $firstDayString = $b; $count += 2; next; };
      /^-?[0-9]+$/
        && do { $daysBack = $a; $daysBack =~ s/^-//g; $count += 2; next; };
      /^-?\?$/   && do { usage();      exit; };
      /^-?\?\?$/ && do { usageQuick(); exit; };
      usage();
    }
  }

}

sub todayString {
  my $temp = time - 86400 * $_[0];

  (
    $second,     $minute,    $hour,
    $dayOfMonth, $month,     $yearOffset,
    $dayOfWeek,  $dayOfYear, $daylightSavings
  ) = localtime($temp);

  my $year = $yearOffset + 1900;

  return sprintf( "%d%02d%02d.txt", $year, $month + 1, $dayOfMonth );
}

sub isUnix {
  my $buffer;
  open( XYZ, $_[0] );
  binmode(XYZ);
  read( XYZ, $buffer, 1000, 0 );
  close(XYZ);

  foreach ( split( //, $buffer ) ) {
    if ( $_ eq chr(13) ) { return 0; }
  }
  return 1;
}

sub readFileSizes {
  my $retVal = 0;
  for (@fileArray) {
    $finalString .= "@fileArray=" . ( -s "$intoDir/$_" ) . " ";
    $retVal += ( -s "$intoDir/$_" );
  }
  return $retVal;
}

sub duplicateCheck {
  opendir( DIR, "c:\\writing\\daily" );

  my @dir   = readdir DIR;
  my @dupes = ();

  for my $f (@dir) {
    if ( $f =~ /2[0-9]{7}.txt/ ) {
      if ( -f "c:\\writing\\daily\\done" ) {
        print "DUPLICATE FILE $f.\n";
        push( @dupes, $f );
      }
    }
  }

  printf(
    "TEST RESULTS:daily duplicate files,%d,0,0,%s\n",
    $#dupes + 1,
    join( " / ", @dupes )
  );

}

sub usageQuick {
  print <<EOT;
dsort.pl -home is the main command to use.
EOT
  exit;
}

sub usage {
  print <<EOT;
Hits every file in the given directory & merges with OTL and TXT files which have lines
/subject=description
-home|w = home settings from c:/writing/daily and DropBox folder
-flash  = try e/f/g:/writing
-work   = try test at work
-nm     = don't move files
-nt     = don't count today (default)
-t/2    = count today
-bx/db  = just dropbox directory
-dc = duplicate count

-b/l = last day string
-a/f = first day string
-! shows debug info
-vy/-vn: verify first line before copying over (default is ON)
-vs verify sections (deprecated, now forced on by default)
-fi specifies a file
-d specifies a directory to write to
-i specifies CSV of directories to write from
-lt means loose test
-o output command line hash
-oo skips output and just rejigs the command line hash
-[efgw] specifies the drive for c:/writing, and w=c
-a = after string (e.g. 20140101) -b = before (e.g. 20140505)
-### = # of days to go back (default = 120)
-?? = shows quick usage
EOT
  exit;
}

