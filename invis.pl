#invis.pl
#invisiclues style HTML generator
#
#usage invis.pl (file name, .txt optional)
#
#syntax is
#> = level 1 text heading
#? = beginning of invisiclue clump
#(no punctuation) = each successive clue
#>>, >>>, >>>> = level 2/3/4 etc. headings

use strict;
use warnings;

my @levels = ( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 );

my %exp;

###flags and such
my $updateOnly      = 1;
my $launchAfter     = 0;
my $launchRaw       = 0;
my $count           = 0;
my $forceRunThrough = 0;
my $debug           = 0;
my $launchTextFile  = 0;
my $createTextFile  = 0;
my $verbose         = 0;

#$exp{"pc"} = "compound";
my $default = "btp";
$exp{"0"} = "sc";
$exp{"1"} = "sa";
$exp{"2"} = "roi";
$exp{"3"} = "3d";

###trickier variables
my $cmd      = "";
my $invDir   = "c:\\writing\\scripts\\invis";
my $filename = "$default.txt";

while ( $count <= $#ARGV ) {
  $a = lc( $ARGV[$count] );
  for ($a) {
    /^-?\?$/ && do { usage();          exit; };
    /^-?a$/  && do { printAllFiles(0); exit; };
    /^-?la$/ && do { listAllOutput();  exit; };
    /^-?d$/ && do { $debug           = 1; $count++; next; };
    /^-?f$/ && do { $forceRunThrough = 1; $count++; next; };
    /^-?u$/ && do { $updateOnly      = 1; $count++; next; };
    /^-?[lr]+$/ && do {
      $launchAfter = ( $a =~ /l/ );
      $launchRaw   = ( $a =~ /r/ );
      $count++;
      print
"NOTE: if you're trying to run the Roiling invisiclues, you need ROI for that."
        if ( $a =~ /^-?r$/ );
      next;
    };
    /^-?s$/ && do {
      print "DEFAULT=$default\n";
      for ( sort keys %exp ) { print "$_ -> $exp{$_}\n"; }
      exit();
    };
    /^-?v$/ && do { $verbose        = 1; $count++; next; };
    /^-?e$/ && do { $launchTextFile = 1; $count++; next; };
    /^-?en$/
      && do { $createTextFile = 1; $launchTextFile = 1; $count++; next; };
    /^-/ && do { usage(); exit; };
    do {
      if   ( $exp{$a} ) { $filename = "$exp{$a}.txt"; }
      else              { $filename = "$a.txt"; }
      $count++;
    };
  }
}

if ( ( !-f "$invDir/$filename" ) && ( !$createTextFile ) ) {
  print "No filename, going to usage.\n";
  usage();
}

if ($launchTextFile) {
  my $longFile = "c:\\writing\\scripts\\invis\\$filename";
  if ( $createTextFile || ( -f $longFile ) ) {
    if ( $createTextFile && ( -f $longFile ) ) {
      print "Note: $filename already exists.\n";
    }
    if ( -f $longFile ) { `$longFile`; }
    else {
      my $cmd =
"start \"\" \"c:\\program files (x86)\\Notepad++\\Notepad++\" \"$longFile\"";
      `$cmd`;
      die($cmd);
    }
  }
  else {
    print "$filename doesn't exist. Use -en to create it by force.\n";
  }
  exit();
}

my $outname = "$invDir\\invis-$filename";
$outname =~ s/txt$/htm/gi;

my $fileShort = $filename;

if ( !-f $filename ) { $filename = "$invDir\\$filename"; }

open( A, "$filename" ) || die( "Can't open input file " . $filename );

$a = <A>;

if ( $a =~ /^out=/i ) {
  $a =~ s/^out=//i;
  chomp($a);
  $outname = "$invDir\\$a";
  $a       = <A>;
}

my $rawFile = $filename;
$rawFile =~ s/.*[\\\/]//g;
$rawFile = "c:/writing/scripts/invis/invraw-$rawFile";
$rawFile =~ s/\.txt/\.htm/g;

