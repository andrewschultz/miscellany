########################################
# lnct.pl = LiNe CounT.pl
# simply counts the remaining lines to process in games.otl
#

use strict;
use warnings;

my $inFile = "c:/writing/games.otl";

my $minOkay = 3;

my $sec = 0;
my $totalLines = 0;
my $lines = 0;

###########variables
my %gotYet;
my $count = 0;
my $counting = 0;
my $everFound = 0;

my @starts = ();

while ($count <= $#ARGV)
{
  $a = $ARGV[$count];
  for ($a)
  {
    /^-?[0-9]+$/ && do { $minOkay = $a; if ($minOkay < 0) { $minOkay = - $minOkay; } $count++; next; };
	/^-?\?$/ && do { usage(); exit; };
	/^-f\?$/ && do { $inFile = $ARGV[$count+1]; $count += 2; next; };
	/^-/ && do { print "Bad flag.\n\n"; usage(); exit; };
	/[a-z]/ && do { @starts = split(/,/, $a); for (@starts) { $gotYet{$_} = 0; } $count++; next; };
	die; #should never happen but yeah
  }
}

open(A, $inFile) || die ("No $inFile.");

OUTER:
while ($a = <A>)
{
  if ($a !~ /^#/) { $lines++; }
  if ($a !~ /[a-z]/i)
  {
    #if ($counting) { print "Last line $a"; }
	if ($counting)
	{
    print "TEST RESULTS:games.otl lines for $sec,$minOkay,$totalLines,0,<a href=\"file:///c:/writing/games-otl.htm#$sec\">OTL file</a>\n";
	}
	$totalLines = 0;
    $counting = 0; next;
  }
  if ($a =~ /^\\/)
  {
    for my $st (@starts)
	{
	  if ($a =~ /^\\$st[=\|]/) { $gotYet{$st}++; print "Start with $a"; $sec = $a; chomp($sec); $sec =~ s/[\|=].*//g; $sec =~ s/^\\//g; $everFound = 1; $counting = 1; next OUTER; }
	}
  }
  if (($counting) && ($a !~ /^#/)) { $totalLines++; }
}

if (!$everFound) { die "Oops! Never tripped anything in @starts.\n"; }
else { for (@starts) { if ($gotYet{$_} == 0) { print "Didn't find $_.\n"; } } }

close(A);

sub usage
{
print<<EOT;
numerical parameter means how many errors/lines are acceptable
CSV means which sections to look for
-f means to look for a different file than games.otl
EOT
}