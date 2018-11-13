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
@EXPORT      = qw(@titleWords $np $npo @i7bb @i7gh %i7x %i7xr %projFiles cutArt np npx openWinOrUnix isWindows shortIf sourceFile tableFile tx);
#@EXPORT_OK   = qw(i7x $np);

our %i7x = ();
our %i7xr = ();
our @i7gh = ();
our @i7bb = ();
our %i7com = ();
our %i7ghp = ();
our %i7nonhdr = (); # shortcuts for nonheader files like story.ni, walkthrough.txt, notes.txt
our %i7pf = ();
our %i7rn = (); # release names

our $i7hdir = "c:\\Program Files (x86)\\Inform 7\\Inform7\\Extensions\\Andrew Schultz\\";

open(A, "c:/writing/scripts/i7p.txt") || die ("Can't open i7p.txt");

our $i7p_line;
our $curDef;

our %projFiles;

while ($i7p_line = <A>)
{
  next if $i7p_line =~ /^#/;
  last if $i7p_line =~ /^;/;
  chomp($i7p_line);
  (my $temp = $i7p_line) =~ s/^.*?://;

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
  elsif ($i7p_line =~ /^RELEASE:/)
  {
    my @tempAry = split(/=/, $temp);
	$i7rn{$tempAry[0]} = $tempAry[1];
    next;
  }
  elsif ($i7p_line =~ /^COMBO:/i)
  {
    my @tempAry = split(/=/, $temp);
    $i7com{$tempAry[0]} = $tempAry[1];
    next;
  }
  elsif ($i7p_line =~ /^GHPROJ:/i)
  {
    my @tempAry = split(/=/, $temp);
    $i7ghp{$tempAry[0]} = $tempAry[1];
    next;
  }
  elsif ($i7p_line =~ /^NONHDR:/i)
  {
    my @tempAry = split(/=/, $temp);
    $i7nonhdr{$tempAry[0]} = $tempAry[1];
    next;
  }
  elsif ($i7p_line =~ /^CURDEF:/i)
  {
    $curDef = $temp;
    next;
  }
  elsif ($i7p_line =~ /^HEADERS:/i)
  {
    (my $temp = $i7p_line) =~ s/.*://;
    my @tempAry = split(/=/, $temp);
	my @hdrAry = split(/,/, $tempAry[1]);
	$projFiles{$tempAry[0]} = ( "c:/games/inform/$tempAry[0].inform/source/story.ni" );
	my $hname = toExt($tempAry[0]);
	for my $j (@hdrAry) {
	  my $temp = "$i7hdir$hname $j.i7x";
	};

	next;
  }
  elsif ($i7p_line =~ /:/)
  {
    next if ($i7p_line =~ /^HEADNAME/); # HEADNAME not processed by Perl. It is for my python functions.
    warn("WARNING: For I7 PERL, line $. has an unrecognized colon: $i7p_line\n");
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

sub src {
  return sprintf("c:/games/inform/%s.inform/source/story.ni", to_proj($_[0]))
}

sub tx
{
  my $temp = $_[0];
  $temp =~ s/\.[^\.]*$/.txt/i;
  return $temp;
}

sub toExt
{
  my $x = ucfirst($_[0]);
  $x =~ s/-/ /g;
  return $x;
}

1;
