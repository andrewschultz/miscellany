#######################
#trizx.pl
#
#extracts trizbort object and room properties from GIT commits
#

use XML::LibXML;

use strict;
use warnings;

my %objArray;
my %roomHash;
my %initialRooms;
my %initialItems;
my $proj = "buck-the-past";
my $gh = "c:\\users\\andrew\\documents\\github";
my $projYet = 0;
my $verbose = 0;
my $count = 0;
my $readInitialRooms = 1;
my $readInitialItems = 1;

while ($count <= $#ARGV)
{
  my $arg = $ARGV[$count];
  for ($arg)
  {
  /^-?v$/i && do { $verbose = 1; $count++; next; };
  if ($projYet) { die ("Can't have 2 projects"); }
  $projYet = 1;
  $proj = $arg;
  $count++;
  }
}

my $trizname = "$proj.trizbort";

my $storyChange = 0;
if ($storyChange)
{
  my @storyChange = getChangeIDs($proj, "story.ni");
}
else
{
if ($proj eq "roiling") { $proj = "stale-tales-slate"; $trizname = "Roiling\\maps\\roiling"; }
elsif ($proj eq "shuffling") { $proj = "stale-tales-slate"; $trizname = "Shuffling\\maps\\shuffling"; }
elsif ($proj eq "compound") { $proj = "the-problems-compound"; $trizname = "compound"; }

unless (-d "$gh\\$proj") { die ("No directory $gh\\$proj."); }
unless (-f "$gh\\$proj\\$trizname.trizbort") { die ("No file $gh\\$proj\\$trizname.trizbort."); }

my @changeIDs = getChangeIDs($proj, "$trizname.trizbort");
}

#parseOneXml('c:\games\inform\triz\mine\buck-the-past.trizbort');

my $eq = '=' x 30;

print "$eq", "OBJECTS", "$eq\n";

for (sort {$objArray{$b} <=> $objArray{$a}} keys %objArray)
{
  print "$_ $objArray{$_}" . ($initialItems{$_} ? " * " : "") . "\n";
}

print "$eq", "ROOMS", "$eq\n";

for (sort {$roomHash{$a} <=> $roomHash{$b}} keys %roomHash)
{
  print "$_ $roomHash{$_}" . ($initialRooms{$_} ? " * " : "") . "\n";
}

################################
#subroutines
#

sub parseOneXml
{
my $parser = XML::LibXML->new();
my $xmldoc = $parser->parse_file($_[0]);

my @temp;

for my $obj($xmldoc->findnodes('/trizbort/map/room'))
{
  $roomHash{$obj->getAttribute("name")}++;
  if ($readInitialRooms) { $initialRooms{$obj->getAttribute("name")} = 1; }
  for my $name ($obj->findnodes('./*'))
  {
    if ($name->nodeName() eq "objects") { @temp = split(/\|/, $name->textContent()); for (@temp) { $objArray{$_}++;  } $initialItems{$_} = 1; }
  }
}

$readInitialRooms = 0;
$readInitialItems = 0;

}

sub getChangeIDs
{
  if (!defined($_[0]) || !$_[0]) { return; }
  chdir("$gh\\$_[0]");
  my $commits = `git rev-list --all --objects -- $_[1]`;
  my @list = split(/\n/, $commits);
  my $tempTriz = "c:\\games\\inform\\temp.trizbort";
  #die(join("\n", @list));
  @list = grep { $_ !~ / [a-z]/ } @list;
  my $count = 0;
  my $xmltext;

  my $numdif = `git rev-list --count HEAD`;

  if ($_[1] =~ /story.ni/)
  {
    unlink<"c:\\games\\inform\\$_[0]-swears.txt">;
    for (0..$numdif - 2)
	{
	my $q = $_+1;
	my $cmd = "git diff HEAD~$_ HEAD~$q story.ni | grep -in \"if swears\"";
	print "Checking HEAD~$_ vs HEAD~$q\n";
	#print "$cmd\n";
    my $sweardif = `$cmd`;
	if ($sweardif)
	{
	open(B, ">>c:\\games\\inform\\$_[0]-swears.txt");
	print B "$_\n$sweardif\n\n";
	close(B);
	}
	}
	`c:\\games\\inform\\$_[0]-swears.txt`;
	exit();
  }

  for (@list)
  {
    $_ =~ s/ *$//;
    $count++;
    if ($verbose) { printf("Opening commit $_ $count of %d\n", scalar @list); }

	my $cmd = "git show $_:$_[1]";
    $xmltext = `$cmd`;
	open(B, ">$tempTriz");
	print B $xmltext;
	close(B);
	if ($xmltext =~ /^tree/i) { print "$_ has bad XML to start\n"; next; }
	parseOneXml("$tempTriz");
  }
  exit if $_[1] =~ /story.ni/;
}