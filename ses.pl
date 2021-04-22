##############################
#
#ses.pl
#
#calculates the number of open and new files in Notepad++
#
#no cmd line arguments besides e and ?

use strict;
use warnings;

#######################constant(s)
my $sourceFile = __FILE__;
my $outputFile = "c:\\writing\\scripts\\ses.txt";
my $ses    = "c:\\writing\\scripts\\ses.htm";
my $npSes  = "C:\\Users\\Andrew\\AppData\\Roaming\\Notepad++\\session.xml";
my $tabMax = 25;
my $newMax = 15;
my $tabMin = 10;
my $newMin = 5;

#######################variable(s)
my %sizes;

my @newFiles;
my @unsavedFiles;
my @savedFiles;
my $totalFiles     = 0;
my $newFiles       = 0;
my $tabsOverStreak = 0;
my $newOverStreak  = 0;
my $lastTabs       = 0;
my $lastNew        = 0;
my $newInc         = 0;
my $tabsInc        = 0;

my $count = 0;

my $newUnch  = 0;
my $tabsUnch = 0;

#########################option(s)
my $printNewFiles = 0;
my $toOutput      = 0;
my $analyze       = 0;
my $htmlGen       = 0;
my $launch        = 0;

while ( $count <= $#ARGV ) {
  my $arg = $ARGV[$count];

  for ($arg) {
    /^-?a$/ && do { $analyze = 1; $count++; next; };
    /^-?c$/ && do {
      my $cmd = 'start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" ';
      $cmd .= "\"$sourceFile\"";
      `$cmd`;
      exit();
    };
    /^-?e$/ && do { `$outputFile`; exit(); };
    /^-?h$/ && do { $htmlGen = 1; $count++; next; };
    /^-?l$/ && do { $launch  = 1; $count++; next; };
    /^-?(q|ahl|alh|hal|hla|lah|lha)$/ && do { $analyze = $htmlGen = $launch = 1; $count++; next; };
    /^-?p$/ && do { `$ses`; exit(); };
    /^-?n$/ && do { $printNewFiles = 1; $count++; next; };
    /^-?o$/ && do { $toOutput      = 1; $count++; next; };
    /^-?x$/ && do { `$npSes`; exit(); };
    usage();
  }
}

if ( $launch && !$analyze && !$htmlGen ) {
  `$ses`;
  exit();
}

open( A, $npSes ) || die("Can't open $npSes");

