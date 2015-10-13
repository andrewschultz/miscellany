use integer;

my %inStack;
@toggles = ( "off", "on" );

open(A, "scores.txt");

$wins = $losses = $wstreak = $lstreak = $lwstreak = $llstreak = 0;

if (!fileno(A)) { print "No scores.txt\n"; }
else
{
print "Reading scores...\n";
$stats = <A>; chomp($stats); @pcts = split(/,/, $stats);
$wins = @pcts[0];
$losses = @pcts[1];
$wstreak = @pcts[2];
$lstreak = @pcts[3];
$lwstreak = @pcts[4];
$llstreak = @pcts[5];
close(A);
}

$vertical = $collapse = 0;

init(); drawSix(); printdeck();

if (@ARGV[0]) { @cmds = split(/;/, @ARGV[0]); for $initCmd(@cmds) { print "!$initCmd!\n"; procCmd($initCmd); } }

while (1)
{
  $oneline = <STDIN>;
  if ($oneline =~ /;/) { @cmds = split(/;/, $oneline); for $myCmd (@cmds) { procCmd($myCmd); } }
  else { procCmd($oneline); }
}
exit;

sub procCmd
{
  chomp($_[0]);
  $moveBar = 0;
  if ($_[0] =~ /^[1-6]$/) { print "Need a 2nd row.\n"; }
  if ($_[0] =~ /^ +[^ ]/) { $_[0] =~ s/^ *//g; } #trim leading spaces
  if ($_[0] =~ /^debug/) { printdeckraw(); return; }
  if ($_[0] =~ /^dy/) { drawSix(); printdeck(); return; }
  if ($_[0] =~ /^d/) { if ($anySpecial) { print "Push dy to force--there are still potentially good moves.\n"; return; } else { drawSix(); printdeck(); return; } }
  if ($_[0] =~ /^h/) { showhidden(); return; }
  if ($_[0] =~ /^l=/i) { loadDeck($_[0]); return; }
  if ($_[0] =~ /^c/) { $collapse = !$collapse; print "Card collapsing @toggles[$collapse].\n"; return; }
  if ($_[0] =~ /^s=/i) { saveDeck($_[0]); return; }
  if ($_[0] =~ /^t=/i) { loadDeck($_[0], "debug"); return; }
  if (($_[0] =~ /^ *$/) || ($_[0] =~ /^-/)) { printdeck(); return; }
  if ($_[0] =~ /^v/) { $vertical = !$vertical; print "Vertical view @toggles[$vertical].\n"; return; }
  if ($_[0] =~ /^z/) { print "Time passes more slowly than if you actually played the game."; return; }
  if ($_[0] =~ /^ry/) { if ($drawsLeft) { print "Forcing restart despite draws left.\n"; } doAnotherGame(); return; }
  if ($_[0] =~ /^r/) { if ($drawsLeft) { print "Use RY to clear the board with draws left.\n"; return; } doAnotherGame(); return; }
  if ($_[0] =~ /^%/) { stats(); return; }
  if ($_[0] =~ /^[1-6] *[1-6]/) { tryMove($_[0]); return; }
  if ($_[0] =~ /^[1-6][1-6][^1-9]/) { $_[0] = substr($_[0], 0, 2); tryMove($_[0]); tryMove(reverse($_[0])); return; }
  if ($_[0] =~ /^[1-6][1-6][1-6]/)
  { # detect 2 ways
    @x = split(//, $_[0]);
	tryMove("@x[0]@x[1]");
	tryMove("@x[0]@x[2]");
	tryMove("@x[1]@x[2]");
	return;
  }
  if ($_[0] =~ /^[qx]/) { exit; }
  if ($_[0] =~ /^\?/) { usage(); return; }
#cheats

  print "Command ($_[0]) wasn't recognized. Push ? for usage.\n";
}

sub doAnotherGame
{
if ($youWon) { $youWon = 0; $wins++; $wstreak++; $lstreak=0; if ($wstreak > $lwstreak) { $lwstreak = $wstreak; } }
elsif ($hidCards == 16) { }
else { $losses++; $wstreak = 0; $lstreak++; if ($lstreak > $llstreak) { $llstreak = $lstreak; } }

open(A, ">scores.txt");
print A "$wins,$losses,$wstreak,$lstreak,$lwstreak,$llstreak";
close(A);
init(); drawSix(); printdeck();
}

sub saveDeck
{
  chomp($_[0]);
  my $filename = "al.txt";
  
  open(A, "$filename");
  open(B, ">albak.txt");
  while ($a = <A>)
  {
	if ($a =~ /^;/) { last; }
    print B $a;
    if ($a =~ /^s=$_[0]/)
	{
	  $overwrite = 1;
	  <A>;
	  print B "$vertical,$collapse\n";
	  for (1..6) { print B join(",", @{$stack[$_]}); print B "\n"; }
	  for (1..6) { <A>; }
	}
  }
  
  if (!$overwrite)
  {
    print B "$_[0]\n";
	<A>;
	print B "$vertical,$collapse\n";
	for (1..6) { print B join(",", @{$stack[$_]}); print B "\n"; }
	for (1..6) { <A>; }
  }
  
  close(A);
  close(B);
  
  `copy albak.txt $filename`;

  print "OK, saved.\n";
  printdeck();
}

sub loadDeck
{
  if ($_[1] =~ /debug/) { $filename = "alt.txt"; print "DEBUG test\n"; } else { $filename="al.txt"; }
  chomp($_[0]);
  my $search = $_[0]; $search =~ s/^[lt]/s/gi;
  open(A, "$filename");
  
  while ($a = <A>)
  {
    chomp($a);
	if ($a =~ /$;/) { last; }
    if ("$a" eq "$search")
	{
	print "Found $search in $filename.\n";
	$a = <A>; chomp($a); @temp = split(/,/, $a); $vertical = @temp[0]; $collapse = @temp[1];
    $hidCards = 0;
    for (1..52) { $inStack{$_} = 1; } print "1\n";
    for (1..6)
	{
	  $a = <A>; chomp($a);
	  @{$stack[$_]} = split(/,/, $a);
	  for $card (@{$stack[$_]}) { if ($card > 0) { delete($inStack{$card}); } elsif ($card == -1) { $hidCards++; } }
	  #for $x (sort keys %inStack) { print "$x: " . faceval($x) . "\n"; }
	}
	printdeck();
	close(A);
	return;
	}
  }
  
  print "No $search found in $filename.\n";
}

sub hidCards
{
  my $retVal = 0;
  for my $cardrow (1..6)
  {
    for my $card (@{stack[$_]}) { if ($card == -1) { $retVal++; } }
  }
  return $retVal;
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
  if ($vertical)
  { printdeckvertical(); }
  else
  { printdeckhorizontal(); }
}

sub printdeckhorizontal
{
  for $d (1..6)
  {
    $thisLine = "$d:";
    for $q (0..$#{$stack[$_]})
	{
	$t1 = $stack[$d][$q];
	if (!$t1) { last; }
	$t2 = $stack[$d][$q-1];
	if ($t1)
	{
	if (($q >= 1) && (($t1-1)/13 == ($t2-1)/13))
	{
	  if ($stack[$d][$q-1] -1 == $stack[$d][$q]) { $thisLine .= "-"; }
	  elsif ($stack[$d][$q-1] -1 > $stack[$d][$q]) { $thisLine .= ":"; }
	  else { $thisLine .= " "; }
	}
	else #default
	{
	$thisLine .= " ";
	}
	}
	$thisLine .= faceval($stack[$d][$q]);
	}
	
	if ($collapse) { $thisLine =~ s/-[0-9AKQJCHDS-]+-/=/g; }
	print "$thisLine\n";
  }
  showLegalsAndStats();
}

sub printdeckraw
{
  for $d (1..6)
  {
    print "$d: ";
    for $q (0..$#{$stack[$_]}) { if ($stack[$d][$q]) { print $stack[$d][$q] . " "; } }
	print "\n";
  }
  showLegalsAndStats();
  print "Left: "; for $j (sort { $a <=> $b } keys %inStack) { print " $j"; } print "\n";
    print "$cardsInPlay cards in play, $drawsLeft draws left.\n";
}

sub printdeckvertical
{
  my @deckPos = (0, 0, 0, 0, 0, 0, 0);
  my @lookAhead = (0, 0, 0, 0, 0, 0, 0);
  my @xtrChr = (" ", "=");
  for $row (1..6) { @lookAhead[$row] = 0; print "   "; if ($stack[$row][0]) { print " "; } else { print "!"; }; print "$row"; } print "\n";
  do
  {
  $foundCard = 0;
  $thisLine = "";
  for $row (1..6)
  {
    if ($stack[$row][@deckPos[$row]])
	{
	$thisLine .= " ";
	$foundCard = 1;
	#if ($stack[$row][@deckPos[$row]] % 13 != 10) { $thisLine .= " "; }
	if ($collapse)
	{
	if (@lookAhead[$row])
	{
	while((($stack[$row][@deckPos[$row]] - $stack[$row][@deckPos[$row]+1]) == 1) && ($stack[$row][@deckPos[$row] +1] % 13)) { @deckPos[$row]++; $eq = 1; }
	if ($stack[$row][@deckPos[$row]] % 13 != 10) { $thisLine .= " "; }
	if ($eq) { $thisLine .= "="; } else { $thisLine .= "-"; }
	$thisLine .= faceval($stack[$row][@deckPos[$row]], 1);
	@lookAhead[$row] = 0;
	$eq = 0;
	}
	else
	{
	if ($stack[$row][@deckPos[$row]] % 13 != 10) { $thisLine .= " "; }
	$thisLine .= " " . faceval($stack[$row][@deckPos[$row]], 1);
	}
	if ((($stack[$row][@deckPos[$row]] - $stack[$row][@deckPos[$row]+1]) == 1) && ($stack[$row][@deckPos[$row] +1] % 13))
	{
	  @lookAhead[$row] = 1;
	  #print "$row: $stack[$row][@deckPos[$row]] to $stack[$row][@deckPos[$row]+1]: DING!\n";
	}
	@deckPos[$row]++;
	}
	else
	{
	if ($stack[$row][@deckPos[$row]] % 13 != 10) { $thisLine .= " "; }
	$thisLine .= " " . faceval($stack[$row][@deckPos[$row]], 1);
	@deckPos[$row]++;
	}
	}
	else { $thisLine .= "     "; }
  }
  if ($foundCard) { print "$thisLine\n"; }
  } while ($foundCard);
  showLegalsAndStats();
}

sub showLegalsAndStats
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
  $anySpecial = 0;
  print "Legal moves:";
  for $from (1..6)
  {
    for $to (1..6)
	{
	  if ($from == $to) {}
	  elsif (@blank[$to] == 1) { print " $from$to"; }
	  elsif (cromu($stack[$from][@idx[$from]], $stack[$to][@idx[$to]]))
	  {
	    print " ";
	    $thisEl = @idx[$from];
	    while ($thisEl > 0)
		{
		  if (($stack[$from][$thisEl-1] == $stack[$from][$thisEl] + 1) && ($stack[$from][$thisEl-1] % 13))
		  {
		    $thisEl--;
		  }
		  else { last; }
		}
		if ($thisEl > 0)
		{
		if (suit($stack[$from][$thisEl-1]) != suit($stack[$from][$thisEl]))
		  {
		  print "*"; $anySpecial = 1;
		  }
		elsif (($stack[$from][$thisEl-1] < $stack[$from][$thisEl]) && ($stack[$from][$thisEl-1] != -1))
		  {
		  print "<"; $anySpecial = 1;
		  }
		}
		else
		{
		  print "E";
		}
		if (suit($stack[$from][$thisEl-1]) == suit($stack[$from][$thisEl]))
		{
		  if (suit($stack[$from][$thisEl]) == suit($stack[$to][@idx[$to]]))
		  {
		    if (($stack[$from][$thisEl] < $stack[$to][@idx[$to]]) && ($stack[$from][$thisEl] < $stack[$from][$thisEl-1]))
			{
			  print "C";
			}
		  }
		}
		print "$from$to";
		if (($stack[$from][$thisEl] == $stack[$to][@idx[$to]] - 1) && ($stack[$from][$thisEl] % 13)) { print "+"; $anySpecial = 1; }
	  }
	}
  }
  print "\n";

  $chains = 0; $order = 0;
  for $col (1..6)
  {
    $entry = 1;
	while ($stack[$col][$entry])
	{
	  if (($stack[$col][$entry] % 13) && ($stack[$col][$entry] == $stack[$col][$entry-1] - 1)) { $chains++; $order++; }
	  if (($stack[$col][$entry] < $stack[$col][$entry-1] - 1) && (suit($stack[$col][$entry]) == suit($stack[$col][$entry-1]))) { $order++; }
	  $entry++;
	}
  }

  print "$cardsInPlay cards in play, $drawsLeft draws left, $hidCards hidden cards, $chains chains, $order in order.\n";
}

sub suit
{
  if ($_[0] == -1) { return -1; }
  return ($_[0]-1) / 13;
}

sub cromu
{
  if ($_[0] > $_[1]) { return 0; }
  if (!$_[0]) { return 0; }
  my $x = suit($_[0]);
  my $y = suit($_[1]);
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
  if ($moveBar == 1) { print "$from-$to blocked, as previous move failed.\n"; return; }
  
  if ($from==$to) { print "The numbers should be different.\n"; $moveBar = 1; return; }
  
  if (!$stack[$from][0]) { print "Empty row/column.\n"; $moveBar = 1; return; }

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
	  $moveBar = 1;
	  return;
	}
  }

  #print "Start at $fromEl\n";
  while ($fromEl > 0)
  {
    if (($stack[$from][$fromEl-1] != $stack[$from][$fromEl] + 1) || ($stack[$from][$fromEl] % 13 == 0)) { last; }
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
  checkwin();
  
}

sub showhidden
{
  print "Still off the board: "; for $j (sort { $a <=> $b } keys %inStack) { print " " . faceval($j); } print "\n";
}

sub checkwin
{
  my $suitsDone = 0;
  
  OUTER:
  for $stax (1..6)
  {
    @x = @{$stack[$stax]};
	if (@x == 0) { next; }
	if (@x % 13) { next; }
	if ($#x != 12) { next; }
	$lasty = @x[0];
	for (1..$#x)
	{
	  if (@x[$_] != $lasty - 1)
	  {
	    #print "$stax failed at $_.\n";
        next OUTER;
	  }
	  $lasty--;
	}
	$suitsDone++;
  }
  if ($suitsDone == 4) { print "You win! Push enter to restart."; $x = <STDIN>; $youWon = 1; doAnotherGame(); return; }
  elsif ($suitsDone) { print "$suitsDone suits on their own row/column.\n"; }
}

sub stats
{
 print "$wins wins $losses losses\n";
 if ($wstreak) { print "current streak = $wstreak wins\n"; }
 elsif ($lstreak) { print "current streak = $lstreak losses\n"; }
 print "Longest streak $lwstreak wins $llstreak losses\n";
 printf("Win percentage = %d.%02d", ((100*$wins)/($wins+$losses)), ((10000*$wins)/($wins+$losses)) % 100);
}

sub usage
{
print<<EOT;
[1-6][1-6] moves stack a to stack b
[1-6][1-6]0 (or any character moves stack a to stack b and back
[1-6][1-6][1-6] moves from a to b, a to c, b to c.
v toggles vertical view (default is horizontal)
q/x quits
r restarts
(blank) prints the screen
d draws 6 cards (you get 5)
s=saves deck name
l=loads deck name
t=loads test
EOT
}