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
use POSIX;

use lib 'c:/writing/scripts';
use mytools;

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
my $questionLast    = 0;
my $ghAfter         = 0;
my $launchPost      = "";
my $github_recommended = 1;
my $github_set = 0;

my $questionsThisTime = 0;
my $answersThisTime   = 0;

#$exp{"pc"} = "compound";
$exp{"0"}  = "sc";
$exp{"1"}  = "sa";
$exp{"2"}  = "roi";
$exp{"ro"} = "roi";
$exp{"3"}  = "3d";
$exp{"up"} = "pu";

###trickier variables
my $cmd       = "";
my $invDir    = "c:\\writing\\scripts\\invis";
my $default   = "ai";
my $filename  = "$invDir\\$default.txt";
my $invisData = "$invDir\\invis.txt";

open( A, $invisData ) || warn("No $invisData file to read.");
my $line;

OUTER:
while ( $line = <A> ) {
  chomp($line);
  for ($line) {
    /^DEFAULT=/ && do {
      if ( $line =~ /^default=/i ) {
        ( $default = $line ) =~ s/.*=//;
      }
    };
    /^;/ && do { last OUTER; };
    /^#/ && do { continue; };
  }
}

while ( $count <= $#ARGV ) {
  $a = lc( $ARGV[$count] );
  for ($a) {
    do {
      if ( defined( $exp{$a} ) ) {
        if ( -f "$invDir\\$filename" ) {
          $filename = "$invDir\\$exp{$a}.txt";
          print "$a mapped to $exp{$a}...\n";
          $count++;
          $launchPost = $exp{$a};
          next;
        }
      }
      elsif ( -f "$invDir\\$a.txt" ) {
        print "Getting filename $a.txt in invisiclues directory.\n";
        $filename = "$invDir\\$a.txt";
        $count++;
        next;
      }
    };
    /^-?\?$/ && do { usage(); exit; };
    /^-?gh$/ && do { $ghAfter = 1; $count++; next; };
    /^-?(gn|ng)$/ && do { $github_recommended = 0; $github_set = 1; $count++; next; };
    /^-?a$/  && do { printAllFiles(0); exit; };
    /^-?la$/ && do { listAllOutput();  exit; };
    /^-?d$/ && do { $debug           = 1; $count++; next; };
    /^-?f$/ && do { $forceRunThrough = 1; $count++; next; };
    /^-?u$/ && do { $updateOnly      = 1; $count++; next; };
    /^-?[lr]+$/
      && do
    { # this must be after the filename check since RL = roiling logic. Unfortunately, things clashed.
      $launchAfter = () = $a =~ /l/g;
      $launchRaw   = () = $a =~ /r/g;
      die(
        "The -lr feature can't have more than one or two L's or R's. Bailing.")
        if ( $launchAfter > 1 or $launchRaw > 1 );
      $count++;
      print
"NOTE: if you're trying to run the Roiling invisiclues, you need ROI for that. LR flags are to launch after (l) or launch the raw file (r) or both, combined.\n"
        if ( $a =~ /^-?r$/ );
      next;
    };
    /^-?s$/ && do {
      print "DEFAULT=$default\n";
      for ( sort keys %exp ) { print "$_ -> $exp{$_}\n"; }
      exit();
    };
    /^-?v$/     && do { $verbose        = 1; $count++; next; };
    /^-?e(d)?$/ && do { $launchTextFile = 1; $count++; next; };
    /^-?en$/
      && do { $createTextFile = 1; $launchTextFile = 1; $count++; next; };
    usage();
    exit();
  }
}

if ( ( !-f "$filename" ) && ( !$createTextFile ) ) {
  print "No valid filename $filename, going to usage.\n";
  usage();
}

if ($launchTextFile) {
  if ( $createTextFile || ( -f $filename ) ) {
    if ( $createTextFile && ( -f $filename ) ) {
      print "Note: $filename already exists.\n";
    }
    if ( -f $filename ) { `$filename`; }
    else {
      my $cmd =
"start \"\" \"c:\\program files\\Notepad++\\Notepad++\" \"$filename\"";
      `$cmd`;
      die($cmd);
    }
  }
  else {
    print "$filename doesn't exist. Use -en to create it by force.\n";
  }
  exit();
}

my $outname = "";

( my $fileShort = $filename ) =~ s/.*[\\\/]//;

