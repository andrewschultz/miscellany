#######################
#trizx.pl
#
#extracts trizbort object and room properties
#

use XML::LibXML;

use strict;
use warnings;

my %objArray;
my %roomHash;
my $proj = "buck-the-past";
my $gh = "c:\\users\\andrew\\documents\\github";
my $projYet = 0;
my $verbose = 0;
my $count = 0;

while ($count <= $#ARGV)
{
  my $arg = $ARGV[$count];
  for ($arg)
  {
  /^-?v$/i && do { $verbose = 1; $count++; next; };
  if ($projYet) { die ("Can't have 2 projects"); }
  $projYet = 1;
  $proj = $arg;
  unless (-d "$gh\\$proj") { die ("No directory $gh\\$proj."); }
  $count++;
  }
}

my @changeIDs = getChangeIDs($proj, "$proj.trizbort");

#parseOneXml('c:\games\inform\triz\mine\buck-the-past.trizbort');

getChangeIDs();

my $eq = '=' x 30;

print "$eq", "OBJECTS", "$eq\n";

for (sort {$objArray{$b} <=> $objArray{$a}} keys %objArray)
{
  print "$_ $objArray{$_}\n";
}

print "$eq", "ROOMS", "$eq\n";

for (sort {$roomHash{$a} <=> $roomHash{$b}} keys %roomHash)
{
  print "$_ $roomHash{$_}\n";
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
  for my $name ($obj->findnodes('./*'))
  {
    if ($name->nodeName() eq "objects") { @temp = split(/\|/, $name->textContent()); for (@temp) { $objArray{$_}++; } }
  }
}

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

  for (@list)
  {
    $_ =~ s/ *$//;
    $count++;
    if ($verbose) { printf("Opening commit $_ $count of %d\n", scalar @list); }
    $xmltext = `git show $_:$_[0].trizbort`;
	open(B, ">$tempTriz");
	print B $xmltext;
	close(B);
	if ($xmltext =~ /^tree/i) { print "$_ has bad XML to start\n"; next; }
	parseOneXml("$tempTriz");
  }

}