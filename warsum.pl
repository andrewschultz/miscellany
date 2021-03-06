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

my $line;
my $c;

#variables
my $strict = 0;
my $warnings = 0;
my $argCount = 0;

#options
my $fileToSearch = "";
my $sortByLine = 1;
my $adjustWarnings = 0;

print "SortByLine " . ($sortByLine ? "on" : "off") . " by default.\n";

if (!defined($ARGV[$argCount])) { usage(); }

###############NEED TO FIX THIS

my $count = 0;

while ($count <= $#ARGV)
{
  my $thisarg = $ARGV[$count];
  for ($thisarg)
  {
    /^-?l$/ && do { $sortByLine = 1; $count++; next; };
    /^-?nl$/ && do { $sortByLine = 0; $count++; next; };
    /^-?aw$/ && do { $adjustWarnings = 1; $count++; next; };
	/\.pl$/i && do
	{
	  if ($fileToSearch)
	  {
	    print "WARNING: $fileToSearch overwritten as file to search.\n";
	  }
      $fileToSearch = $thisarg; $count++; next; };
	usage();
  }
}

if (! -f $fileToSearch)
{
if ($ENV{"PATHEXT"} !~ /\.pl;/i) { $ENV{"PATHEXT"} = ".PL;" . $ENV{"PATHEXT"}; }
my @bins = where($fileToSearch);

if ($#bins == -1) { die "No file $fileToSearch."; } else { print "Reading $bins[0].\n"; }

if ($#bins > 0) { print "(Note there's >1: @bins)\n"; }

$fileToSearch = $bins[0];
}

if (!$fileToSearch) { die ("Need a file to search,"); }

if ($adjustWarnings) { adjustWarnings($fileToSearch); exit(); }

open(A, "$fileToSearch") || die ("Can't find $fileToSearch");

$lastsub{"MAIN"} = 0;

while ($line = <A>)
{
  if ($line =~ /^use strict;/) { $strict = 1; }
  if ($line =~ /^use warnings;/) { $warnings = 1; }
  if ($line =~ /^sub/) { $line =~ s/^sub //; $line =~ s/ +#.*//; chomp($line); $lastsub{$line} = $.; }
}
close(A);

if ($strict + $warnings < 2)
{
  if (!$strict) { print "Need USE STRICT.\n"; }
  if (!$warnings) { print "Need USE WARNINGS.\n"; }
  die();
}

my $cmd = "$fileToSearch -? 2>&1";
print "Running usage for $fileToSearch...\n";

my $mystr = `$cmd`;

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

my $errCount = 0;
my $firstkey = "";
for my $key (sort {
  ($sortByLine && ((substr($a, 0, 1) cmp substr($b, 0, 1)) || ($low{$a} <=> $low{$b}) || ($high{$a} <=> $high{$b}))) # first we test if the $/%/@ match up, then for actual line numbers
  || ($a cmp $b) } # then finally for names
  keys %low)
{
  $errCount += $count{$key};
  my $key1 = substr($key,0,1);
  if ($key1 ne $firstkey) { print "=" x 40 . $descr{$key1} . "\n"; $firstkey = $key1; }
  print "$key covers $low{$key} to $high{$key}, $count{$key} times.";
  if (cursub($low{$key}) ne cursub($high{$key})) { printf (" Seen from: %s vs %s.", cursub($low{$key}), cursub($high{$key})); }
  else { printf(" %s ONLY.", cursub($low{$key})); }
  print "\n";
}

for my $key (sort keys %scalars)
{
  print "$key has warnings thrown: $scalars{$key}.\n";
}

if (scalar keys %scalars) { print "Rerun with -aw to change \@ to \$.\n"; }

print "" . (scalar keys %low) . " total keys read, $errCount error count.\n";

if ((scalar keys %low == 0) && (scalar keys %scalars == 0)) { print "The file $fileToSearch seems to pass strict/warnings. Nice job!\n"; }

#####################################
#
#subroutines
#

sub adjustWarnings
{
  my $gotOne = 0;
  my $commentChange = 0;
  my $warout = "c:\\writing\\scripts\\warsum.txt";
  open(A, "$_[0]") || die ("No such file $_[0]");
  #if (-f $warout) { die ("Erase $warout before continuing."); }
  open(B, ">$warout") || die ("Can't open $warout");

  while ($line = <A>)
  {
    if ($line =~ /\@([^\[ ])+\[.*?]/)
	{
	  $gotOne++;
	  #print "Line $.\n";
	  #print $line;
	  $line =~ s/\@([^\]]+)(\[.*?\])/\$$1$2/g;
	  #print $line;
	  if ($line =~ /^[ \t]*#/) { $commentChange++; }
	}
	print B $line;
  }
  if ($gotOne)
  {
  print "$gotOne potential warning(s) replaced.\n";
  if ($commentChange) { print "NOTE: changed $commentChange inside comments.\n"; }
  `xcopy /y /q $warout $_[0]`;
  }
  else { print "Didn't find any \@ to convert to \$.\n"; }
}

######################find the current subroutine for a line
sub cursub
{
  my $k;
  for $k (sort {$lastsub{$b} <=> $lastsub{$a}} keys %lastsub)
  {
    if ($_[0] > $lastsub{$k}) { return $k; }
  }
}

######################usage
sub usage
{
print<<EOT;
You need to type in the name of a program to check for strict/warnings violations.
-l sort by line
-nl don't sort by line
-aw adjust warnings eg \@variable[] to \$variable[]
EOT
exit()
}