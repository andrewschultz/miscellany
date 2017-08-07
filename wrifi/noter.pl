############################
#noter.pl
#
#looks in the notebook files for a specific phrase or regex
#
# use = noter.pl [word or phrase]
#

use strict;
use warnings;

my $capsString;
my $dailyDir;
my $maxFinds;
my $otlDir;
my @toRead;
my $namesRead;
my $readBigs;
my $readDaily;
my $sectToMatch;

initialize();
readParams();

if ($readBigs) { for my $curFile (@toRead) { readOne("$otlDir/$curFile", 1); } }
if ($readDaily) { readDailyFiles(); }

exit;

###################################################
#subroutines

sub readParams
{
while ($ARGV[0] =~ /^-/)
{
  for ($ARGV[0])
  {
    /-C/ && do { $capsString = "";shift(@ARGV); next; };
    /-c/ && do { $dailyDir = "c:/writing/daily"; shift(@ARGV); next; };
    /-bo/ && do { $readDaily = 0; $readBigs = 1; shift(@ARGV); next; };
    /-do/ && do { $readDaily = 1; $readBigs = 0; shift(@ARGV); next; };
    /-d/ && do { $readDaily = 1; shift(@ARGV); next; };
    /-b/ && do { $readBigs = 1; shift(@ARGV); next; };
    /-m/ && do { $maxFinds = $ARGV[1]; shift(@ARGV); shift(@ARGV); next; };
    /-n/ && do { $namesRead = 1; shift(@ARGV); next; };
    /-s/ && do { $sectToMatch = $ARGV[1]; $sectToMatch =~ s/^-s=//g; shift(@ARGV); next; };
    usage();
  }
}

}

sub initialize
{
$maxFinds = 1000;
$dailyDir = "c:/writing/daily";
$capsString = "i";
$otlDir = "c:/writing";
@toRead = ("notes9.otl", "hthws.otl", "names.otl");
$readBigs = 1;
$namesRead = 0;
}

sub readDailyFiles
{
opendir(DIR, "$dailyDir");

my @files = readdir(DIR);

foreach (@files) { if ("$_" !~ /^2[0-9]*\.txt$/) { next; }

if (! -f "$dailyDir/$_") { next; }

#print "$_\n";

readOne("$dailyDir/$_", 0);
}

close(DIR);

}

sub readOne
{
my $namePrint = 0;
$namesRead = 0;

my $nameString = "";
my $outputString = "";
my $headerString = "========================$_[0]\n";

open(A, "$_[0]") || die ("$_[0]");
#open(A, "notes.otl") || die ("Can't open writing/notes.otl");

if (!defined($ARGV[0])) { die ("You need a string to match."); }

my $matchstr = $ARGV[0];
my @bgrep;

my $count = 0;
my $thisSect = "";

while ($a = <A>)
{
  chomp($a);
  if ($a =~ /^\\/) { $thisSect = $a; $thisSect =~ s/^\\//g; }

  if ($a =~ /\t/) {
    my @b = split(/\t/, $a);
    if ($capsString eq "i") { @bgrep = grep(/$matchstr/i, @b); } else
    { @bgrep = grep(/$matchstr/, @b); }
    foreach my $c (@bgrep) { if (!$namesRead) { $nameString .= "Names: $c"; } else { $nameString .= "\t$c"; } $namesRead++; $count++;}
    #print "\n"; print "Last is $b[$#b]\n";
    if ($namePrint == 1) { $outputString .= "\n"; } next; }
  if (($a =~ /$matchstr/) || (($capsString eq "i") && ($a =~ /$matchstr/i)))
  { $count++; if (($thisSect eq $sectToMatch) || (!$sectToMatch))
    { $outputString .= "$count $a\n"; } };
  if ($count >= $maxFinds) { $count .= "+"; last; };
}

if ($nameString) { $outputString .= "$nameString\n"; }
#print "!@!@ $outputString@!@!\n"; return;
if ($outputString) {
  print $headerString; print $outputString;
  print "$count total occurrences of $matchstr, $namesRead names.\n";
}

if ($namesRead) { print "\n"; }

close(A);

}

