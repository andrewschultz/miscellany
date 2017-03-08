####################################
#
# despacer desp.pl
#
# removes spaces in a GameFAQs FAQ and also does outline adjusting stuff
# changes emails too, etc.
#

use strict;
use warnings;

if ($#ARGV == -1) { die ("Need name of file."); }

my $filename = $ARGV[0];
my $outfile = $filename;
$outfile =~ s/\./-despace\./;
if ($outfile eq $filename) { $outfile .= "-despace";

my $outFileText = "";

my $lastLineText = 0;
my $spacesFound = 0;

my $copyBackOver = 1;

my $parzap = 0;

if (!defined($ARGV[0])) { die ("Need a file name to proceed."); }

open(A, "$ARGV[0]") || die ("Can't find $ARGV[0].");

print "$filename to $outfile\n";

my $gotMarkup = 0;

while (my $line = <A>)
{
  $line =~ s/schultz.andrew\@earthlink.net/blurglecruncheno\@gmali.cmo \(anti spam typo\)/g;

  ###############fix numerical outlines to ='s
  if (($line =~ /^(  )*[0-9].*\./) && ($line !~ /[a-z]/))
  {
    chomp($line);
    my $line2 = $line;
	$line2 =~ s/.*\. *//;
    $line =~ s/\..*//; my @l = split(/-/, $line);
	$outFileText .= "=" x ($#l + 2) . $line2 . "=" x ($#l + 2) . "\n";
	next;
  }

   if ($line eq ";format:gf-markup\n") { $gotMarkup = 1; }
  $line =~ s/schultz.andrew\@sbcglobal.net/blurglecruncheno\@gmail\.cmo/g; # change email address
  $line =~ s/schultza\@earthlink.net/blurglecruncheno\@gmail\.cmo/g; # change email address
  if (($line =~ /[a-z\. '\\"\*\_]/i) && (length($line) > 65) && ($line !~ /^[\#\*\|]/))
  {
    if (($parzap == 1) && ($line =~ /^  [A-Z]/)) { $line =~ s/^  //g; }
    $line =~ s/\.  /\. /g;
    $lastLineText = 1;
    chomp($line);
    $spacesFound++;
    $outFileText .= $line;
  }
  else
  {
    if ($lastLineText && (length($line) < 2)) { $outFileText .= "\n"; $spacesFound--; }
    $lastLineText = 0;
    $outFileText .= $line;
  }
}

open(B, ">$outfile");
if (!$gotMarkup) { print B ";format:gf-markup\n\n"; }
print B $outFileText;
close(B);

printf("%d bytes to %d bytes, total spaces = %d.\n", -s "$filename", -s "$outfile", $spacesFound);

if ($copyBackOver)
{
  print "Copying $outfile back over.";
  copy($outfile, $filename);
}
