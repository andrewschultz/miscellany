#####################################
#
#i7.pm
#
#perl module
#

package i7;

use strict;
use warnings;

use Exporter;

use vars qw($VERSION @ISA @EXPORT @EXPORT_OK %EXPORT_TAGS);

$VERSION     = 1.00;
@ISA         = qw(Exporter);
@EXPORT      = qw(%i7x %xtraFiles tableFile cutArt openWinOrUnix);
#@EXPORT_OK   = qw(i7x);

our %i7x = ( "12" => "shuffling",
"sa" => "shuffling",
"roi" => "roiling",
"s13" => "roiling",
"3" => "threediopolis",
"13" => "threediopolis",
"14" => "ugly-oafs",
"oafs" => "ugly-oafs",
"s15" => "dirk",
"15" => "compound",
"4" => "fourdiopolis",
"s16" => "fourdiopolis",
"16" => "slicker-city",
"bs" => "btp-st",
"s17" => "btp-st",
"btp" => "buck-the-past"
);

our %xtraFiles;

$xtraFiles{"buck-the-past"} = ["c:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions\\Andrew Schultz\\Buck the Past tables.i7x"];
$xtraFiles{"slicker-city"} = ["c:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions\\Andrew Schultz\\Slicker City tables.i7x"];
$xtraFiles{"compound"} = ["c:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions\\Andrew Schultz\\Compound tables.i7x"];
$xtraFiles{"shuffling"} = ["c:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions\\Andrew Schultz\\Shuffling nudges.i7x", "c:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions\\Andrew Schultz\\Shuffling random text.i7x"];
$xtraFiles{"roiling"} = ["c:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions\\Andrew Schultz\\Roiling nudges.i7x", "c:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions\\Andrew Schultz\\Roiling random text.i7x"];

sub cutArt
{
  my $die = 0;
  my $temp = $_[0];
  if ($temp =~ /^a (thing\t|for )/) { return $_[0]; } #A for effort is a special case
  $temp =~ s/^(a thing called |a |the )//gi;
  return $temp;
}

sub openWinOrUnix
{
  open($_[0], $_[1]);
  my $line = <$_[0]>;
  if ($line !~ /\r/)
  {
    close($_[0]);
	open($_[0], $_[1]);
	binmode($_[0]);
  }
}

sub tableFile
{
  my $temp = $_[0];
  $temp =~ s/-/ /g;
  return "c:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions\\Andrew Schultz\\$temp tables.i7x";
}

1;
