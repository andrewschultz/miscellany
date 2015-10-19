use integer;
use List::Util 'shuffle';

my %inStack;
@toggles = ( "off", "on" );

readScoreFile(); initGlobal();

initGame(); printdeck();

if (@ARGV[0]) { @cmds = split(/;/, @ARGV[0]); }

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
  if ($_[0] =~ /^ +[^ ]/) { $_[0] =~ s/^ *//g; } #trim leading spaces first

  if ($_[0] =~ /^sd/) { saveDefault(); return; }
  if ($_[0] =~ /^[0-9]$/)
  {
    if ($_[0] !~ /[1-6]/) { print "Valid rows are to auto-move are 1-6.\n"; }
    my $fromCard = $stack[$_[0]][$#{$stack[$_[0]]}];
	my $totalRows = 0;
	my $anyEmpty = 0;
    for $tryRow (1..6)
	{
	  my $toCard = $stack[$tryRow][$#{$stack[$tryRow]}];
	  if ($#{$stack[$tryRow]} < 0) { $anyEmpty++; }
	  #print "$fromCard - $toCard, " . cromu($fromCard, $toCard) . " $#{$stack[$tryRow]} && $emptyIgnore\n";
	  if ((cromu($fromCard, $toCard)) || (($#{$stack[$tryRow]} < 0) && !$emptyIgnore))
	  { if ($tryRow != $_[0])
	    { $totalRows++; $forceRow = $tryRow; #print "$tryRow works. $#{$stack[$tryRow]}\n";
	    }
	  }
	}
	  if ($totalRows == 0) { print "No row to move $_[0] to."; if ($anyEmpty) { print " There's an empty one, but you disabled it with e."; } print "\n"; return; }
	  elsif ($totalRows > 1) { print "Too many rows ($totalRows) to move $_[0] to.\n"; return; }
	  else { print "Forcing $_[0] -> $forceRow.\n"; tryMove("$_[0]$forceRow"); return; }
  }
  if ($_[0] =~ /^uu$/) { undoToStart(); return; }
  if ($_[0] =~ /^u$/) { undo(); return; }
  if ($_[0] =~ /^o$/) { showOpts(); return; }
  if ($_[0] =~ /^debug/) { printdeckraw(); return; }
  if ($_[0] =~ /^dy/) { drawSix(); printdeck(); return; }
  if ($_[0] =~ /^cb/) { $chainBreaks = !$chainBreaks; print "Showing bottom chain breaks @toggles[$chainBreaks].\n"; return; }
  if ($_[0] =~ /^e$/) { $emptyIgnore = !$emptyIgnore; print "Ignoring empty cell for one-number move @toggles[$emptyIgnore].\n"; return; }
  if ($_[0] =~ /^d/) { if (($anySpecial) && ($drawsLeft)) { print "Push dy to force--there are still potentially good moves.\n"; return; } else { drawSix(); printdeck(); return; } }
  if ($_[0] =~ /^h/) { showhidden(); return; }
  if ($_[0] =~ /^l=/i) { loadDeck($_[0]); return; }
  if ($_[0] =~ /^c/) { $collapse = !$collapse; print "Card collapsing @toggles[$collapse].\n"; return; }
  if ($_[0] =~ /^s=/i) { saveDeck($_[0]); return; }
  if ($_[0] =~ /^t=/i) { loadDeck($_[0], "debug"); return; }
  if (($_[0] =~ /^ *$/) || ($_[0] =~ /^-/)) { printdeck(); checkwin(); return; }
  if ($_[0] =~ /^v/) { $vertical = !$vertical; print "Vertical view @toggles[$vertical].\n"; return; }
  if ($_[0] =~ /^z/) { print "Time passes more slowly than if you actually played the game."; return; }
  if ($_[0] =~ /^ua/) { print join(",", @undoArray) . "\n"; return; }
  if ($_[0] =~ /^(f|f=)/) { forceArray($_[0]); return; }
  if ($_[0] =~ /^lu/) { if ($fixedDeckOpt) { peekAtCards(); } else { print "Must have fixed-deck card set.\n"; } return; }
  if ($_[0] =~ /^ra/) { if (($drawsLeft < 5) || ($hidCards < 16)) { print "Need to restart to toggle randomization.\n"; return; } $fixedDeckOpt = !$fixedDeckOpt; print "fixedDeck card-under @toggles[$fixedDeckOpt].\n"; return; }
  if ($_[0] =~ /^ry/) { if ($drawsLeft) { print "Forcing restart despite draws left.\n"; } doAnotherGame(); return; }
  if ($_[0] =~ /^r/) { if ($drawsLeft) { print "Use RY to clear the board with draws left.\n"; return; } doAnotherGame(); return; }
  if ($_[0] =~ /^%/) { stats(); return; }
  if ($_[0] =~ /^a[0-9][0-9]/) { altUntil($_[0]); return; }
  if ($_[0] =~ /^[0-9][0-9][^0-9]/) { $_[0] = substr($_[0], 0, 2); tryMove($_[0]); tryMove(reverse($_[0])); return; }
  if ($_[0] =~ /^[0-9][0-9][0-9]/)
  { # detect 2 ways
    @x = split(//, $_[0]);
	tryMove("@x[0]@x[1]");
	tryMove("@x[0]@x[2]");
	tryMove("@x[1]@x[2]");
	return;
  }
  if ($_[0] =~ /^[0-9] *[0-9]/) { tryMove($_[0]); return; }
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
initGame(); printdeck();
}

sub saveDeck
{
  chomp($_[0]);
  my $filename = "al.txt";
  my $overwrite = 0;
  
  open(A, "$filename");
  open(B, ">albak.txt");
  while ($a = <A>)
  {
    print B $a;
	if ($a =~ /^;/) { last; }
    if ($a =~ /^$_[0]/)
	{
      print "Overwriting entry $_[0]\n";
	  $overwrite = 1;
	  <A>;
	  print B "$vertical,$collapse\n";
	  print B "TC=" . join(",", @topCard) . "\n";
	  print B "M=" . join(",", @undoArray) . "\n";
	  if ($fixedDeckOpt)
	  {
	    print B "FD=" . join(",", @oneDeck) . "\n";
		for (1..6) { print B "HC=" . join(",", @{$backupCardUnder[$_]}) . "\n"; }
	  }
	  for (1..6) { print B join(",", @{$stack[$_]}); print B "\n"; }
	  for (1..6) { <A>; }
	}
  }
  
  if (!$overwrite)
  {
    print "Saving new entry $_[0]\n";
    print B "$_[0]\n";
	<A>;
	print B "$vertical,$collapse\n";
	print B "TC=" . join(",", @topCard) . "\n";
	print B "M=" . join(",", @undoArray) . "\n";
	if ($fixedDeckOpt)
	{
	  print B "FD=" . join(",", @oneDeck) . "\n";
	  for (1..6) { print B "HC=" . join(",", @{$backupCardUnder[$_]}) . "\n"; }
	}
	for (1..6) { print B join(",", @{$stack[$_]}); print B "\n"; }
	for (1..6) { <A>; }
  }
  
  while ($a = <A>) { print B $a; }
  
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
  my $li = 0;
  my @temp;
  
  my $q = <A>; chomp($q); @opts = split(/,/, $q); $vertical = @opts[0]; $collapse = @opts[1]; # read in default values
  my $hidRow = 0;
  
  while ($a = <A>)
  {
    $li++;
    chomp($a);
	$fixedDeckOpt = 0;
	my $rowsRead = 0;
	if ($a =~ /$;/) { last; }
    if ("$a" eq "$search")
	{
	print "Found $search in $filename, line $li.\n";
	$a = <A>; chomp($a); @temp = split(/,/, $a); $vertical = @temp[0]; $collapse = @temp[1];
	#topCards line
    $hidCards = 0;
   $cardsInPlay = 0; $drawsLeft = 5;
    for (1..52) { $inStack{$_} = 1; }
	while ($rowsRead < 6)
	{
	  $a = <A>; chomp($a);
	  $b = $a; $b =~ s/^[A-Z]+=//g; #b = the data for a
	  if ($a =~ /^FD=/)
	  {
	    $fixedDeckOpt = 1;
	    @fixedDeck = split(/,/, $a);
		next;
	  }
	  if ($a =~ /^TC=/)
	  {
		@topCard = split(/,/, $b);
		next;
	  }
	  if ($a =~ /^M=/)
	  {
		@undoArray = split(/,/, $b);
		next;
	  }
	  if ($a =~ /^HC=/)
	  {
	    $hidRow++;
		@{backupCardUnder[$hidRow]} = split(/,/, $b);
		@{cardUnder[$hidRow]} = split(/,/, $b);
		next;
	  }
	  $rowsRead++;
	  @{$stack[$rowsRead]} = split(/,/, $a);
	    for $card (@{$stack[$rowsRead]})
	    {
		if ($card > 0)
		{
		  $cardsInPlay++;
		  #print "$card in $curRow makes $cardsInPlay\n";
		  delete($inStack{$card});
		} elsif ($card == -1) { $cardsInPlay++; $hidCards++; }
	    }
	  $drawsLeft = (52-$cardsInPlay)/6;
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
    for my $card (@{$stack[$_]}) { if ($card == -1) { $retVal++; } }
  }
  return $retVal;
}

sub forceArray
{
    my $card = $_[0]; $card =~ s/^(f|f=)//g;
	
	if (!$hidden) { print "Too many cards out.\n"; return; }
	
	if ($card == 0) { push(@force, $card); print "Forcing null, for instance, for a draw.\n"; return; }
	if (($card <= 52) && ($card >= 1))
	{
	if (!$inStack{$card}) { print "$card (" . faceval($card) . ") already out on the board.\n"; return; }
	push (@force, $card); delete ($inStack{$card}); if ((!$undo) && (!$quickMove)) { print faceval($card) . " successfully pushed.\n"; }
	return;
	}
	
	for $su (0..$#suit)
	{
	  if ($card =~ /$su/)
	  {
	    $dumpVal = 13 * $_; $card =~ s/$su//g;
		for $fv (0..$#vals) { if ($card =~ /$fv/) { $dumpVal += ($fv + 1); print "$_[0] successfully pushed.\n"; return; } }
	  }
	}
  if (!$gotFaceVal) { print "Card must be of the form [A23456789 10 JQK][CDHS], or the matching number.\nFace value = C=0 D=13 H=26 S=39.\n"; return; }
}

sub initGame
{

$hidCards = 16;
$cardsInPlay = 16;
$drawsLeft = 6;

@undoArray = ();

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

drawSix();

deckFix();

}

sub drawSix
{
if ($drawsLeft == 0) { print "Can't draw any more!\n"; return; }
for (1..6)
{
  if ($fixedDeckOpt)
  {
  push(@{$stack[$_]}, @fixedDeck[0]);
  shift(@fixedDeck);
  }
  else
  {
  my $thiscard = randcard();
  push (@{$stack[$_]}, $thiscard);
  if ((!$undo) && ($drawsLeft < 6)) { push(@undoArray, "f$thiscard"); }
  }
  if ($drawsLeft == 6) { @topCard[$_] = $stack[$_][$#{$stack[$_]}]; }
}
if ((!$undo) && ($drawsLeft < 6)) { push(@undoArray, "dy"); }
$drawsLeft--;
$cardsInPlay += 6;
}

sub randcard
{
  if (@force[0]) { $rand = @force[0]; shift(@force); }
  else
  {
  if (@force[0] eq "0") { shift(@force); }
  $rand = (keys %inStack)[rand keys %inStack];
  }
  delete $inStack{$rand};
  #print "Returning $rand\n";
  return $rand;
}

sub faceval
{
  if ($_[0] == -1) { return "**"; }
  my $x = $_[0] - 1;
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
  my $anyJumps = 0;
  for $d (1..6) { $anyJumps += jumpsFromBottom($d); }

  for $d (1..6)
  {
    $thisLine = "$d:";
	if (($anyJumps > 0) && ($chainBreaks))
	{
	  my $temp = jumpsFromBottom($d);
	  if ($temp) { $thisLine = "($temp) $thisLine"; } else { $thisLine = "    $thisLine"; }
	}
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
	if ((!$undo) && (!$quickMove)) { print "$thisLine\n"; }
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

sub jumpsFromBottom
{
    my $thisdif = 0;
    for ($thisone = $#{$stack[$_[0]]}; $thisone >= 1; $thisone--  )
	{
	  if (!cromu($stack[$_[0]][$thisone], $stack[$_[0]][$thisone-1])) { last; }
	  if ($stack[$_[0]][$thisone-1] - $stack[$_[0]][$thisone] > 1)
	  {
	    $thisdif++;
	  }
	}
	return $thisdif;
}

sub printdeckvertical
{
  my @deckPos = (0, 0, 0, 0, 0, 0, 0);
  my @lookAhead = (0, 0, 0, 0, 0, 0, 0);
  my @xtrChr = (" ", "=");
  my $temp;
  my $myString = "";
  my $anyJumps = 0;
  if ($chainBreaks)
  {
  for $row (1..6)
  {
    if ($temp = jumpsFromBottom($row)) { $myString .= "  ($temp)"; } else { $myString .= "     "; }
    @lookAhead[$row] = 0;
  }
  if (($myString =~ /[0-9]/) && (!$undo) && (!$quickMove)) { print "$myString\n"; }
  }
  if ((!$undo) && (!$quickMove))
  {
  for $row (1..6)
  {
    print "   ";
	if ($stack[$row][0]) { print " "; } else { print "!"; }; print "$row";
  }
  print "\n";
  }
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
  if (($foundCard) && (!$undo) && (!$quickMove)) { print "$thisLine\n"; }
  } while ($foundCard);
  showLegalsAndStats();
}

sub showLegalsAndStats
{
  if (($undo) || ($quickMove)) { return; }
  my @idx;
  my @blank = (0,0,0,0,0,0);
  my @circulars = (0,0,0,0,0,0);
  my $canMakeEmpty = 0;
  
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
	  if ($from == $to) { next; }
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
		  print "*"; $anySpecial = 1; @circulars[$to]++;
		  }
		elsif (($stack[$from][$thisEl-1] < $stack[$from][$thisEl]) && ($stack[$from][$thisEl-1] != -1))
		  {
		  print "<"; $anySpecial = 1;
		  }
		}
		else
		{
		  print "E"; $canMakeEmpty = 1;
		}
		if (suit($stack[$from][$thisEl-1]) == suit($stack[$from][$thisEl]))
		{
		  if (suit($stack[$from][$thisEl]) == suit($stack[$to][@idx[$to]]))
		  {
		    if (($stack[$from][$thisEl] < $stack[$to][@idx[$to]]) && ($stack[$from][$thisEl] < $stack[$from][$thisEl-1]))
			{
			  print "C"; @circulars[$to]++;
			}
		  }
		}
		print "$from$to";
		if (($stack[$from][$thisEl] == $stack[$to][@idx[$to]] - 1) && ($stack[$from][$thisEl] % 13)) { print "+"; $anySpecial = 1; }
	  }
	  if (!$stack[$to][0]) { print "e"; if (!$emptyIgnore) { $anySpecial = 1; } }
	} #?? maybe if there is no descending, we can check for that and give a pass
  }
  for $toPile (1..6) { if (@circulars[$toPile] > 1) { $anySpecial = 1; print " " . (X x (@circulars[$toPile]-1)) . "$toPile"; } }
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
  
  if ($anySpecial)
  {
    $allBalanced = 1;
    for $row (1..6)
	{
	  for $card (1..$#{$stack[$row]})
	  {
	    if (!cromu($stack[$row][$card], $stack[$row][$card-1])) { $allBalanced = 0; }
		#else { print "$stack[$row][$card], $stack[$row][$card-1] ok\n"; }
	  }
	}
	if ($allBalanced) { $anySpecial = 0; }
  }
  
  if ((!$anySpecial) && (!$allBalanced) && ($cardsInPlay == 52))
  {
    my $gotEmpty = 0;
    for (1..6)
	{
	  if (!$stack[$_][0]) { $gotEmpty = 1; }
	}
	 if (($gotEmpty) || ($canMakeEmpty)) { print "Still an empty slot.\n"; } else { print "This is likely unwinnable.\n"; }
  }

  my $visible = $cardsInPlay - $hidCards;
  my $breaks = 0;
  for my $breakRow (1..6)
  {
    for (0..$#{$stack[$breakRow]} - 1)
	{
	  if ($stack[$breakRow][$_] != -1)
	  {
	    if (($stack[$breakRow][$_] - $stack[$breakRow][$_+1] != 1) || (suit($stack[$breakRow][$_+1]) != suit($stack[$breakRow][$_+1])))
		{
		  $breaks++;
		}
	  }
	}
  }
  print "$cardsInPlay cards in play, $visible/$hidCards visible/hidden, $drawsLeft draws left, $breaks breaks, $chains chains, $order in order.\n";
}

sub suit
{
  if ($_[0] == -1) { return -1; }
  return ($_[0]-1) / 13;
}

sub cromu
{
  if ($_[0] >= $_[1]) { return 0; }
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
  
  if (($from > 6) || ($from < 1) || ($to > 6) || ($to < 1)) { print "$from-$to is not valid. Rows range from 1 to 6."; $moveBar = 1; return; }
  
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
  splice (@{$stack[$from]}, $fromEl, 1);
  }
  if ($stack[$from][0] == -1) #see about turning a card over
  {
    $fromLook = 0;
	while ($stack[$from][$fromLook] == -1) { $fromLook++; }
	if ($stack[$from][$fromLook] == 0)
	{
	$fromLook--;
	if ($fixedDeckOpt)
	{
	$stack[$from][$fromLook] = $cardUnder[$from][$#{$cardUnder[$from]}];
	pop(@{$cardUnder[$from]});
	}
	else
	{
	$stack[$from][$fromLook] = randcard;
	if (!$undo) { push(@undoArray, "f$stack[$from][$fromLook]"); }
	}
	$hidCards--;
	}
  }
  if (!$undo) { push(@undoArray, "$from$to"); }
  printdeck();
  checkwin();
}

sub altUntil
{
  my @cmds = split(//, $_[0]);
  my $from = @cmds[1];
  my $to = @cmds[2];
  my $totalMoves = 0;
  if (($from < 1) || ($from > 6) || ($to < 1) || ($to > 6)) { print "From/to must be between 1 and 6.\n"; }
  $quickMove = 1;
  #print "$from$to trying\n";
  if (!canChain($from,$to))
  {
    if (canChain($to, $from)) { $temp = $from; $from = $to; $to = $temp; }
	else { print "These two rows aren't switchable.\n"; }
  }
  #print "$to$from trying\n";
  while (canChain($from, $to))
  {
    tryMove("$from$to"); #print "$to$from trying\n";
    if ($moveBlocked == 1) { print "Move was blocked. This should never happen.\n"; last; }
	$temp = $from; $from = $to; $to = $temp;
	$totalMoves++;
  }
  $quickMove = 0;
  printdeck();
  print "Made $totalMoves moves.\n";
}

sub canChain
{
  my $toCard = $stack[$_[1]][$#{$stack[$_[1]]}];
  if ($toCard % 13 == 1) { return 0; } # if it is an ace, there's no way we can chain
  my $fromLoc = $#{$stack[$_[0]]};
  #print "CanChain: on to $toCard From: $stack[$_[0]][$fromLoc-1] $stack[$_[0]][$fromLoc]\n";
  while (($fromLoc > 0) && ($stack[$_[0]][$fromLoc-1] -  $stack[$_[0]][$fromLoc] == 1))
  {
    #print "...$stack[$_[0]][$fromLoc-1] $stack[$_[0]][$fromLoc]\n";
    $fromLoc--;
  }
  #print "CanChainAfter: on to $toCard From: $stack[$_[0]][$fromLoc-1] $stack[$_[0]][$fromLoc]\n";
  if ($toCard - $stack[$_[0]][$fromLoc] == 1)
  {
    return 1;
  }
  return 0;
}

sub reinitBoard
{
  my @depth = (0, 3, 3, 2, 2, 3, 3);
  $cardsInPlay = 22;
  $drawsLeft = 5;
  $hidCards = 16;
  for (1..52) { $inStack{$_} = 1; }
  for (1..6)
  {
    @{$stack[$_]} = ();
    for $x (1..@depth[$_]) { push (@{$stack[$_]}, -1); }
	push (@{$stack[$_]}, @topCard[$_]);
	delete($inStack{@topCard[$_]});
  }
}

sub undoToStart
{
  reinitBoard();
  @cardUnder = @backupCardUnder;
  @fixedDeck = @oneDeck;
  printdeck();
}

sub undo
{
  $undo = 1;
  #if ($#undoArray == -1) { print "Nothing to undo.\n"; return;}
  reinitBoard();
  print "$cardsInPlay cards in play.\n";
  $x = $#undoArray;
  print "$x elts left\n";
  if ($x >= 0)
  {
    $temp = pop(@undoArray);
	$x--;
	print "Popped $temp\n";
	while ((@undoArray[$x] =~ /^f/) && ($x >= 0))
	{
	  $x--;
	  $temp = pop(@undoArray);
	  print "extra-popped $temp\n";
	}
  }
  print "@undoArray\n";
  for (0..$#undoArray)
  {
    for $j (1..52) { if (!$inStack{$j}) { print "$j=" . faceval($j) . " "; } } print "\n";
    procCmd(@undoArray[$_]);
  }
  $undo = 0;
  printdeck();
}

sub showhidden
{
  if ($hidCards == 0) { print "Nothing hidden left.\n"; }
  my $lastSuit = -1;
  print "Still off the board:";
  for $j (sort { $a <=> $b } keys %inStack)
  {
    if ($lastSuit != suit($j)) { $lastSuit = suit($j); print "\n" . faceval($j); } else { print " " . faceval($j); }
  }
  print " (" . (keys %inStack) . " total)\n";
}

sub checkwin
{
  my $suitsDone = 0;
  
  OUTER:
  for $stax (1..6)
  {
    my @x = @{$stack[$stax]};
	#print "$stax: total $#{$stack[$stax]}\n";
	for (0..$#x)
	{
	  $inarow = 0;
	  if ((@x[$_] > 0) && (@x[$_] % 13 == 0))
	  {
	    while ((@x[$_] - @x[$_+1] == 1) && (@x[$_+1]) && (suit(@x[$_]) == suit(@x[$_+1]))) { $_++; $inarow++; }
	  }
	  if ($inarow == 12) { $suitsDone++; }
	}
  }
  if ($suitsDone == 4) { print "You win! Push enter to restart."; $x = <STDIN>; $youWon = 1; doAnotherGame(); return; }
  elsif ($suitsDone) { print "$suitsDone suits completed.\n"; }
}

sub peekAtCards
{
  print "On draw:";
  for (0..$#fixedDeck)
  {
    if (($_) && ($_ % 6 == 0)) { print " |"; }
    print " " . faceval(@fixedDeck[$_]);
  }
  print "\n";
  for $thisrow(1..6)
  {
    $idx = 0;
    while ($stack[$thisrow][$idx] == -1)
	{
	  if ($idx == 0) { print "Row $thisrow:"; }
	  print faceval($cardUnder[$thisrow][$idx]);
	  $idx++;
	}
	if ($idx) { print "\n"; }
  }
}

sub deckFix
{
  @fixedDeck = ();
  my @blanks = (0,3,3,2,2,3,3);
  @oneDeck = shuffle(keys %inStack);
  #print "$#oneDeck: @oneDeck\n";
	for $thisrow(1..6)
	{
	  for (1..@blanks[$thisrow])
	  {
	    $cardUnder[$thisrow][$_-1] = pop(@oneDeck);
		$backupCardUnder[$thisrow][$_-1] = $cardUnder[$thisrow][$_-1];
		#print "Popped $cardUnder[$thisrow][$_].\n";
	  }
	}
	@fixedDeck = @oneDeck;
	#print "$#fixedDeck: @fixedDeck\n";
}

sub stats
{
 print "$wins wins $losses losses\n";
 if ($wstreak) { print "current streak = $wstreak wins\n"; }
 elsif ($lstreak) { print "current streak = $lstreak losses\n"; }
 print "Longest streak $lwstreak wins $llstreak losses\n";
 printf("Win percentage = %d.%02d\n", ((100*$wins)/($wins+$losses)), ((10000*$wins)/($wins+$losses)) % 100);
}

sub saveDefault
{
  my $filename = "al.txt";
  open(A, "$filename");
  <A>;
  open(B, ">albak.txt");
  print B "$vertical,$collapse\n";
  while ($a = <A>) { print B $a; }
  close(A);
  close(B);
  `copy albak.txt al.txt`;
}

sub initGlobal
{
  $vertical = $collapse = 0;
  @sui = ("C", "D", "H", "S");
  @vals = ("A", 2, 3, 4, 5, 6, 7, 8, 9, 10, "J", "Q", "K");

  open(A, "al.txt");
  my $a = <A>; chomp($a); my @opts = split(/,/, $a); $vertical = @opts[0]; $collapse = @opts[1]; close(A);
}

sub showOpts
{
  print "Vertical view (v) @toggles[$vertical].\n";
  print "Collapsing (c) @toggles[$collapse].\n";
  print "Fixed deck (ra) @toggles[$fixedDeckOpt].\n";
  print "Ignore Empty on Force (e) @toggles[$emptyIgnore].\n";
  print "Show Chain Breaks (cb) @toggles[$chainBreaks].\n";
}

sub readScoreFile
{
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
}

sub usage
{
print<<EOT;
[1-6] moves that row, if there is exactly one suitable destination
[1-6][1-6] moves stack a to stack b
[1-6][1-6]0 (or any character moves stack a to stack b and back
[1-6][1-6][1-6] moves from a to b, a to c, b to c.
v toggles vertical view (default is horizontal)
c toggles collapsed view (8h-7h-6h vs 8h=6h)
cb shows chain breaks e.g. KH-JH-9H-7H has 3
e toggles empty-ignore on eg if 2H can go to an empty cell or 6H, with it on, 1-move goes to 6H.
q/x quits
r restarts, ry forces if draws are left
(blank) or - prints the screen
d draws 6 cards (you get 5 of these), dy forces if "good" moves are left
s=saves deck name
h=shows hidden/left cards
l=loads deck name
t=loads test
sd=save default
u=undo
uu=undo all the way to the start
%=prints stats
o=prints options
EOT
}