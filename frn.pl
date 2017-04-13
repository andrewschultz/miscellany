################################
#FRN.PL: Full Room Name
#
#command line variables ATM: word1,word2
#

use strict;
use warnings;
####################constants
my @mainWordList = ("for", "when", "if", "is", "or", "in", "of", "to", "or");
my $schema = "frn-schema.txt";

###################hashes
my %misses;
my %idx;
my %needb4;
my %needaf;
my %adds;
my %litany;
my %exceptions;
my %mainWord;

###################options
my $onlyMain = 1;

###################variables
my @words;
my $longComment = 0;
my $count = 0;
my $origLine;
my $b4;
my $line;
my $detail = 0;
my $reverse = 0;
my $lookFwd = 0;
my $lookBack = 0;

if (defined($ARGV[0]))
{
  print "Reading command line for prevword,nextword\n";
  for ($ARGV[0])
  {
    @words=split(/,/, $_);
	$needb4{$words[1]} = $words[0];
  }
}
else
{
open(A, $schema) || die ("No $schema.");

while ($line=<A>)
{
  $lookBack = $lookFwd = 1;
  if ($line =~ /^!/) #in other words, ignore this except for detailed searches
  {
    if ($detail == 0) { next; }
	$line =~ s/^!//;
  }
  if ($line =~ /^>/)
  {
    $lookBack = 0;
	$line =~ s/^>//;
  }
  if ($line =~ /^</)
  {
    $lookFwd = 0;
	$line =~ s/^<//;
  }
  if ($line =~ /^;/) { last; }
  if ($line =~ /^#cut/) { $longComment = !$longComment; next; }
  if ($line =~ /^#/) { next; }
  if ($longComment) { next; }
  chomp($line);
  if ($line =~ /^-/)
  {
    $line =~ s/^-//;
	$exceptions{$line} = 1;
	next;
  }
  $line = lc($line);
  @words = split(/ /, $line);
  if ($#words == 1)
  {
    if ($lookBack) { $needb4{$words[1]} = $words[0]; }
    if ($lookFwd) { $needaf{$words[0]} = $words[1]; }
  }
}

close(A);
}

initMainWords();

open(A, "story.ni");

my $key;

while ($line = <A>)
{
  if ($line =~ /^to say/) { next; }
  for $key (keys %needb4)
  {
    if ($line =~ /\b$key\b/i)
    {
	  if ($line =~ /\t$key/i)
	  {
	    print "L$. has tab then $key.\n";
		next;
	  }
	  if ($line =~ /^$key/i)
	  {
	    print "L$. starts with $key.\n";
		next;
	  }
      $origLine = $line;
      $line = lc($line);
      $line =~ s/^[\t ]*//; chomp($line);
      @words = split(/[ ;=:,\.\t\"\]\[\?!\(\)]+/, $line);
      for $count (0..$#words)
      {
        #print "$count $words[$count]\n";
        if ((lc($words[$count]) eq $key) && ($needb4{$key} ne lc($words[$count-1])) && (!defined($exceptions{"$words[$count-1] $words[$count]"})))
        {
		  if (($onlyMain) && (!defined($mainWord{$words[$count-1]})))
		  {
		    next;
		  }
          chomp($origLine);
		  $origLine =~ s/^[\t ]*//;
		  $b4 = lc($words[$count-1]);
          print "L$.-$count: $origLine/$b4 $key => $needb4{$key} $key.\n";
          $misses{$key}++;
		  if (!defined($adds{"$key-$b4"}))
		  {
			$litany{$key} .= "-$b4";
		  }
          $adds{"$key-$b4"}++;
        }
      }
    }
  }
}

close(A);

my $idx;

for $idx (sort { $misses{$b} <=> $misses{$a} } keys %misses)
{
  print "$idx: $misses{$idx}, $litany{$idx}\n";
}

for $idx (sort { short($b) cmp short($a) || $adds{$b} <=> $adds{$a} } keys %adds)
{
  print "$idx : $adds{$idx}\n";
}

print "PASSED:";

for $idx (sort  keys %needb4)
{
  unless (defined($litany{$idx}))
  {
    print " $idx";
  }
}
print "\n";

############################subroutines

sub initMainWords
{
  for (@mainWordList)
  {
    $mainWord{$_} = 1;
  }
}

sub short
{
  my $temp = $_[0];
  $temp =~ s/-.*//;
  return $temp;
}