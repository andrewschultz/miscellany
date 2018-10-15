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

our %i7x = ();
our %i7xr = ();
our @i7gh = ();
our @i7bb = ();

open(A, "c:/writing/scripts/i7p.txt") || die ("Can't open i7p.txt");

our $i7p_line;

while ($i7p_line = <A>)
{
  next if $i7p_line =~ /^#/;
  last if $i7p_line =~ /^;/;
  chomp($i7p_line);
  my $temp = $i7p_line;
  $temp =~ s/.*://;

  if ($i7p_line =~ /^GITHUB:/)
  {
    @i7gh = split(/,/, $temp);
    next;
  }
  elsif ($i7p_line =~ /^BITBUCKET:/)
  {
    @i7bb = split(/,/, $temp);
    next;
  }

  my @i7xary = split(/=/, $i7p_line);
  my @poss_proj;
  if ($i7xary[1] !~ /,/)
  {
    $i7x{$i7xary[1]} = $i7xary[0];
    $i7xr{$i7xary[0]} = $i7xary[1];
  }
  else
  {
    @poss_proj = split(/,/, $i7xary[1]);
	for my $p (@poss_proj) {
	  $i7x{$p} = $i7xary[0];
	}
  }
}

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
