################################
#FRN.PL: Full Room Name
#

use strict;
use warnings;

###################hashes
my %misses;
my %idx;
my %need;
my %adds;
my %litany;

###################variables
my @words;
my $longComment = 0;
my $count = 0;
my $origLine;
my $b4;
my $line;

open(A, "frm-schema.txt");

while ($line=<A>)
{
  if ($line =~ /^;/) { last; }
  if ($line =~ /^#cut/) { $longComment = !$longComment; next; }
  if ($line =~ /^#/) { next; }
  if ($longComment) { next; }
  chomp($line);
  $line = lc($line);
  @words = split(/ /, $line);
  if ($#words == 1) { $need{$words[1]} = $words[0]; }
}

close(A);

open(A, "story.ni");

my $key;

while ($line = <A>)
{
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
      @words = split(/\W+/, $line);
      for $count (0..$#words)
      {
        #print "$count $words[$count]\n";
        if ((lc($words[$count]) eq $key) && ($need{$key} ne lc($words[$count-1])))
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