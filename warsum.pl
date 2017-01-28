##############################
#
#warsum.pl
#
#warnings summary so it doesn't go on for one whole screen
#
#usage is generally with another file e.g.
#
#tofix.pl 2>&1 | warsum.pl
#
#to add: what's in what function(s)
#
#ws.bat
#@echo off
#set FILE=%1
#echo Note you need to specify the file with extension as DOS is a bit wobbly
#set WARSUM=1
#%FILE% 2>&1 | warsum.pl -annoyingstring
#set WARSUM=

use warnings;
use strict;
use File::Which qw (which where);

my %count;
my %low;
my %high;
my %lastsub;
my %scalars;

my %descr;
$descr{"\$"} = "STRING VARIABLES";
$descr{"\@"} = "ARRAYS";
$descr{"\%"} = "HASHES";

my $c;

my $fileToSearch = "";

if (!defined($ARGV[0])) { usage(); }

if ($ENV{"PATHEXT"} !~ /\.pl;/i) { $ENV{"PATHEXT"} = ".PL;" . $ENV{"PATHEXT"}; }
my @bins = where($ARGV[0]);

if ($#bins == -1) { die "No file $ARGV[0]."; } else { print "Reading $bins[0].\n"; }

if ($#bins > 0) { print "(Note there's >1: @bins)\n"; }

$fileToSearch = $bins[0];

open(A, "$fileToSearch");

$lastsub{"MAIN"} = 0;

my $line;
while ($line = <A>)
{
  if ($line =~ /^sub/) { $line =~ s/^sub //; $line =~ s/ +#.*//; chomp($line); $lastsub{$line} = $.; }
}
close(A);

my $mystr = `$ARGV[0]  -? 2>&1`;

my @warnlines = split(/[\r\n]+/, $mystr);

my $thisline;

for $thisline (@warnlines)
{
  if ($thisline =~ /^Execution of/i) { next; }
  chomp($thisline);
  $b = $thisline;
  $b =~ s/.* line //;
  $c = $b; $c =~ s/\.//;
  if ($thisline =~ /^scalar value/i)
  {
    $thisline =~ s/^scalar value //i;
	$thisline =~ s/\[.*//;
	$scalars{$thisline}++;
  }
  if ($thisline !~ /^Global symbol/i) { next; }
  $thisline =~ s/^Global symbol \"//; $thisline =~ s/\".*//;
  if (!$low{$thisline})
  {
    $low{$thisline} = $c;
	$high{$thisline} = $c;
  }
  else
  {
    if ($c < $low{$thisline}) { $low{$thisline} = $c; }
    if ($c > $high{$thisline}) { $high{$thisline} = $c; }
  }
  $count{$thisline}++;
  #print "$thisline\n";
}

my $firstkey = "";
for my $key (sort keys %low)
{
  my $key1 = substr($key,0,1);
  if ($key1 ne $firstkey) { print "=" x 40 . $descr{$key1} . "\n"; $firstkey = $key1; }
  print "$key covers $low{$key} to $high{$key}, $count{$key} incidences.";
  if (cursub($low{$key}) ne cursub($high{$key})) { printf (" Separate functions: %s vs %s.", cursub($low{$key}), cursub($high{$key})); }
  else { printf(" Completely contained in %s.", cursub($low{$key})); }
  print "\n";
}

for my $key (sort keys %scalars)
{
  print "$key has warnings thrown: $scalars{$key}. ";
}

print "" . (scalar keys %low) . " total keys read.\n";

#####################################

sub cursub
{
  my $k;
  for $k (sort {$lastsub{$b} <=> $lastsub{$a}} keys %lastsub)
  {
    if ($_[0] > $lastsub{$k}) { return $k; }
  }
}

sub usage
{
print<<EOT;
You need to type in the name of a program to check for strict/warnings violations.
EOT
exit()
}