if ( $updateOnly && defined( -M $outname ) ) {

#if (-M $filename > 1) { print "$filename not modified in the past 24 hours.\n"; exit; }
  if ($debug) {
    print ""
      . ( ( -M $filename ) . " $filename | $outname " . ( -M $outname ) )
      . "\n";
  }

# remember that -M $filename says days since last edit, so it's not a timestamp--then the > would be <
  if ( ( -M $filename > -M $outname ) && ( !$forceRunThrough ) ) {
    if ( -M $outname > -M __FILE__ ) {
      print
"$outname was modified after $filename, but since the source was updated, we will regenerate it.\n";
    }
    else {
      print "$outname is already up to date. Run with -f to force things.\n";
      launchIt();
      exit;
    }
  }
  else {
    print "TEST RESULTS:$fileShort invisiclues,0,1,0,(TEST ALREADY RUN)\n";
  }
}

if ( $a !~ /^!/ ) {
  print(
"The first line (other than out=) must begin with a (!). That's a bit rough, but it's how it is."
  );
  exit;
}

$a =~ s/^!//g;

chomp($a);

my $header = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>
' . $a . '
</title>

</head>
<body>

<noscript><p style="color:#633;font-weight:bold;">This page requires JavaScript enabled in your browser to see the hints.</p></noscript>

<center><h1>' . $a . '</h1></center>
<center><h2>Invisiclues hint javascript thanks to <a href="http://nitku.net/blog">Undo Restart Restore</a></h2></center>

<center>[NOTE: tab/enter may be quicker to reveal clues than futzing with the mouse.]</center>
';

my $footer = '</body>
</html>';

open( B, ">$outname" ) || die("Can't write to $outname.");
print B $header;

my $lastLev           = 0;
my $temp              = 0;
my $otl               = 0;
my $lastWasInvisiclue = 0;
my $theDir            = "";

