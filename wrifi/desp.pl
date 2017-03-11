####################################
#
# despacer desp.pl
#
# removes spaces in a GameFAQs FAQ and also does outline adjusting stuff
# changes emails too, etc.
#

use strict;
use warnings;
use File::Copy qw (copy);

if ($#ARGV == -1) { die ("Need name of file."); }

my $filename = $ARGV[0];
my $outfile = $filename;

$outfile =~ s/\./-despace\./;

if ($outfile eq $filename) { $outfile .= "-despace"; }

my $outFileText = "";

my $lastLineText = 0;
my $spacesFound = 0;
my $outlines = 0;

my $copyBackOver = 1;

my $parzap = 0;

if (!defined($ARGV[0])) { die ("Need a file name to proceed."); }

if (defined($ARGV[1]))
{
  if ($ARGV[1] =~ /^-?y$/i) { $copyBackOver = 1; }
  if ($ARGV[1] =~ /^-?n$/i) { $copyBackOver = 0; }
}

open(A, "$ARGV[0]") || die ("Can't find $ARGV[0].");

print "$filename to $outfile\n";

my $gotMarkup = 0;

while (my $line = <A>)
{
  if ($line =~ /;format:gf-markup/) { die ("This has already been converted. Delete the first line to try again."); }
  if ($line =~ /  OUTLINE/) { die ("You may want to delete your manual outline so that the ='s are not duplicated."); }
  $line =~ s/schultza\@earthlink.net/blurglecruncheno\@gmali.cmo \(anti spam letter flip\)/g;

  ###############fix numerical outlines to ='s
  if (($line =~ /^(  )*[0-9].*\./) && ($line !~ /[a-z]/))
  {
    $outlines++;
    chomp($line);
    my $line2 = $line;
	$line2 =~ s/.*\. *//;
    $line =~ s/\..*//; my @l = split(/-/, $line);
	$outFileText .= "=" x ($#l + 2) . $line2 . "=" x ($#l + 2) . "\n";
	next;
  }

   if ($line eq ";format:gf-markup\n") { $gotMarkup = 1; }
  $line =~ s/schultw.andrez\@sbcglobal.net/blurglecruncheno\@gmail\.cmo \(anti spam letter flip\)/g; # change email address
  $line =~ s/schultz.andrew\@sbcglobal.net/blurglecruncheno\@gmail\.cmo \(anti spam letter flip\)/g; # change email address
  $line =~ s/schultza\@earthlink.net/blurglecruncheno\@gmail\.cmo \(anti spam letter flip\)/g; # change email address
  if (($line =~ /[a-z\. '\\"\*\_]/i) && (length($line) > 65) && ($line !~ /^[\#\*\|]/))
  {
    if (($parzap == 1) && ($line =~ /^  [A-Z]/)) { $line =~ s/^  //g; }
    $line =~ s/\.  /\. /g;
    $lastLineText = 1;
    chomp($line);
    $spacesFound++;
	if ($outFileText =~ /[a-z]$/i) { $outFileText .= " "
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
print "Outline sections found: $outlines\n";

if ($copyBackOver)
{
  print "Copying $outfile back over.\n";
  copy($outfile, $filename);
  if (-f "$outfile" && -f "$filename") { unlink $outfile; print "Deleting $outfile\n"; }
}
