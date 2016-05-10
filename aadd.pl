##############################
#aadd.pl adds a word alphabetically to dict files, big one and by-length
#
#usage aadd.pl word1,word2
#

use File::Copy qw(copy);

if (@ARGV[0] !~ /[a-z]/i) { print "need word or list of words to add."; }

@words = split(/,/, uc(@ARGV[0]));

my $b1 = "c:/writing/dict/brit-1word.txt";
my $ta = "c:/writing/dict/temp-alf.txt";

for $w (@words)
{
  $l = length($w);
  addAlf($w, $b1);
  addAlf($w, "c:/writing/dict/words-$l.txt");
}

sub addAlf
{
  my $sorted = 0;
  my $lc = lc($_[0]);
  my $uc = uc($_[0]);
  my $llc = length($lc);

  open(A, "$_[1]");
  open(B, ">$ta");
  while ($a = <A>)
  {
    $last = $a;
    if ($sorted) { print B $a; next; }
    if (($uc le $a) && ($llc == length($a) - 1))
    {
      $sorted = 1;
      $b = $a; chomp($b); if ($b eq $uc) { print "Already have $lc.\n"; $sorted = 1; next; }
      print "Added $uc before $b.\n";
      print B "$uc\n$a"; $sorted = 1; next;
    }
    print B $a;
  }
  if (!$sorted) { print B "$uc\n"; print "Adding $uc to last in $_[1].\n"; }
  close(B);
  close(A);
  copy($ta, $_[1]);
}

