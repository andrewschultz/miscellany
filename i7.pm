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
@EXPORT      = qw(@titleWords $np $npo @i7bb @i7gh %i7x %i7xr %xtraFiles cutArt np npx openWinOrUnix isWindows shortIf sourceFile tableFile tx);
#@EXPORT_OK   = qw(i7x $np);

our %i7x = ( "12" => "shuffling",
  "sa" => "shuffling",
  "roi" => "roiling",
  "s13" => "roiling",
  "sts" => "stale-tales-slate", # not one game, but one repo
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
  "sc" => "slicker-city",
  "bs" => "btp-st",
  "s17" => "btp-st",
  "btp" => "buck-the-past",
  "e11" => "dash",
  "e13" => "ghost",
  "e14" => "Candy Rush Saga",
  "e15" => "heezy-park",
  "e16" => "checkered-haunting",
  "e17a" => "uxmulbrufyuz",
  "e17b" => "vivid-mimic",
  "ss" => "seeker-status",
  "17" => "cube-cavern",
  "cc" => "cube-cavern",
  "ai" => "ailihphilia",
  "ail" => "ailihphilia",
  "pu" => "ailihphilia",
  "up" => "ailihphilia",
  "tm" => "tragic-mix",
  "mo" => "molesworth",
  "mw" => "molesworth",
  "69" => "69105more",
  "qb" => "big-nose",
  "bn" => "big-nose"
);

our %i7xr = ( "shuffling" => "sa",
  "roiling" => "roi",
  "threediopolis" => "3d",
  "fourdiopolis" => "4d",
  "ugly-oafs" => "uo",
  "compound" => "pc",
  "slicker-city" =>"sc" ,
  "btp-st" =>"bs" ,
  "btp" => "buck-the-past",
  "ailihphilia" => "ai",
  "big-nose" => "qb",
);

our @i7gh = ("threediopolis", "short-games", "fourdiopolis", "stale-tales-slate", "the-problems-compound", "slicker-city", "misc", "ugly-oafs", "dirk", "trizbort", "writing", "ailihphilia", "tragic-mix");
our @i7bb = ("seeker-status", "buck-the-past",  "ailihphilia", "big-nose", "curate");

our @titleWords = ("but", "by", "a", "the", "in", "if", "is", "it", "as", "of", "on", "to", "or", "sic", "and", "at", "an", "oh", "for", "be", "not", "no", "nor", "into", "with", "from", "over");

our %xtraFiles;

$xtraFiles{"buck-the-past"} = ["c:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions\\Andrew Schultz\\Buck the Past tables.i7x"];
$xtraFiles{"slicker-city"} = ["c:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions\\Andrew Schultz\\Slicker City tables.i7x"];
$xtraFiles{"compound"} = ["c:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions\\Andrew Schultz\\Compound tables.i7x"];
$xtraFiles{"shuffling"} = ["c:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions\\Andrew Schultz\\Shuffling nudges.i7x", "c:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions\\Andrew Schultz\\Shuffling random text.i7x"];
$xtraFiles{"roiling"} = ["c:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions\\Andrew Schultz\\Roiling nudges.i7x", "c:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions\\Andrew Schultz\\Roiling random text.i7x"];
$xtraFiles{"ailihphilia"} = ["c:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions\\Andrew Schultz\\Ailihphilia Tables.i7x", "c:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions\\Andrew Schultz\\Ailihphilia Tests.i7x", "c:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions\\Andrew Schultz\\Ailihphilia Mistakes.i7x", ];

our $np = "\"C:\\Program Files (x86)\\Notepad++\\notepad++.exe\"";
our $npo = "start \"\" $np";

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

############################################
# creates the string to open a file on the clipboard then runs it

sub np
{
  my $param = scalar @_;
  for my $x (0..$param-1)
  {
    next if $_[$x] =~ /^[0-9]*$/;
	my $cmd = "$npo \"$_[$x]\"";
    $cmd .= " -n$_[$x+1]" if defined($_[$x+1]) && ($_[$x+1] =~ /^[0-9]+$/);
	print "Opening $_[$x]\n";
    system($cmd);
  }
}

sub npx
{
  np(@_);
  exit()
}

############################################
# checks a file's line endings, then opens it

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

sub isWindows
{
  my $file = $_[0];
  my $origFile = "";
  open($origFile, "<", $file);
  binmode($file);
  my $line = <$file>;

  return $line =~ /\r/;
}

############################################
# gives a project's short handle, if there

sub shortIf
{
  return defined($i7xr{$_[0]}) ? $i7xr{$_[0]} : $_[0];
}

# gives the story file for the project

sub sourceFile
{
  my $temp = $_[0];
  $temp = $i7x{$temp} if defined($i7x{$temp});
  return "c:\\games\\inform\\$temp.inform\\Source\\story.ni";
}

############################################
# opens the table file for a project (removes dashes)

sub tableFile
{
  my $temp = $_[0];
  $temp =~ s/-/ /g;
  return "c:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions\\Andrew Schultz\\$temp tables.i7x";
}

############################################
# gives a file with the extension txt

sub to_proj
{
  my $temp = $_[0];
  return $i7x{$_[0]} if defined($i7x{$_[0]});
  return $_[0];

}

sub tx
{
  my $temp = $_[0];
  $temp =~ s/\.[^\.]*$/.txt/i;
  return $temp;
}

1;
