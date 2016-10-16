#####################################
#b1.pl
#
#this takes a sequence of hangman letters with correctly guessed places
#along with incorrect guesses and then looks through a dictionary
#
#then prints out results, with the most likely letters left
#

use strict;
use warnings;
use List::MoreUtils qw(uniq);

my $misses = "c:/writing/dict/b1.txt";
my %miss;
my $wrongString;
my $endString = "";
my $missFound = 0;
my %freq;
my %f2;

if (!defined($ARGV[0])) { die ("Usage: found letters (.=blank), wrong letters. Use +(word) to add it to $misses.\n"); }

if ($ARGV[0] =~ /^\+/)
{
  my $toAdd = lc($ARGV[0]); $toAdd =~ s/^\+//g;
  open(A, "$misses");
  while (my $line = <A>) { chomp($line); if ($line eq $toAdd) { print "Already there.\n"; exit; } }
  close(A);
  open(B, ">>$misses"); print B "$toAdd\n"; close(B); print "Added $toAdd.\n"; exit;
}

my @right = split(//, lc($ARGV[0]));
if (!defined($ARGV[1])) { $wrongString = ""; }
else
{
  $wrongString = lc($ARGV[1]);
  if ($ARGV[0] =~ /[$wrongString]/) { die "Oops, found and wrong overlap.\n"; }
}

my @wrong = split(//, $wrongString);
my @toGuess;

my $count = 0;

my $lastOne = "";
my $firstOne = "";
my $whichf = length ($ARGV[0]);

my $wordBad = 0;

my $readFile = "c:/writing/dict/words-$whichf.txt";

my $line;
 
open(A, "$misses") || die ("No misses file.");
while ($line = <A>) { chomp($line); if (defined($miss{lc($line)})) { print "$line duplicated.\n"; } $miss{lc($line)} = 1; }
close(A);

open(A, "$readFile") || die ("No $readFile");

my $canAlphabetize = 0;

#if ($r =~ /$ARGV[1]/i) { die; }
#else { die ("$r !~ $ARGV[1]"); }

if ($ARGV[0] =~ /^[a-z]/i) { $canAlphabetize = 1; $lastOne = $ARGV[0]; $lastOne =~ s/\..*//g; $lastOne .= "zzz"; $firstOne = uc(substr(lc($ARGV[0]), 0, 1)); }

while ($line = <A>)
{
  chomp($line);
  #if (length($line) != length($ARGV[0])) { next; }
  if ($canAlphabetize)
  {
    if ($line le $firstOne) { next; }
    if ($lastOne le $line) { last; }
  }
  $line = lc($line);
  @toGuess = split(//, $line);
  $wordBad = 0;
  for (0..$#toGuess)
  {
    if (($toGuess[$_] eq $right[$_])) { }
    elsif  ($right[$_] ne ".") { $wordBad = 1; last; }
    if ($right[$_] eq ".")
    {
      for my $x (0..$#wrong) { if ($line =~ $wrong[$x]) { $wordBad = 1; last; } }
    }
  }
  if (!$wordBad) { checkForRepeats($line); }
}

if ($endString) { print "MISSED BEFORE:\n$endString"; }

if ($count + $missFound > 1)
{
print "FREQUENCIES:";
#for (@right) { if (defined($freq{$_})) { delete($freq{$_}); } }
foreach my $val ( sort { $freq{$b} <=> $freq{$a}  or $f2{$b} <=> $f2{$a} } keys %freq)
{
  if ($f2{$val} == ($count + $missFound)) { print " **$val**"; next; }
  print " $val:$f2{$val}/$freq{$val}";
}
print "\n";
} elsif ($count + $missFound == 0) { print "Uh oh no matches.\n"; } else { print "Only one match found.\n"; }

sub checkForRepeats
{
  my @a1 = split(//, lc($ARGV[0]));
  my @a2 = split(//, $_[0]);
 
  my $a3 = lc($ARGV[0]); $a3 =~ s/\.//g;
  
  for (0..$#a2)
  {
    if ($a1[$_] ne ".") { $a2[$_] = ""; }
  }
  
  my $a4 = join("", @a2);
  
  my @b3 = split(//, $a3);

  #print "Now @a1 vs @a2 with @b3\n";
  
  for my $j (@b3)
  {
    if ($a4 =~ /$j/)
    {
      #print "$_[0] contains extra guessed letters from $ARGV[0] namely $j.\n";
      return;
    }
  }
  for (@a2) { if ($_) { $freq{$_}++; } }
  my @a2a = uniq(@a2);
  for (@a2a) { if ($_) { $f2{$_}++; } }

  if ($miss{$line}) { $missFound++; $endString .= "****** $missFound $line\n"; } else { $count++; if ($count < 1000) { print "$count $line\n"; } elsif ($count == 1000) { print "1000+.\n"; } }
}