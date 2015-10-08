use integer;

my %inStack;

init();

drawSix();

printdeck();

while (1)
{
  $q = <STDIN>;
  if ($q =~ /^debug/) { printdeckraw(); next; }
  if ($q =~ /^d/) { drawSix(); printdeck(); next; }
  if ($q =~ /^h/) { showhidden(); next; }
  if ($q =~ /^l/) { printdeck(); next; }
  if ($q =~ /^$/) { printdeck(); next; }
  if ($q =~ /^r/) { init(); drawSix(); printdeck(); next; }
  if ($q =~ /^[1-6] *[1-6]/) { tryMove($q); next; }
  if ($q =~ /^[qx]/) { last; }
  if ($q =~ /^\?/) { usage(); next; }
#cheats

  if ($q =~ /^z/) { $stack[5][4] = 17; printdeck(); next; }
  if ($q =~ /^t1/) { setPushMult(); printdeck(); next; }
  if ($q =~ /^t2/) { setPushEmpty(); printdeck(); next; }

  print "That wasn't recognized. Push ? for usage.\n";
}
exit;

sub setPushMult
{
@stack = (
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[10, 9],
[5, 4],
[],
[],
[],
[],
);
}

sub setPushEmpty
{
@stack = (
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[-1, 10, 9, 5, 4],
[],
[],
[],
[],
);
}

sub init
{

$hidCards = 16;
$cardsInPlay = 16;
$drawsLeft = 6;

for (1..52) { $inStack{$_} = 1; }

@stack = (
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[-1, -1, -1],
[-1, -1, -1],
[-1, -1],
[-1, -1],
[-1, -1, -1],
[-1, -1, -1],
);

}

sub drawSix
{
if ($drawsLeft == 0) { print "Can't draw any more!\n"; return; }
for (1..6)
{
  push (@{$stack[$_]}, randcard());
}
$drawsLeft--;
$cardsInPlay += 6;
}

sub randcard
{
  $rand = (keys %inStack)[rand keys %inStack];
  delete $inStack{$rand};
  #print "Returning $rand\n";
  return $rand;
}

sub faceval
{
  if ($_[0] == -1) { return "**"; }
  my $x = $_[0] - 1;
  @sui = ("C", "D", "H", "S");
  @vals = ("A", 2, 3, 4, 5, 6, 7, 8, 9, 10, "J", "Q", "K");
  my $suit = @sui[$x/13];
  return "$vals[$x%13]$suit";
  
}

sub printdeck
{
  for $d (1..6)
  {
    print "$d:";
    for $q (0..$#{$stack[$_]}) { if ($stack[$d][$q]) { print faceval($stack[$d][$q]) . " "; } }
	print "\n";
  }
  showLegals();
    print "$cardsInPlay cards in play, $drawsLeft draws left, $hidCards hidden cards.\n";
}

sub printdeckraw
{
  for $d (1..6)
  {
    print "$d:";
    for $q (0..$#{$stack[$_]}) { if ($stack[$d][$q]) { print $stack[$d][$q] . " "; } }
	print "\n";
  }
  showLegals();
  print "Left: "; for $j (sort { $a <=> $b } keys %inStack) { print " $j"; } print "\n";
    print "$cardsInPlay cards in play, $drawsLeft draws left.\n";
}

sub showLegals
{
  my @idx;
  my @blank = (0,0,0,0,0,0);
  for $d(1..6)
  {
    $curEl = 0;
    while ($stack[$d][$curEl]) { $curEl++; }
	@idx[$d] = $curEl - 1;
	if (@idx[$d] < 0) { @blank [$d] = 1; @idx[$d] = 0; }
  }
  #for $thi (0..5) { print "Stack $thi (@idx[$thi]): $stack[$thi][@idx[$thi]]\n"; }
  print "Legal moves:";
  for $from (1..6)
  {
    for $to (1..6)
	{
	  if ($from == $to) {}
	  elsif (@blank[$to] == 1) { print " $from$to"; }
	  elsif (cromu($stack[$from][@idx[$from]], $stack[$to][@idx[$to]])) { print " $from$to"; }
	}
  }
  print "\n";
}

sub cromu
{
  if ($_[0] > $_[1]) { return 0; }
  my $x = ($_[0] - 1) / 13;
  my $y = ($_[1] - 1) / 13;
  #print "$_[0] vs. $_[1]: $x =? $y\n";
  if ($x != $y) { return 0; }
  return 1;
}

sub tryMove
{
  my @q = split(/ */, $_[0]);
  my $from = @q[0];
  my $to = @q[1];
  
  #print "$_[0] becomes $from $to\n";
  
  if ($from==$to) { print "The numbers should be different.\n"; return; }

  my $toEl = 0;
  my $fromEl = 0;
  while ($stack[$to][$toEl])
  {
    #print "Skipping $stack[$to][$toEl]\n";
	$toEl++;
  }
  $toEl--;
  #print "$toEl elts\n";

   while ($stack[$from][$fromEl]) { $fromEl++; }
  $fromEl--;
  #print "$fromEl elts\n";
  #print "From " . $stack[$from][$fromEl] . "\n";
  #print "To " . $stack[$to][$toEl] . "\n";
  if (($toEl > -1) && ($fromEl > -1))
  {
	if (!cromu($stack[$from][$fromEl], $stack[$to][$toEl]))
	{
	  print "Card needs to be placed on empty stack or a same-suit card of greater value (kings high).\n";
	  return;
	}
  }

  print "Start at $fromEl\n";
  while ($fromEl > 0)
  {
    if ($stack[$from][$fromEl-1] != $stack[$from][$fromEl] + 1) { last; }
	$fromEl--;
  }
  #print "Going from $from-$fromEl to $to-$toEl\n";
  while ($stack[$from][$fromEl])
  {
  push (@{$stack[$to]}, $stack[$from][$fromEl]);
  splice (@{stack[$from]}, $fromEl, 1);
  }
  if ($stack[$from][0] == -1) #see about turning a card over
  {
    $fromLook = 0;
	while ($stack[$from][$fromLook] == -1) { $fromLook++; }
	if ($stack[$from][$fromLook] == 0)
	{
	$fromLook--;
	$stack[$from][$fromLook] = randcard; $hidCards--;
	}
  }
  printdeck();
  
}

sub showhidden
{
  print "Still off the board: "; for $j (sort { $a <=> $b } keys %inStack) { print " " . faceval($j); } print "\n";
}

sub usage
{
print<<EOT;
[1-6][1-6] moves stack a to stack b
q/x quits
r restarts
l/(blank) prints it
d draws 6 cards
EOT
}