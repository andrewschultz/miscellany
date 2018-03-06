#ICL = Inform Command Line
#
#Perl script to compile stuff without having to open the IDE, etc.
#
#cd c:/Users/Andrew/Documents/Inform/Extensions/
#cd c:/games/inform/$proj.inform/Build
#"C:/Program Files (x86)/Inform 7/Compilers/ni" -rules "C:/Program Files (x86)/Inform 7/Inform7/Extensions" -package "C:/games/inform/$proj.inform" -extension=ulx
#"C:/Program Files (x86)/Inform 7/Compilers/inform-633" -kwSDG +include_path=../Source,./ auto.inf output.ulx
#set HOME=c:/games/inform/$proj.inform
#"C:/Program Files (x86)/Inform 7/Compilers/ni" -release -rules "C:/Program Files (x86)/Inform 7/Inform7/Extensions" -package "C:/games/inform/$proj.inform" -extension=ulx
#"C:/Program Files (x86)/Inform 7/Compilers/cblorb" -windows Release.blurb Build/output.gblorb

#I can and should expand this to do more than one at once

use lib "c:/writing/scripts";
use strict;
use warnings;
use Time::HiRes qw(time);
use i7;

my %zmac;
my %proj;
my %use6l;
my %forceDir;

#######################options
my $informBase         = 0;
my $informDir          = 0;
my $infOnly            = 0;
my $checkRecentChanges = 0;
my $ignoreDRBPrefix    = 0;
my $debugTables        = 0;

my $infDir;

#######################vars
my @allProj;
my @compileList;
my @inDirs;
my @defaultCompileList;

my $ex;
my $gz;
my $iflag;
my $v6l = 0;
my $bdir;
my $mat;
my $bmat;
my $i6x;

my $buildSpecified = 0;

my $betaDir = "c:\\games\\inform\\beta.inform";
my $baseDir = "c:\\games\\inform";
my $logFile = "c:\\writing\\scripts\\icl-log.txt";
my $cfgFile = "c:\\writing\\scripts\\icl.txt";

open( X, $cfgFile ) || die("Need $cfgFile.");

my $x;
my $y;

