################################
#FRN.PL: Full Room Name
#
#command line variables ATM: word1,word2
#

use strict;
use warnings;

my $schema = "frn-schema.txt";

###################hashes
my %misses;
my %idx;
my %need;
my %adds;
my %litany;
my %exceptions;

###################variables
my @words;
my $longComment = 0;
my $count = 0;
my $origLine;
my $b4;
my $line;
my $detail = 0;

if (defined($ARGV[0]))
{
  print "Reading command line for prevword,nextword\n";
  for ($ARGV[0])
  {
    @words=split(/,/, $_);
	$need{$words[1]} = $words[0];
  }
}
else
{
open(A, $schema) || die ("No $schema.");

while ($line=<A>)
{
  if ($line =~ /^!/) #in other words, ignore this except for detailed searches
  {
    if ($detail == 0) { next; }
	$line =~ s/^!//;
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
  if ($#words == 1) { $need{$words[1]} = $words[0]; }
}

close(A);
}

open(A, "story.ni");

my $key;

while ($line = <A>)
{
  if ($line =~ /^to say/) { next; }
  for $key (keys %need)
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
        if ((lc($words[$count]) eq $key) && ($need{$key} ne lc($words[$count-1])) && (!defined($exceptions{"$words[$count-1] $words[$count]"})))
        {
          chomp($origLine);
		  $origLine =~ s/^[\t ]*//;
		  $b4 = lc($words[$count-1]);
          print "L$.-$count: $origLine/$b4 $key => $need{$key} $key.\n";
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

############################subroutines

sub short
{
  my $temp = $_[0];
  $temp =~ s/-.*//;
  return $temp;
}