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

my @levels = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0);

my %exp;

###flags and such
my $updateOnly = 1;
my $launchAfter = 1;
my $launchRaw = 1;
my $count = 0;
my $forceRunThrough = 0;
my $debug = 0;

###trickier variables
my $cmd = "";
my $invDir = "c:\\writing\\scripts\\invis";
my $filename = "";

#$exp{"pc"} = "compound";
my $default = "pc";
$exp{"1"} = "sa";
$exp{"2"} = "roi";
$exp{"3"} = "3d";

while ($count <= $#ARGV)
{
  $a = $ARGV[$count];
  for ($a)
  {
  /-a/ && do { printAllFiles(); exit; };
  /-d/ && do { $debug = 1; $count++; next; };
  /-f/ && do { $forceRunThrough = 1; $count++; next; };
  /-u/ && do { $updateOnly = 1; $count++; next; };
  /-l/ && do { $launchAfter = 1; $count++; next; };
  /-r/ && do { $launchRaw = 1; $count++; next; };
  /^-?e$/ && do { `$invDir\\$ARGV[$count+1].txt`; exit; };
  do { if ($exp{$a}) { $filename = "$exp{$a}.txt"; } else { $filename = "$a.txt"; } $count++; };
  }
}

if (! -f "$invDir/$filename") { print "No filename, going to usage.\n"; usage(); }

my $outname = "$invDir\\invis-$filename";
$outname =~ s/txt$/htm/gi;

my $fileShort = $filename;

if (! -f $filename) { $filename = "$invDir\\$filename"; }

open(A, "$filename") || die ("Can't open input file " . $filename);

$a = <A>;

if ($a =~ /^out=/i) { $a =~ s/^out=//i; chomp($a); $outname = "c:\\writing\\scripts\\invis\\$a"; $a = <A>; }

if ($updateOnly && defined(-M $outname))
{
  #if (-M $filename > 1) { print "$filename not modified in the past 24 hours.\n"; exit; }
  if ($debug) { print "" . ((-M $filename) . " $filename | $outname " . (-M $outname)) . "\n"; }
  if ((-M $filename > -M $outname) && (!$forceRunThrough)) { print "$outname is already up to date. Run with -f to force things.\n"; exit; }
  else { print "TEST RESULTS:$fileShort invisiclues,0,1,0,(TEST ALREADY RUN)\n"; }
}

if ($a !~ /^!/) { print ("The first line (other than out=) must begin with a (!). That's a bit rough, but it's how it is."); exit; }

$a =~ s/^!//g;

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

open(B, ">$outname") || die ("Can't write to $outname.");
print B $header;

my $lastLev = 0; my $temp = 0; my $otl = 0;
my $lastWasInvisiclue = 0;
my $theDir = "";

while ($a = <A>)
{
  chomp($a);
  if ($a =~ /^->/) { $a =~ s/^->//g; $theDir = $a; next; }
  if ($a =~ /^\#/) { next; } #comments
  if ($a =~ /;/) { last; }
  if ($a !~ /^[\?>]/)
  {
    $levels[$lastLev]++;
    $otl = currentOutline(@levels);
    print B "<a href=\"#\" onclick=\"document.getElementById('$otl').style.display = 'block'; this.style.display = 'none'; return false;\">" . cbr() . "Click to show next hint</a></div>
<div id=\"$otl\" style=\"display:none;\">$a\n";
    $lastWasInvisiclue = 1;
    next;
  }
  if ($lastWasInvisiclue) { print B "</div>\n"; }
  $lastWasInvisiclue = 0;
  if ($a =~ /^\?/)
  {
    my $ll = $lastLev + 1;
    $a =~ s/^.//g;
    $levels[$lastLev]++;
    $otl = currentOutline(@levels);
    print B "<h$ll>$a</h$ll>\n<div>\n";
    next;
  }
  print "Outlining $a.\n";
  $temp = $a;
  my $times = $temp =~ tr/>//;
  $temp =~ s/>//g;
  #print "1 $a\n2 $temp\n";
  $levels[$times]++;
  for ($times+1 .. 9) { @levels[$_] = 0; }
  $otl = currentOutline(@levels);
  print "$otl!!\n";
  my $t2 = $lastLev - $times;

  print "Current level $times Last level $lastLev\n";

  if ($t2 >= 0)
  {
  for (0..$t2)
  {
  if ($_ > 0) { print "Playing catchup on $otl.\n"; }
  print B "</div>\n";
  }
  }
  $lastLev = $times;
  
  if ($times == 1) { print B "<hr>\n"; }

  print B "<h$times>$temp</h$times>\n";
  print B "<div><a href=\"#\" onclick=\"document.getElementById('$otl').style.display = 'block'; this.style.display = 'none'; return false;\">Open outline</a></div>\n<div id=\"$otl\" style=\"display:none;\">\n";
}

for (1..$lastLev) { print B "</div>\n"; }

print B $footer;

close(B);

close(A);

open(B, "$outname");

my $rawFile = $filename;
$rawFile =~ s/.*[\\\/]//g;
$rawFile = "c:/writing/scripts/invis/invraw-$rawFile"; $rawFile =~ s/\.txt/\.htm/g;

open(C, ">$rawFile");

while ($a = <B>)
{
  $a =~ s/<div[^>]*>//g;
  $a =~ s/<\/div>//g;
  if ($a =~ /^<a href/) { print C "<br />\n"; }
  else
  {
  print C $a;
  }
}

close(B);
close(C);

if ($launchAfter) { `$outname`; }
if ($launchRaw) { `$rawFile`; }

if ($theDir)
{
  print "Copying to $theDir.\n";
  my $outshort = $outname; $outshort =~ s/.*[\\\/]//g;
  $cmd = "copy $outname \"$theDir/$outshort\"";
  $cmd =~ s/\//\\/g;
  print "$cmd\n";
  `$cmd`;
}

sub currentOutline
{
  my $retString;
  #print "@_ is the current level.\n";
  for my $q (1..9)
  {
    if ($_[$q] == 0) { return $retString; }
    elsif ($q == 1) { $retString = "$_[$q]"; } else
    { $retString .= ".$_[$q]"; }
  }
  print "Oops missed.\n";
}

sub cbr
{
  if ($lastWasInvisiclue) { return "<br>"; }
  return "";
}

sub printAllFiles
{
  opendir(DIR, "c:\\writing\\scripts\\invis");
  my @dfi = readdir DIR;
  for my $fi (@dfi) { if ($fi =~ /\.txt/) { print "$fi\n"; } }
}

sub usage
{
print<<EOT;
EOT
exit;
}