while ( $x = <X> ) {
  chomp($x);
  if ( $x =~ /^;/ )     { last; }
  if ( $x =~ /^#/ )     { next; }
  if ( $x !~ /[a-z]/i ) { next; }

  my @cmd = split( /=/, $x );
  if ( defined( $cmd[1] ) ) {
    if ( lc( $cmd[0] ) eq lc("default") ) {
      @defaultCompileList = split( /,/, $cmd[1] );
    }
    elsif ( lc( $cmd[0] eq lc "allproj" ) ) {
      @allProj = split( /,/, $cmd[1] );
    }
    else {    # deprecated with the i7 module
      my @froms = split( /,/, $cmd[0] );
      for (@froms) { $i7x{$_} = $cmd[1]; }
    }
  }
  elsif ( $x =~ /^FORCE / ) {
    $y = $x;
    $y =~ s/^FORCE //g;
    my @z = split( /=/, $y );
    $forceDir{ $z[0] } = $z[1];
  }
  elsif ( $x =~ /^z(8)?:/ ) { $y = $x; $y =~ s/^z(8)?://g; $zmac{ p($y) } = 1; }
  elsif ( $x =~ /^z5:/ )    { $y = $x; $y =~ s/^z5://g;    $zmac{ p($y) } = 5; }
  elsif ( $x =~ /^z6:/ ) {
    $y = $x;
    $y =~ s/^z6://g;
    $zmac{ p($y) } = 6;
  }    #z6 is hacky code for z5 in release/beta but z8 in debug
  elsif ( $x =~ /^z7:/ ) {
    $y = $x;
    $y =~ s/^z7://g;
    $zmac{ p($y) } = 7;
  }    #z7 is hacky code for z5 in release but z8 in debug/beta
  elsif ( $x =~ /^6l:/ ) {
    $y = $x;
    $y =~ s/^6l://g;
    $use6l{ p($y) } = 1;
  }
  else {
    print "WARNING: unparsed line $.: $x\n";
  }
}

#sensible abbreviations

$use6l{"compound"} = 0;

my $runBeta = 0;
my $debug   = 0;
my $release = 1;
my $execute = 0;

my $count = 0;

while ( $count <= $#ARGV ) {

  $a = lc( $ARGV[$count] );
  for ($a) {

    #print "Argument " . ($a + 1) . " of " . ($#ARGV + 1) . ": $a\n";
    /^(b|beta)$/
      && do { $buildSpecified = 1; $runBeta = 1 - $runBeta; $count++; next; };
    /^-?jb$/ && do {
      $buildSpecified = 1;
      $runBeta        = 1;
      $debug          = $release = 0;
      $count++;
      next;
    };
    /^-?jd$/ && do {
      $buildSpecified = 1;
      $debug          = 1;
      $runBeta        = $release = 0;
      $count++;
      next;
    };
    /^-?jr$/ && do {
      $buildSpecified = 1;
      $release        = 1;
      $debug          = $runBeta = 0;
      $count++;
      next;
    };
    /^-?jrn$/ && do {
      $buildSpecified  = 1;
      $ignoreDRBPrefix = 1;
      $release         = 1;
      $debug           = $runBeta = 0;
      $count++;
      next;
    };
    /^-?f[rdb]*$/ && do {
      $buildSpecified = 1;
      $release = $debug = $runBeta = 0;
      if ( $a =~ /r/ ) { $release = 1; }
      if ( $a =~ /d/ ) { $debug   = 1; }
      if ( $a =~ /b/ ) { $runBeta = 1; }
      $count++;
      next;
    };
    /^-?24$/
      && do { $checkRecentChanges = 86000; $count++; next; }; # note it's really 86400 seconds in a day but we need fudge factors for daily builds eg if one starts late and the next starts early
    /^-?inf$/ && do { $infOnly = 1; $count++; next; };
    /^-?l$/
      && do { $v6l = 1 - $v6l; $informDir = $inDirs[$v6l]; $count++; next; };
    /^-?ba$/ && do { $informBase      = $ARGV[ $count + 1 ]; $count++; next; };
    /^-?be$/ && do { $betaDir         = $ARGV[ $count + 1 ]; $count++; next; };
    /^-?np$/ && do { $ignoreDRBPrefix = 1;                   $count++; next; };
    /^-?nr$/ && do { $buildSpecified = 1; $release = 0; $count++; next; };
    /^-?yr$/ && do { $buildSpecified = 1; $release = 1; $count++; next; };
    /^-?nd$/ && do { $buildSpecified = 1; $debug   = 0; $count++; next; };
    /^-?yd$/ && do { $buildSpecified = 1; $debug   = 1; $count++; next; };
    /^-(dt|td)$/   && do { $debugTables = 1;  $count++; next; };
    /^-(ndt|ntd)$/ && do { $debugTables = -1; $count++; next; };
    /^-?x$/        && do { $execute     = 1;  $count++; next; };
    /^-?e(c)?$/ && do { `c:\\writing\\scripts\\icl.txt`; exit; };
    /^-?a$/ && do {
      for my $entry (@allProj) { push( @compileList, $a ); }
      $count++;
      next;
    };
    /^-\?$/ && do { usage(); exit; };
    /^-/ && do { print "Not a valid option.\n"; usage(); exit; };
    push( @compileList, $a );
    $count++;
    next;
  }
}

if ( $#compileList == -1 ) {
  print "Nothing in compile list. Using default: @defaultCompileList.\n";
  @compileList = @defaultCompileList;
}

if ( $release + $debug + $runBeta == 0 ) {
  die("None of release/debug/beta chosen.");
}

if ( $buildSpecified == 0 ) {
  print "No builds chosen, going with default list:"
    . ( $release ? " release" : "" )
    . ( $debug   ? " debug"   : "" )
    . ( $runBeta ? " beta"    : "" ) . "\n";
}

my $myProj;

my $startTimeGlobal = time();

my $totalBuilds = $release + $debug + $runBeta;

for my $toComp (@compileList) {
  if    ( $i7x{$toComp} )    { $myProj = $i7x{$toComp}; }
  elsif ( $i7x{"-$toComp"} ) { $myProj = $i7x{"-$toComp"}; }
  elsif ( -d "c:\\games\\inform\\$toComp.inform" ) { $myProj = $toComp; }
  else {
    die("No project for $toComp. If you wanted an option, try -?.\n");
  }
  $infDir = $inDirs[$v6l];
  runProj($myProj);
  $count++;
}

if ( -f "gameinfo.dbg" ) {
  print "Deleting gameinfo.dbg file\n";
  unlink <gameinfo.dbg>;
}

my $totalTimeGlobal = time() - $startTimeGlobal;
print "Total time taken: $totalTimeGlobal seconds.\n";

####################################################
#subroutines
#

sub runProj {

  my $bakfile = "c:\\games\\inform\\story.bak";

  if ( defined( $forceDir{ $_[0] } ) ) {
    $bdir = $forceDir{ $_[0] };
  }
  else {
    $bdir = "$baseDir\\$_[0].inform";
  }

  $infDir = buildDir( $_[0] );
  $i6x    = i6exe( $_[0] );

  if ( $debugTables != 0 ) {
    `copy $bdir\\source\\story.ni $bakfile`;
    open( A, "$bakfile" );
    open( B, ">$bdir\\source\\story.ni" );
    while ( $a = <A> ) {
      if ( $a eq "[debug table switch]\n" ) {
        print B $a;
        my $temp = <A>;
        if ( $debugTables == 1 ) {
          $temp =~ s/ (debug )?tables/ debug tables/i;
        }
        else {
          $temp =~ s/ (debug )?tables/ tables/i;
        }
        print B $temp;
        next;
      }
      else {
        print B $a;
      }
    }
    close(A);
    close(B);
  }

  if ($runBeta) {
    $mat  = "$baseDir\\$_[0].materials";
    $bmat = "$baseDir\\beta Materials";
    if ( $use6l{ $_[0] } ) {
      $mat =~ s/ materials/\.materials/g;
      $bmat =~ s/ materials/\.materials/g;
    }
    doOneBuild( $betaDir, "~D", "$baseDir\\beta Materials", "beta", "$_[0]" );
  }

  if ($release) {
    doOneBuild( "$bdir", "~D", "$baseDir\\$_[0] Materials", "release",
      "$_[0]" );
  }

  if ($debug) {
    doOneBuild( "$bdir", "D", "$baseDir\\$_[0] Materials", "debug", "$_[0]" );
  }

  if ( $debugTables != 0 ) {
    `copy $bakfile $bdir\\source\\story.ni`;
  }

}

sub doOneBuild {
  my $startTime = time();

  $ex    = "ulx";
  $gz    = "gblorb";
  $iflag = "G";
  if ( defined( $zmac{ $_[4] } ) && z5( $zmac{ $_[4] }, $_[3] ) ) {
    $ex    = "z5";
    $gz    = "zblorb";
    $iflag = "v5";
  }
  elsif ( defined( $zmac{ $_[4] } ) && ( $zmac{ $_[4] } > 0 ) ) {
    $ex    = "z8";
    $gz    = "zblorb";
    $iflag = "v8";
  }

  my $tempSource = "$bdir\\source\\story.ni";
  my $outFile    = "$_[0]\\Build\\output.$ex";
  my $dflag      = "$_[1]";
  my $infOut     = "$_[0]\\Build\\auto.inf";

  if ( $_[3] eq "beta" ) {
    copyToBeta($bdir);
  }

  my $blorbFileShort = getFile("$_[0]/Release.blurb");
  if ( $_[3] ne "debug" && !($ignoreDRBPrefix) ) {
    $blorbFileShort = "$_[3]-$blorbFileShort";
  }
  my $outFinal = "$_[2]\\Release\\$blorbFileShort";

  if ($checkRecentChanges) {
    my $lastmod = ( stat($tempSource) )[9];
    my $infmod = -f "$outFinal" ? ( stat($outFinal) )[9] : 0;

    if ( defined($lastmod) && ( $lastmod < $infmod ) ) {
      my $delta1 = time() - $lastmod;
      if ( $delta1 && ( $delta1 > $checkRecentChanges ) ) {
        print
"NOT RUNNING BUILD\nToo long since $tempSource was modified\nToo short since $outFinal was modified\n";
        printTimeDif($startTime);
        return;
      }
      print "$tempSource:$delta1\n";
    }
  }

  delIfThere($infOut);

  my $compileCmd =
"\"$infDir\\Compilers\\ni\" -release -rules \"$infDir\\Inform7\\Extensions\" -package \"$_[0]\" -extension=$ex\"";
  my $compileCheck = `$compileCmd`;

  my $doneTime = time() - $startTime;

  print "BUILD RESULTS\n=================\n$compileCheck";
  if ( $compileCheck =~ /has finished/i ) {
    print "TEST RESULTS:$_[4] $_[3] $_[0] i7->i6 failed,0,1,0\n";
    if ( !$infOnly ) {
      print "TEST RESULTS:$_[4] $_[3] $_[0] i6->binary untested,grey,0,0\n";
      print "TEST RESULTS:$_[4] $_[3] $_[0] blorb creation untested,grey,0,0\n";
    }
    printTimeDif($startTime);
    return;
  }
  if ($infOnly) {
    printTimeDif($startTime);
    return;
  }

  ####probably not necessary
  #print "TEST RESULTS:$_[4] $_[3] $_[0] i7->i6 succeeded,0,0,0\n";

  delIfThere($outFile);
  system(
"\"$infDir/Compilers/$i6x\" -kw~S$dflag$iflag +include_path=$_[0] $infOut $outFile"
  );

  if ( !-f $outFile ) {
    print "TEST RESULTS:$_[4] $_[3] $_[0] i6->binary failed,0,1,0\n";
    print "TEST RESULTS:$_[4] $_[3] $_[0] blorb creation untested,grey,0,0\n";
    printTimeDif($startTime);
    return;
  }

  ####probably not necessary
  #print "TEST RESULTS:$_[4] $_[3] $_[0] i6->binary succeeded,0,0,0\n";

  ################this reloads the final output file
  delIfThere("$outFinal");
  sysprint(
"\"$infDir/Compilers/cblorb\" -windows \"$_[0]\\Release.blurb\" \"$outFinal\""
  );

  print "TEST RESULTS:$_[4] $_[3] $_[0] blorb creation "
    . (  ( !-f $outFinal )
      || ( -s "$outFinal" < -s "$outFile" ) ? "failed,0,1" : "passed,0,0" )
    . ",0\n";

  if ( -f $outFinal ) { writeToLog( $outFinal, @_ ); }
  printTimeDif($startTime);
  return;
}

sub writeToLog {
  open( LOG, "$logFile" );
  my $time        = localtime( time() );
  my $logString   = "$_[0],$_[4],$time";
  my $writeString = "";
  my $line;

  while ( $line = <LOG> ) {
    if ( $line =~ /^$_[0]/ ) {
      $writeString .= $logString;
    }
    else {
      $writeString .= $line;
    }
  }
  close(LOG);
  open( LOG, ">$logFile" );
  print LOG $writeString;
  close(LOG);
}

sub printTimeDif {
  my $temp = time() - $_[0];
  print "$temp seconds elapsed.\n";
}

sub sysprint {
  print "$_[0]\n";
  system("$_[0]");
}

sub copyToBeta {
  print("set HOME=$betaDir\n\n");
  print "****BETA BUILD****\n\n";

  my $mtr = $_[0];
  $mtr =~ s/\.inform/ materials/g;

  print "Copying blurb file...\n";
  system("copy \"$_[0]\\Release.blurb\" \"$betaDir\\Release.blurb\"");
  print "Copying UUID file...\n";
  system("copy \"$_[0]\\uuid.txt\" \"$betaDir\\uuid.txt\"");
  system("erase \"$bmat\\Figures\"*");
  system("copy \"$mtr\\Figures\\*\" \"$bmat\\Figures\"");

  print "Searching for cover....\n";

  my $cover = "$betaDir\\Cover";
  my $covr  = "$betaDir\\Release\\Cover";
  my $smcov = "$betaDir\\Small Cover";
  if ( -f "$cover.jpg" ) {
    print "BETA: Erasing old jpg.\n";
    system("Erase \"$cover.jpg\"");
  }
  if ( -f "$cover.png" ) {
    print "BETA: Erasing old png.\n";
    system("Erase \"$cover.png\"");
  }
  if ( -f "$covr.png" ) {
    print "BETA: Erasing old Release\\png.\n";
    system("Erase \"$covr.png\"");
  }
  if ( -f "$covr.jpg" ) {
    print "BETA: Erasing old Release\\jpg.\n";
    system("Erase \"$covr.jpg\"");
  }
  if ( -f "$smcov.jpg" ) {
    print "BETA: Erasing old small jpg.\n";
    system("Erase \"$smcov.jpg\"");
  }
  if ( -f "$smcov.png" ) {
    print "BETA: Erasing old small png.\n";
    system("erase \"$smcov.png\"");
  }

  if ( -f "c:/games/inform/$_[0] materials/Cover.png" ) {
    print "Copying png over.\n";
    system("copy \"$baseDir\\$_[0] materials\\Cover.png\" \"$bmat\"");
  }
  if ( -f "c:/games/inform/$_[0] materials/Cover.jpg" ) {
    print "Copying jpg over.\n";
    system("copy \"$baseDir\\$_[0] materials\\Cover.jpg\" \"$bmat\"");
  }
  if ( -f "c:/games/inform/$_[0] materials/Small Cover.png" ) {
    print "Copying small png over.\n";
    system("copy \"$baseDir\\$_[0] materials\\Small Cover.png\" \"$bmat\"");
  }
  if ( -f "c:/games/inform/$_[0] materials/Small Cover.jpg" ) {
    print "Copying small jpg over.\n";
    system("copy \"$baseDir\\$_[0] materials\\Small Cover.jpg\" \"$bmat\"");
  }

  modifyBeta( "$_[0]\\source\\story.ni", "$betaDir\\source\\story.ni" );

}

sub modifyBeta {
  open( A, "$_[0]" )  || die("Can't open source $_[0]");
  open( B, ">$_[1]" ) || die("Can't open target $_[1]");

  my $foundBetaLine            = 0;
  my $foundDebugGlobalsSection = 0;

  while ( $a = <A> ) {
    if ( $a =~ /^volume beta testing/i ) {
      print B "volume beta testing\n";
      $foundBetaLine = 1;
    }
    elsif ( $a =~ /^section debug compiler globals/i ) {
      print B "section debug compiler globals\n";
      $foundDebugGlobalsSection = 1;
    }
    elsif ( $a =~ /\t\[showtime\]/ ) {
      my (
        $second,     $minute,    $hour,
        $dayOfMonth, $month,     $yearOffset,
        $dayOfWeek,  $dayOfYear, $daylightSavings
      ) = localtime( time() );
      print B sprintf(
"\tsay \"(Debug text, detailed time stamp in case I run 2 builds in a day) %d-%d-%d %d:%02d:%02d\"\n",
        $yearOffset + 1900,
        $month + 1, $dayOfMonth, $hour, $minute, $second
      );
    }
    else {
      print "WARNING we have an odd nonrelease section: $a"
        if ( $a =~ /^section .*- not for release/i );
      print B $a;
    }
  }
  close(A);
  close(B);
  print "Warning: didn't find VOLUME BETA TESTING - NOT FOR RELEASE line!"
    if ( !$foundBetaLine );
  print "Warning: didn't find SECTION DEBUG COMPILER GLOBALS line!"
    if ( !$foundDebugGlobalsSection );
}

sub i6exe {
  if ( !$use6l{ $_[0] } ) {
    return "inform-633";
  }
  else {
    return "inform6.exe";
  }
}

sub buildDir {
  if ( !$use6l{ $_[0] } ) {
    return "c:/program files (x86)/Inform 7";
  }
  my @altDir =
    ( "c:/program files (x86)/Inform 76L", "d:/program files (x86)/Inform 7" );
  for ( 0 .. $#altDir ) {
    if ( -d "$altDir[$_]" ) { return $altDir[$_]; }
  }
}

sub getFile {
  open( A, "$_[0]" ) || die("No blorb file $_[0]");

  while ( $a = <A> ) {
    if ( $a =~ / leafname / ) {
      chomp($a);
      $a =~ s/.* leafname \"//g;
      $a =~ s/\"//g;
      return $a;
    }
  }
  return "output.$ex";
}

sub delIfThere {
  if ( -f "$_[0]" ) { print "Deleting $_[0]\n"; system("erase \"$_[0]\""); }
  else              { print "No $_[0]\n"; }
}

sub z5 {
  if ( !defined( $_[0] ) || ( $_[0] !~ /^[0-9]+$/ ) ) {
    print "WARNING: bad value passed to Z5 function.\n";
    return 0;
  }
  if ( ( $_[0] == 1 ) || ( $_[0] == 8 ) ) { return 0; }
  if ( ( $_[1] eq "debug" )   && ( $_[0] <= 5 ) ) { return 1; }
  if ( ( $_[1] eq "beta" )    && ( $_[0] <= 6 ) ) { return 1; }
  if ( ( $_[1] eq "release" ) && ( $_[0] <= 7 ) ) { return 1; }
  return 0;
}

sub p {
  if ( $i7x{ $_[0] } ) { return $i7x{ $_[0] }; }
  return $_[0];
}

sub usage {
  print <<EOT;
USAGE
-ba = base dir specified default c:/games/inform/(project name).inform
-bd = base dir specified, default c:/games/inform/beta
-inf = create INF file only, no binary build
-jb -jd -jr just build/release/debug
-e edits the icl.txt file
-np = no prefix in export file
-td/dt = debug tables on, -ndt/ntd off
EOT
  exit;
}