while ( $a = <A> ) {
  chomp($a);
  if ( $a !~ /backupfilepath/i ) { next; }
  my @b          = split( /\"/, $a );
  my $fileName   = '';
  my $fileBackup = '';
  for my $x (0..scalar(@b)-1)
  {  print($x . " of " . scalar(@b-1) . ":" . $b[$x] . "\n");
	  if ($b[$x] =~ /backupfilepath/i) { $fileBackup = $b[$x+1]; }
	  if ($b[$x] =~ /filename=/i) { $fileName = $b[$x+1]; }
  }

  if ( $a =~ /^[ \t]*<File / ) {
    $totalFiles++;
    if ( $a =~ /\"new [0-9]+\"/ ) { $newFiles++; push( @newFiles, $fileName ); }
    elsif ($fileBackup) {
      push( @unsavedFiles, $fileName );
    }
    else {
      push( @savedFiles, $fileName );
    }
    if ( $fileName =~ /^new [0-9]+$/ && ( -f "$fileBackup" ) ) {
      $sizes{$fileName} = -s "$fileBackup";
    }
  }

}

my $news = smallest();

print "TEST RESULTS:Notepad++ tabs,25,$totalFiles,0,(none yet)\n";
print "TEST RESULTS:Notepad++ new files,15,$newFiles,0,$news\n";

if ($toOutput) {
  open( A, ">>$outputFile" );
  my (
    $second,     $minute,    $hour,
    $dayOfMonth, $month,     $yearOffset,
    $dayOfWeek,  $dayOfYear, $daylightSavings
  ) = localtime( time() );
  print A sprintf(
"%d-%02d-%02d %02d:%02d:%02d: $totalFiles total files, $newFiles new files.\n",
    $yearOffset + 1900,
    $month + 1, $dayOfMonth, $hour, $minute, $second
  );
  close(A);
}

my @newFilesSort = sort { numVal($a) <=> numVal($b) } (@newFiles);

if ($printNewFiles) { print join( ", ", @newFilesSort ) . "\n"; }

if ($analyze) {
  my @b;
  open( A, "$outputFile" );
  while ( $a = <A> ) {
    chomp($a);
    $a =~ s/.*: //;
    @b = split( /, /, $a );
    for (@b) { $_ =~ s/ .*//g; }
    if   ( $b[0] > $tabMax ) { $tabsOverStreak++; }
    else                     { $tabsOverStreak = 0; }
    if   ( $b[1] > $newMax ) { $newOverStreak++; }
    else                     { $newOverStreak = 0; }
    if ( ( $b[0] > $lastTabs ) && ( $lastTabs >= $tabMin ) ) { $tabsInc++; }
    elsif ( $b[0] < $lastTabs ) { $tabsInc = 0; }
    if ( ( $b[1] > $lastNew ) && ( $lastNew >= $newMin ) ) { $newInc++; }
    elsif ( $b[1] < $lastNew ) { $newInc = 0; }
    $newUnch  = ( $lastNew == $b[1] );
    $tabsUnch = ( $lastTabs == $b[0] );
    $lastNew  = $b[1];
    $lastTabs = $b[0];

    #print "$b[0] $b[1] $tabsOverStreak $newOverStreak $tabsInc $newInc\n";
  }

  my @errs;
  if ( $newOverStreak > 1 ) {
    push( @errs, "NEW TABS too big $newOverStreak times in a row." );
  }
  if ( $newInc > 1 ) { push( @errs, "NEW TABS grew $newInc times in a row." ); }
  if ( $tabsOverStreak > 1 ) {
    push( @errs, "OVERALL TABS too big $tabsOverStreak times in a row." );
  }
  if ( $tabsInc > 1 ) {
    push( @errs, "OVERALL TABS grew $tabsInc times in a row." );
  }
  push( @errs, "No new file change since last run" ) if $newUnch;
  push( @errs, "No tab file change since last run" ) if $tabsUnch;
  if ( scalar @unsavedFiles > 1 ) {
    print "Unsaved files: " . join( ", ", @unsavedFiles ) . "<br />\n";
  }
  if ( $#errs > -1 ) {
    if ($htmlGen) {
      open( B, ">$ses" );
      print B
"<html><title>Streak Error Stuff</title><body bgcolor=red><center><font size=+5>SES.PL RESULTS:</font></center>\n";
      for (@errs) { print B "<center><font size=+3>$_</font></center>\n"; }
      print B
        "<center><font size=+3>$lastNew new, $lastTabs tabs</font></center>\n";
      print B join( ", ", @newFiles ) . "<br />\n" if ($newFiles);
	  print B "<font size=+3>BCO.PY for unsaved files</font><br />\n";
      if ( scalar @newFiles > 5 ) {
        print B "Smallest: " . smallest() . "<br />\n";
        print B "Largest: " . largest() . "<br />\n";
        print B "Leftest: " . join( ", ", @newFiles[ 0 .. 4 ] ) . "<br />\n";
        print B "Rightest: "
          . join( ", ", @newFiles[ $#newFiles - 4 .. $#newFiles ] )
          . "<br />\n";
      }
      if ( scalar @unsavedFiles > 1 ) {
        print B "Unsaved: " . join( ", ", @unsavedFiles ) . "<br />\n";
      }
      print B "</body></html>\n";
      close(B);
      if ($launch) {
        `$ses`;
      }
      else {
        print "Use -l to launch.\n";
      }
    }
    else {
      print join( "\n", @errs );
    }
  }
  else {
    print "All good!\n";
  }
}

###############################

sub numVal {
  my $temp = $_[0];
  $temp =~ s/.* //;
  return $temp;
}

sub smallest {
  my $count = 0;
  my $temp  = "Smallest: ";
  for my $x ( sort { $sizes{$a} <=> $sizes{$b} } keys %sizes ) {
    $temp .= "$x ($sizes{$x})<br />";
    $count++;
    if ( $count == 5 ) { last; }
  }
  return $temp;
}

sub largest {
  my $count = 0;
  my $temp  = "Largest: ";
  for my $x ( sort { $sizes{$b} <=> $sizes{$a} } keys %sizes ) {
    $temp .= "$x ($sizes{$x})<br />";
    $count++;
    if ( $count == 5 ) { last; }
  }
  return $temp;
}

sub usage {
  print <<EOT;
-a = analyze
-c = edit source code
-e = edit stat file
-h = to html
-l = launch HTML file created with -a -h
-n = show all new files
-o = output to stat file
-p = show previous launched file
-q = -alh (-ahl -lah etc work too)
-x = edit XML tabs file
EOT
  exit;
}