if ( ( -f $filename )
  && ( getcwd() ne "c:\\writing\\scripts\\invis" )
  && ( getcwd() ne "c:\\writing\\scripts" )
  && ( $filename !~ /[\\\/]/ ) )
{
  print
"WARNING there is a $filename in the local directory but I'm using the one in $invDir.\n";
}

open( A, "$filename" ) || die( "Can't open input file " . $filename );

my $rawFile = $filename;
$rawFile =~ s/.*[\\\/]//g;
$rawFile = "c:/writing/scripts/invis/invraw-$rawFile";
$rawFile =~ s/\.txt/\.htm/g;

my $theDir = "";
my $title  = "NO TITLE DEFINED, USE !";

while ( $a = <A> ) {
  last if $a =~ /end ?header/i;
  if ( $a =~ /^->/ ) { chomp($a); $a =~ s/^->//g; $theDir = $a; next; }
  if ( $a =~ /^>/ ) {
    print
"WARNING: no line with 'end header' text in $filename.\nNot a critical error, but it's good form to add such a line. With or without a space between end and header.\n";
    seek( A, -length($a) - 1, 1 )
      ;    # ?? not sure what to do here if something is in UNIX mode
    last;
  }
  if ( $a =~ /^!/ ) {
    $title = $a;
    $title =~ s/^!//;
    next;
  }

  if ($a =~ /^no-github/) { $github_recommended = 0; $github_set = 1; next; }
  if ($a =~ /^yes-github/) { $github_recommended = 1; $github_set = 1; next; }

  if ($a =~ /^outdir=/i) {
    ($theDir = $a) =~ s/.*=//;
	chomp($theDir);
  }

  if ($a =~ /^out(file)?=/i) {
	if ($outname) { print "Warning: redefinition of outfile from $outname at line $. of $filename.\n"; }
	my $prefix = ($a =~ /^outfile/ ? "c:/writing/scripts/invis//" : "$theDir\\");
	die("Need to define a directory before out=") if (($a =~ /^out/) && (!$theDir));
    $a =~ s/^out.*?=//i;
    chomp($a);
    $outname = "" . $prefix . $a;
	if (($outname =~ /github/i) != ($github_recommended)) {
	printf("WARNING: OUTNAME of $outname doesn't %s github as it should.\n", $github_recommended ? "have" : "avoid");
	}
  }

  if ( $a =~ /^raw=/i ) {
    $a =~ s/^raw=//i;
    chomp($a);
    $rawFile = "$invDir\\$a";
    next;
  }
}

if ($outname eq "") {
  $outname = "$invDir\\invis-$filename";
  $outname =~ s/txt$/htm/gi;
  print "No outname defined. Going with default $outname.\n";
}

my $file_link = follow_symlink($filename);
my $out_link = follow_symlink($outname);

if ( $updateOnly && defined( -M $out_link ) ) {

#if (-M $filename > 1) { print "$filename not modified in the past 24 hours.\n"; exit; }
  if ($debug) {
    print ""
      . ( ( -M $file_link ) . " $filename | $outname " . ( -M $out_link ) )
      . "\n";
  }

# remember that -M $filename says days since last edit, so it's not a timestamp--then the > would be <
  if ( ( -M $file_link > -M $out_link ) && ( !$forceRunThrough ) ) {
    if ( -M $out_link > -M __FILE__ ) {
      print
"$outname was modified after $filename, but since the source was updated, we will regenerate it.\n";
    }
    else {
  my $daydelt = (-M $file_link) - (-M $out_link);
      print
"$outname is already up to date. Its timestamp is after $filename by " . ($daydelt < 1 ? sprintf("%d seconds", $daydelt * 86400 + .5) : sprintf("%.2f days", $daydelt)) . ". Run with -f to force things.\n";
      launchIt();
      exit;
    }
  }
  else {
    print "TEST RESULTS:$fileShort invisiclues,0,1,0,(TEST ALREADY RUN)\n";
  }
}

my $header = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>
' . $title . '
</title>

</head>
<body>

<noscript><p style="color:#633;font-weight:bold;">This page requires JavaScript enabled in your browser to see the hints.</p></noscript>

<center><h1>' . $title . '</h1></center>
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
my $skip_lines = 0;

while ( $a = <A> ) {
  print $a if $verbose;
  chomp($a);
  if ( $a =~ /^\#/ ) { next; }    #comments
  if ( $a =~ /^;/ )  { last; }
  if ($a =~ /^#skipstart/) {
    $skip_lines = 1;
	continue;
	}
  if ($a =~ /^#skipend/) {
    $skip_lines = 0;
	continue;
	}
  continue if $skip_lines;
  $a =~ s/ *##regignore.*//;      # regression ignore, for testing elsewhere

  if ( $a !~ /^[\?>]/ ) {
    if ( !$questionLast ) {
      print "WARNING line $. has no question before it: $a\n";
      $questionLast = 1;          # don't repeat the error printout
    }
    $answersThisTime++;
    $a = addBoldItalic($a);
    $otl = currentOutline( \@levels, $questionsThisTime, $answersThisTime );
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
    $questionsThisTime++;
    $answersThisTime = 0;
    $questionLast    = 1;
    my $ll = $lastLev + 1;
    $a =~ s/^.//g;
    $otl = currentOutline( \@levels, $questionsThisTime, $answersThisTime );
    print B "<h$ll>$a</h$ll>\n<div>\n";
    next;
  }
  $questionLast = $questionsThisTime = $answersThisTime = 0;
  if ($debug) { print "Outlining $a.\n"; }
  $temp = $a;
  my $times = $temp =~ tr/>//;
  $temp =~ s/>//g;

  #print "1 $a\n2 $temp\n";
  $levels[$times]++;
  for ( $times + 1 .. 9 ) { @levels[$_] = 0; }
  $otl = currentOutline( \@levels, $questionsThisTime, $answersThisTime );

  # if ($debug) { print "Element number $otl!!\n"; }
  my $t2 = $lastLev - $times;

  if ($debug) { print "Current level $times Last level $lastLev ... $otl\n"; }

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

if (!$github_set) { print "WARNING: no-github and yes-github not set. Default is " . ($github_recommended ? "have" : "avoid") . ".\n"; }

launchIt();

  if ($ghAfter) {
    print "Running gh.pl $launchPost...\n";
    my $q = `gh.pl $launchPost`;
    print $q;
  }

# start subroutines

sub currentOutline {
  my @ary = @{ $_[0] };
  my $retString;

  #print "@_ is the current level.\n";
  for my $q ( 1 .. 9 ) {
    if ( $ary[$q] == 0 ) { return "$retString.q.$_[1].$_[2]"; }
    elsif ( $q == 1 ) { $retString = "$ary[$q]"; }
    else              { $retString .= ".$ary[$q]"; }
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
    if ( ( $fi =~ /\.txt/i ) && ( $fi !~ /\.bak/i ) ) {
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
  my $full_name;

  for my $fi (@dfi) {
    $dname = "(default)";
    $fname = "(default)";
    if ( !-f "$invDir\\$fi" ) { next; }
    if ( $fi !~ /txt$/i )     { next; }
    open( A, "$invDir\\$fi" );
    while ( $a = <A> ) {
	  if ($a =~ /^outfile=/) { $full_name = $a; $full_name =~ s/^outfile=//; chomp($full_name); last; }
      if ( $a =~ /^out=/ ) { $fname = $a; $fname =~ s/^out=//; chomp($fname); }
      if ( $a =~ /^->/ ) {
        $dname = $a;
        $dname =~ s/^->//;
        chomp($dname);
        $dname =~ s/\//\\/g;
      }
    }
    close(A);
	if (!$full_name) { $full_name = "$dname\\$fname"; }
    print "$invDir\\$fi: $full_name\n";
  }
}

sub launchIt {
  if ($launchAfter) { `$outname`; }
  if ($launchRaw)   { `$rawFile`; }
}

sub addBoldItalic {
  my $temp = $_[0];
  return $_[0] unless $temp =~ /[_\@]/ || $temp =~ /\\n/;
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
  $temp =~ s/\\n/\n/g;    # backslash-n mapped to CR
  return $temp;
}

sub usage {
  print <<EOT;
===========================USAGE
-a  = show all files
-d  = debug
-e  = (ed) edits the next file (e.g. -e btp edits \\writing\\scripts\\invis\\btp.txt)
-en = edits a new text file (e.g. -e btp edits \\writing\\scripts\\invis\\btp.txt)
-f  = force a redo if HTM file's mod date >= the generating file
-gh = runs GH post-invis processing
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
  print "Current shortcuts:";
  print join( ', ', ( map { "$_=$exp{$_}" } sort keys %exp ) );
  print "\n";
  exit;
}