while ( $a = <A> ) {
  print $a if $verbose;
  chomp($a);
  if ( $a =~ /^->/ ) { $a =~ s/^->//g; $theDir = $a; next; }
  if ( $a =~ /^\#/ ) { next; }    #comments
  if ( $a =~ /^;/ )  { last; }
  $a =~ s/ *##regignore.*//;      # regression ignore, for testing elsewhere

  if ( $a !~ /^[\?>]/ ) {
    $levels[$lastLev]++;
    $a   = addBoldItalic($a);
    $otl = currentOutline(@levels);
    print B
"<a href=\"#\" onclick=\"document.getElementById('$otl').style.display = 'block'; this.style.display = 'none'; return false;\">"
      . cbr()
      . "Click to show next hint</a></div>
<div id=\"$otl\" style=\"display:none;\">$a\n";
    $lastWasInvisiclue = 1;
    next;
  }
  if ($lastWasInvisiclue) { print B "</div>\n"; }
  $lastWasInvisiclue = 0;
  if ( $a =~ /^\?/ ) {
    my $ll = $lastLev + 1;
    $a =~ s/^.//g;
    $levels[$lastLev]++;
    $otl = currentOutline(@levels);
    print B "<h$ll>$a</h$ll>\n<div>\n";
    next;
  }
  if ($debug) { print "Outlining $a.\n"; }
  $temp = $a;
  my $times = $temp =~ tr/>//;
  $temp =~ s/>//g;

  #print "1 $a\n2 $temp\n";
  $levels[$times]++;
  for ( $times + 1 .. 9 ) { @levels[$_] = 0; }
  $otl = currentOutline(@levels);
  if ($debug) { print "Element number $otl!!\n"; }
  my $t2 = $lastLev - $times;

  if ($debug) { print "Current level $times Last level $lastLev\n"; }

  if ( $t2 >= 0 ) {
    for ( 0 .. $t2 ) {
      if ( ( $_ > 0 ) && ($debug) ) { print "Playing catchup on $otl.\n"; }
      print B "</div>\n";
    }
  }
  $lastLev = $times;

  if ( $times == 1 ) { print B "<hr>\n"; }

  print B "<h$times>$temp</h$times>\n";
  print B
"<div><a href=\"#\" onclick=\"document.getElementById('$otl').style.display = 'block'; this.style.display = 'none'; return false;\">Open outline</a></div>\n<div id=\"$otl\" style=\"display:none;\">\n";
}

for ( 1 .. $lastLev ) { print B "</div>\n"; }

print B $footer;

close(B);

close(A);

open( B, "$outname" );

open( C, ">$rawFile" );

while ( $a = <B> ) {
  $a =~ s/<div[^>]*>//g;
  $a =~ s/<\/div>//g;
  if ( $a =~ /^<a href/ ) { print C "<br />\n"; }
  else {
    print C $a;
  }
}

close(B);
close(C);

launchIt();

if ($theDir) {
  print "Copying to $theDir.\n";
  my $outshort = $outname;
  $outshort =~ s/.*[\\\/]//g;
  $cmd = "copy $outname \"$theDir/$outshort\"";
  $cmd =~ s/\//\\/g;
  print "$cmd\n";
  `$cmd`;
}

sub currentOutline {
  my $retString;

  #print "@_ is the current level.\n";
  for my $q ( 1 .. 9 ) {
    if ( $_[$q] == 0 ) { return $retString; }
    elsif ( $q == 1 ) { $retString = "$_[$q]"; }
    else              { $retString .= ".$_[$q]"; }
  }
  print "Oops missed.\n";
}

sub cbr {
  if ($lastWasInvisiclue) { return "<br>"; }
  return "";
}

sub printAllFiles {
  opendir( DIR, $invDir );
  my @dfi = sort( readdir DIR );
  for my $fi (@dfi) {
    if ( $fi =~ /\.txt/ ) {
      if ( $_[0] ) { $fi =~ s/\.txt//g; print " $fi"; }
      else         { print "$fi\n"; }
    }
  }
}

sub listAllOutput {
  opendir( DIR, $invDir );
  my @dfi = sort( readdir DIR );
  my $dname;
  my $fname;

  for my $fi (@dfi) {
    $dname = "(default)";
    $fname = "(default)";
    if ( !-f "$invDir\\$fi" ) { next; }
    if ( $fi !~ /txt$/i )     { next; }
    open( A, "$invDir\\$fi" );
    while ( $a = <A> ) {
      if ( $a =~ /^out=/ ) { $fname = $a; $fname =~ s/^out=//; chomp($fname); }
      if ( $a =~ /^->/ ) {
        $dname = $a;
        $dname =~ s/^->//;
        chomp($dname);
        $dname =~ s/\//\\/g;
      }
    }
    close(A);
    print "$invDir\\$fi: $dname\\$fname\n";
  }
}

sub launchIt {
  if ($launchAfter) { `$outname`; }
  if ($launchRaw)   { `$rawFile`; }
}

sub addBoldItalic {
  my $temp = $_[0];
  return $_[0] unless $temp =~ /[_\@]/;
  my $ital = () = $temp =~ /_/g;
  my $bold = () = $temp =~ /\@/g;
  my $openTag = 0;

  if ( ( $ital % 2 ) or ( $bold % 2 ) ) {
    warn("Odd bold/italic, not converting line $. $_[0]");
    return $_[0];
  }
  while ( $temp =~ /\@/ ) {
    $temp =~ s/\@/"<" . ($openTag ? "\/" : "") . "b>"/e;
    $openTag = !$openTag;
  }
  while ( $temp =~ /\_/ ) {
    $temp =~ s/\_/"<" . ($openTag ? "\/" : "") . "i>"/e;
    $openTag = !$openTag;
  }
  return $temp;
}

sub usage {
  print <<EOT;
===========================USAGE
-a  = show all files
-d  = debug
-e  = edits the next file (e.g. -e btp edits \\writing\\scripts\\invis\\btp)
-en = edits a new text file (e.g. -e btp edits \\writing\\scripts\\invis\\btp)
-f  = force a redo if HTM file's mod date >= the generating file
-l  = launch HTM invisiclues after
-la = list all invisicules with output
-r  = launch raw (e.g. spoiler file showing everything, launched after -l)
-s  = print shortcuts
-u  = update only (opposite of -f, currently the default)
-v  = verbose output
EOT

  print "Current files in directory:";
  printAllFiles(1);
  print "\n";
  exit;
}
