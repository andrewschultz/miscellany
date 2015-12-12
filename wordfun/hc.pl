open(A, "c:/writing/dict/brit-1word.txt") || die ("No brit-1word.txt");

@nope = split(//, @ARGV[1]);

  @mine = split(//, @ARGV[0]);

#if ($r =~ /@ARGV[1]/i) { die; }
#else { die ("$r !~ @ARGV[1]"); }

while ($a = <A>)
{
  chomp($a);
  if (length($a) != length(@ARGV[0])) { next; }
  $a = lc($a);
  @theirs = split(//, $a);
  $nope = 0;
  for (0..$#mine)
  {
    if ((@theirs[$_] eq @mine[$_]) || (@mine[$_] eq ".")) { }
    else { $nope = 1; }
    if (@mine[$_] eq ".")
    {
      for $x (0..$#nope) { if ($a =~ @nope[$x]) { $nope = 1; } }
    }
  }
  if (!$nope) { checkForRepeats($a); }
}

my $count = 0; if (keys %occur > 1) { print "BEST CHOICE: "; } for $q (sort {$occur{$b} <=> $occur{$a} || $a cmp $b} keys %occur) { $count++; if ($count % 5 == 2) { print "\n"; } if ($count == 2) { print "OTHERS: "; } print "$q: $occur{$q} "; }

sub checkForRepeats
{
  my @a1 = split(//, @ARGV[0]);
  my @a2 = split(//, $_[0]);
  
 
  my $a3 = @ARGV[0]; $a3 =~ s/\.//g;
  
  for (0..$#a2)
  {
    if (@a1[$_] ne ".") { @a2[$_] = ""; }
  }
  
  $a4 = join("", @a2);
  
  my @b3 = split(//, $a3);

  #print "Now @a1 vs @a2 with @b3\n";
  
  for $j (@b3)
  {
    if ($a4 =~ /$j/)
    {
      #print "$_[0] contains extra guessed letters from @ARGV[0] namely $j.\n";
      return;
    }
  }

  $count++;
  print "$count $_[0] @ARGV[1]\n";
  for $x (@a2) { if (@ARGV[0] !~ /$x/) { $occur{$x}++; } }
}