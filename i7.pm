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
@EXPORT      = qw(%i7x %i7xr @i7gh @i7bb %xtraFiles tableFile cutArt openWinOrUnix sourceFile tx $np);
#@EXPORT_OK   = qw(i7x $np);

our %i7x = ( "12" => "shuffling",
  "sa" => "shuffling",
  "roi" => "roiling",
  "s13" => "roiling",
  "3" => "threediopolis",
  "3d" => "threediopolis",
  "13" => "threediopolis",
  "14" => "ugly-oafs",
  "oafs" => "ugly-oafs",
  "s15" => "dirk",
  "15" => "compound",
  "pc" => "compound",
  "4" => "fourdiopolis",
  "4d" => "fourdiopolis",
  "s16" => "fourdiopolis",
  "16" => "slicker-city",
  "bs" => "btp-st",
  "s17" => "btp-st",
  "btp" => "buck-the-past"
);

our %i7xr = ( "shuffling" => "sa",
  "roiling" => "roi",
  "threediopolis" => "3d",
  "fourdiopolis" => "4d",
  "ugly-oafs" => "uo",
  "compound" => "pc",
  "slicker-city" =>"sc" ,
  "btp-st" =>"bs" ,
  "btp" => "buck-the-past"
);

our @i7gh = ("threediopolis", "short-games", "fourdiopolis", "stale-tales-slate", "the-problems-compound", "slicker-city", "misc", "ugly-oafs", "dirk", "trizbort", "writing");
our @i7bb = ("seeker-status", "buck-the-past",  "curate");

our %xtraFiles;

$xtraFiles{"buck-the-past"} = ["c:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions\\Andrew Schultz\\Buck the Past tables.i7x"];
$xtraFiles{"slicker-city"} = ["c:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions\\Andrew Schultz\\Slicker City tables.i7x"];
$xtraFiles{"compound"} = ["c:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions\\Andrew Schultz\\Compound tables.i7x"];
$xtraFiles{"shuffling"} = ["c:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions\\Andrew Schultz\\Shuffling nudges.i7x", "c:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions\\Andrew Schultz\\Shuffling random text.i7x"];
$xtraFiles{"roiling"} = ["c:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions\\Andrew Schultz\\Roiling nudges.i7x", "c:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions\\Andrew Schultz\\Roiling random text.i7x"];

our $np = "\"C:\\Program Files (x86)\\Notepad++\\notepad++.exe\"";

############################################
#cuts the leading article off an object definition
#

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
  my $file = $_[0];
  open($file, "<", $_[1]);
  binmode($file);
  my $line = <$file>;
  close($file);

  open($_[0], '<', $_[1]);
  if ($line !~ /\r/)
  {
	binmode($_[0]);
	return 0;
  }
  return 1;
}

sub tableFile
{
  my $temp = $_[0];
  $temp =~ s/-/ /g;
  return "c:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions\\Andrew Schultz\\$temp tables.i7x";
}

sub tx
{
  my $temp = $_[0];
  $temp =~ s/\.[^\.]*$/.txt/i;
  return $temp;
}

sub sourceFile
{
  my $temp = $_[0];
  $temp = $i7x{$temp} if defined($i7x{$temp});
  return "c:\\games\\inform\\$temp.inform\\Source\\story.ni";
}

1;
