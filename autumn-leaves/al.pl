use integer;
use List::Util 'shuffle';

my %inStack;
@toggles = ( "off", "on" );

readScoreFile(); initGlobal();

if ($startWith > 7) { print "First draw may take a bit...\n"; }

initGame(); printdeck();

if (@ARGV[0]) { @cmds = split(/;/, @ARGV[0]); }

while (1)
{
  $oneline = <STDIN>;
  if ($oneline =~ /;/) { @cmds = split(/;/, $oneline); for $myCmd (@cmds) { procCmdFromUser($myCmd); } }
  else { procCmd($oneline); }
  seeBlockedMoves();
}
exit;

sub procCmdFromUser #this is so they can't use debug commands
{
  if (($_[0] eq "n-") || ($_[0] eq "n+")) { print "This is a debug command, so I'm ignoring it.\n"; return; }
  procCmd($_[0]);
}

sub seeBlockedMoves
{
  if ($blockedMoves == 1)
  {
    print "Blocked move not shown.\n";
  }
  elsif ($blockedMoves > 1)
  {
    print "$blockedMoves blocked moves not shown.\n";
  }
  if (!$showBlockedMoves)
  {
  $blockedMoves = 0;
  }
}

sub procCmd
{
  $errorPrintedYet = 0;
  $printedThisTurn = 0;
  chomp($_[0]);
  $_[0] = lc($_[0]);
  $moveBar = 0;
  $_[0] =~ s/^\s+//g;
  if ($_[0] ne "g") { $lastCommand = $_[0]; }

  if ($_[0] =~ /^lw/) { printLastWon(); return; }
  if ($_[0] =~ /^sd/) { saveDefault(); return; }
  if ($_[0] =~ /^[0-9]$/)
  {
    if ($_[0] !~ /[1-6]/) { print "Valid rows are to auto-move are 1-6.\n"; return; }
	my $totalRows = 0;
	my $anyEmpty = 0;
	my $fromCardTop = $#{$stack[$_[0]]};
	my $temp = 0;
	
	while (($fromCardTop > 0) && ($stack[$_[0]][$fromCardTop] == $stack[$_[0]][$fromCardTop-1] - 1) && ($stack[$_[0]][$fromCardTop] % 13)) { $fromCardTop--; } # see if we can move the whole stack
	
    my $fromCard = $stack[$_[0]][$fromCardTop];

    for $tryRow (1..6)
	{
	  my $toCard = $stack[$tryRow][$#{$stack[$tryRow]}];
	  if ($#{$stack[$tryRow]} < 0) { $anyEmpty++; }
	  #print "$fromCard - $toCard, " . cromu($fromCard, $toCard) . " $#{$stack[$tryRow]} && $emptyIgnore\n";
	  if ((cromu($fromCard, $toCard)) || (($#{$stack[$tryRow]} < 0) && !$emptyIgnore))
	  {
	    if (($toCard - $fromCard == 1) && ($fromCard % 13))
		{
		  tryMove("$_[0]$tryRow"); # force 4-3 if we have 4S, QS, 3S
		  return;
		}
	    if ($tryRow != $_[0])
	    { if (($fromCardTop != 0) || ($#{$stack[$tryRow]} != -1)) { $totalRows++; $forceRow = $tryRow; } # empty, Kh-7h, 4h : 4h to 7h #print "$tryRow works. $#{$stack[$tryRow]}\n";
	    }
	  }
	}
	  if ($totalRows == 0) { print "No row to move $_[0] to."; if ($anyEmpty) { print " There's an empty one, but you disabled it with e."; } print "\n"; return; }
	  elsif ($totalRows > 1)
	  {
	    if ((emptyRows() > 0) && ($totalRows > 1)) { print "First empty row is " . firstEmptyRow() . ".\n"; tryMove("$_[0]" . firstEmptyRow()); return; }
	    print "Too many rows ($totalRows) to move $_[0] to.\n"; return;
	  }
	  else { print "Forcing $_[0] -> $forceRow.\n"; tryMove("$_[0]$forceRow"); return; }
  }
  if ($_[0] =~ /^n[-\+]$/) { return; } # null move for debugging purposes
  if ($_[0] =~ /^uu$/) { undoToStart(); return; }
  if ($_[0] =~ /^ud$/) { undo(2); return; }
  if ($_[0] =~ /^ud1$/) { undo(3); return; }
  if ($_[0] =~ /^ul$/) { print "Last undo array info=====\nTC=" . join(",", @topCard) . "\nM=" . join(",", @undoLast) . "\n"; return; }
  if ($_[0] =~ /^sae$/) { $saveAtEnd = !$saveAtEnd; print "Save at end to undo-debug.txt now @toggles[$saveAtEnd].\n"; return; }
  if ($_[0] =~ /^sl$/) { open(B, ">>undo-debug.txt"); print B "Last undo array info=====\nTC=" . join(",", @topCard) . "\nM=" . join(",", @undoLast) . "\n"; close(B); return; }
  if ($_[0] =~ /^du$/) { $undoDebug = !$undoDebug; print "Undo debug now @toggles[$undoDebug].\n"; return; }
  if ($_[0] =~ /^1p/) { ones(1); printdeck(); return; }
  if (($_[0] =~ /^x[0-9]$/) || ($_[0] =~ /^[0-9]x$/))
  {	
    my $oldEmptyRows = emptyRows();
    if (emptyRows() < 2) { print "Not enough empty rows.\n"; return; }
    if ($_[0] !~ /[1-6]/) { print "Not a valid row.\n"; return; }
	my @rows = (0, 0);
	my $thisRow = $_[0]; $thisRow =~ s/x//g;
	if ($#{$stack[$thisRow]} == -1) { print "Nothing to spill.\n"; return; }
	if (($thisRow < 1) || ($thisRow > 6)) { print "Not a valid row to shuffle. Please choose 1-6.\n"; die; }
	for $emcheck (1..6)
	{
	  #print "$emcheck: $stack[$emcheck][0], @{$stack[$emcheck]}\n";
	  if (!$stack[$emcheck][0])
	  {
	    if (@rows[0]) { @rows[1] = $emcheck; last; }
	    else
	    {
	    @rows[0] = $emcheck;
	    }
	  }
	}
	
	placeUndoStart();
	$quickMove = 1;
	autoShuffleExt($thisRow, @rows[0], @rows[1]);
	$quickMove = 0;
	placeUndoEnd();
	printdeck();
	checkwin();
	return;
  }
  if ($_[0] =~ /^u$/) { undo(0); return; }
  if ($_[0] =~ /^u1$/) { undo(1); return; }
  if ($_[0] =~ /^o$/) { showOpts(); return; }
  if ($_[0] =~ /^debug/) { printdeckraw(); return; }
  if ($_[0] =~ /^df/) { drawSix(); printdeck(); checkwin(); return; }
  if ($_[0] =~ /[0-9]{4}/) { print "Commands can take up to three row numbers. Please eliminate one and try again.\n"; return; }
  if ($_[0] =~ /^sw0/) { printPoints(); return; }
  if ($_[0] =~ /^sw/) { if (($_[0] !~ /^sw[0-9]$/) || ($_[0] =~ /sw1/)) { print "You can only fix 2 through 9 to start. Typing sw0 gives odds of starting points,\n"; return; } $temp = $_[0]; $temp =~ s/^..//g; $startWith = $temp; if ($startWith > 7) { print "WARNING: this may take a bit of time to set up, and it may ruin some of the game's challenge, as well.\n"; } print "Now $temp points (consecutive cards or cards of the same suit) needed to start. sw0 prints the odds.\n"; return; }
  if ($_[0] =~ /^cb/) { $chainBreaks = !$chainBreaks; print "Showing bottom chain breaks @toggles[$chainBreaks].\n"; return; }
  if ($_[0] =~ /^1a/) { $autoOnes = !$autoOnes; print "AutoOnes on draw @toggles[$autoOnes].\n"; return; }
  if ($_[0] =~ /^1s/) { $autoOneSafe = !$autoOneSafe; print "AutoOneSafe on draw @toggles[$autoOneSafe].\n"; return; }
  if ($_[0] =~ /^1f/) { $autoOneFull = !$autoOneFull; print "AutoOneFull writeup @toggles[$autoOneFull].\n"; return; }
  if ($_[0] =~ /^mr/) { $showMaxRows = !$showMaxRows; print "Show Max Rows @toggles[$showMaxRows].\n"; return; }
  if ($_[0] =~ /^sb/) { $showBlockedMoves = !$showBlockedMoves; print "Show blocked moves @toggles[$showBlockedMoves].\n"; return; }
  if ($_[0] =~ /^1b/) { $beginOnes = !$beginOnes; print "BeginOnes on draw @toggles[$beginOnes].\n"; return; }
  if ($_[0] =~ /^e$/) { $emptyIgnore = !$emptyIgnore; print "Ignoring empty cell for one-number move @toggles[$emptyIgnore].\n"; return; }
  if ($_[0] =~ /^d$/) { if (($anySpecial) && ($drawsLeft)) { print "Push df to force--there are still potentially productive moves."; if ($mbGood) { print " $mbGood is one."; } print "\n"; return; } else { drawSix(); printdeck(); checkwin(); return; } }
  if ($_[0] =~ /^h/) { showhidden(); return; }
  if ($_[0] =~ /^ll/i) { if (!$lastSearchCmd) { print "Can't load last--we haven't loaded a game in the first place.\n"; } loadDeck($lastSearchCmd); return; }
  if ($_[0] =~ /^l=/i) { loadDeck($_[0]); return; }
  if ($_[0] =~ /^lf=/i) { loadDeck($_[0], 1); return; }
  if ($_[0] =~ /^c/) { $collapse = !$collapse; print "Card collapsing @toggles[$collapse].\n"; return; }
  if ($_[0] =~ /^s=/i) { saveDeck($_[0]); return; }
  if ($_[0] =~ /^t=/i) { loadDeck($_[0], "debug"); return; }
  if ($_[0] =~ /^tf/) { runEachTest(); return; }
  if ($_[0] =~ /^g$/) { procCmd($lastCommand); }
  if (($_[0] =~ /^ *$/) || ($_[0] =~ /^-/)) { printdeck(); checkwin(); return; }
  if ($_[0] =~ /^v/) { $vertical = !$vertical; print "Vertical view @toggles[$vertical].\n"; return; }
  if ($_[0] =~ /^af/) { if ($#force == -1) { print "Nothing in force array.\n"; } else { print "Force array: " . join(",", @force) . "\n"; } return; }
  if ($_[0] =~ /^ua/) { print "Top cards:"; for (1..6) { print " @topCard[$_](" . faceval(@topCard[$_]) . ")"; } print "\nMoves: " . join(",", @undoArray) . "\n"; return; }
  if ($_[0] =~ /^(f|f=)/) { forceArray($_[0]); return; }
  if ($_[0] =~ /^lu/) { if ($fixedDeckOpt) { peekAtCards(); } else { print "Must have fixed-deck card set.\n"; } return; }
  if ($_[0] =~ /^ra/) { if (($drawsLeft < 5) || ($hidCards < 16)) { print "Need to restart to toggle randomization.\n"; return; } $fixedDeckOpt = !$fixedDeckOpt; print "fixedDeck card-under @toggles[$fixedDeckOpt].\n"; return; }
  if ($_[0] =~ /^ry/) { if ($drawsLeft) { print "Forcing restart despite draws left.\n"; } doAnotherGame(); return; }
  if ($_[0] =~ /^r/) { if ($drawsLeft) { print "Use RY to clear the board with draws left.\n"; return; } doAnotherGame(); return; }
  if ($_[0] =~ /^%/) { stats(); return; }
  if ($_[0] =~ /[0-9]{4}/) { print "Too many numbers.\n"; return; }
  if (($_[0] =~ /^[az][0-9]{2}/) || ($_[0] =~ /^[0-9]{2}[az]/)) { $_[0] =~ s/[az]//g; placeUndoStart(); altUntil($_[0]); placeUndoEnd(); return; }
  if ($_[0] =~ /^[0-9]{2}[^0-9]/) { $_[0] = substr($_[0], 0, 2); tryMove($_[0]); tryMove(reverse($_[0])); return; }
  if ($_[0] =~ /^[!t~`][0-9]{3}/)
  {
    my $didAny;
	my $empties;
	my $localFrom, my $localTo, my $curMinToFlip;
    @x = split(//, $_[0]);
	printNoTest("3-waying stacks @x[1], @x[2] and @x[3].\n");
	$quickMove = 1;
	placeUndoStart();
    while (anyChainAvailable(@x[1], @x[2], @x[3]))
	{
	  $empties = 0;
	  for (1..3) { if ($#{$stack[$_]} == -1) { $empties++; } }
	  if ($empties == 2) { print "You made a full chain!\n"; last; }
	  $localFrom = 0; $localTo = 0;
	  $curMinToFlip = 0;
	  for $j (1..3) #this is so we pull the lowest card onto the lowest remaining. Not fully workable eg (other)-7-6-5 3-2-1-j-10-9 k-q-8-4 will lose
	  #we'd need a check for "lowest" and "safest" and "safest" trumps "lowest" but if there is nothing else, "lowest"
	  {
	    for $k (1..3)
		{
		  if (canChain(@x[$j], @x[$k]))
		  {
		    $foundChain = 1;
			if (($stack[@x[$k]][$#{$stack[@x[$k]]}] < $curMinToFlip) || ($curMinToFlip == 0)) { $localFrom = $j; $localTo = $k; }
		  }
		  else { }
		}
	  }
	  tryMove("@x[$localFrom]@x[$localTo]");
	  #if (canChain(@x[1], @x[2])) { $foundChain = 1; tryMove("@x[1]@x[2]"); next; }
	  #if (canChain(@x[1], @x[3])) { $foundChain = 1; tryMove("@x[1]@x[3]"); next; }
	  #if (canChain(@x[2], @x[3])) { $foundChain = 1; tryMove("@x[2]@x[3]"); next; }
	  #if (canChain(@x[2], @x[1])) { $foundChain = 1; tryMove("@x[2]@x[1]"); next; }
	  #if (canChain(@x[3], @x[1])) { $foundChain = 1; tryMove("@x[3]@x[1]"); next; }
	  #if (canChain(@x[3], @x[2])) { $foundChain = 1; tryMove("@x[3]@x[2]"); next; }
	  if ($foundChain)
	  {
	    $didAny = 1;
	  }
	}
	placeUndoEnd();
	$quickMove = 0;
	if (!$testing)
	{
	if ($didAny) { printdeck(); print "$didAny total shifts.\n"; checkwin(); } else { print "No shifts available.\n"; }
	}
	checkwin();
	return;
  }
  if (($_[0] =~ /^[0-9]{3}x/) || ($_[0] =~ /^x[0-9]{3}/))
  {
    $_[0] =~ s/x//g;
    @x = split(//, $_[0]);
	$b4 = $#undoArray;
	placeUndoStart();
	$quickMove = 1;
    autoShuffleExt(@x[0], @x[2], @x[1]);
	$quickMove = 0;
	placeUndoEnd();
	if ($b4 == $#undoArray) { if (!$moveBar) { print "No moves made. Please check the stacks you tried to shift.\n"; } } else { printdeck(); }
	return;
  }
  if (($_[0] =~ /^w[0-9]{3}/) || ($_[0] =~ /^[0-9]{3}w/))
  {
    my $oldEmptyRows = emptyRows();
    $_[0] =~ s/w//g;
    @x = split(//, $_[0]);
	$b4 = $#undoArray;
	my $wrongOrder = 0;
	if ($#{$stack[@x[2]]} == -1)
	{
	  $temp = @x[2]; @x[2] = @x[1]; @x[1] = $temp;
	  $wrongOrder = 1;
	}
	placeUndoStart();
	$quickMove = 1;
    autoShuffleExt(@x[0], @x[2], @x[1]);
    autoShuffleExt(@x[2], @x[0], @x[1]);
	$quickMove = 0;
	placeUndoEnd();
	if ($b4 == $#undoArray) { if (!$moveBar) { print "No moves made. Please check the stacks you tried to shift.\n"; } } else
	{
	  printdeck();
	  if ($wrongOrder)
	  {
	  print "NOTE: I switched the last two numbers. You can UNDO if it doesn't work for you.\n";
	  }
	  checkwin();
	}
	return;
  }
  if ($_[0] =~ /^[0-9]{3}/)
  { # detect 2 ways
    $b4 = $#undoArray;
    @x = split(//, $_[0]);
    if ((@x[0] == @x[1]) || (@x[0] == @x[2]) || (@x[2] == @x[1])) { print "Repeated number.\n"; return; }
	placeUndoStart();
	$quickMove = 1;
	tryMove("@x[0]@x[1]");
	tryMove("@x[0]@x[2]");
	tryMove("@x[1]@x[2]");
	$quickMove = 0;
	placeUndoEnd();
	if ($b4 == $#undoArray) { if (!$moveBar) { print "No moves made. Please check the stacks you tried to shift.\n"; } } else { printdeck(); }
	checkwin();
	return;
  }
  if ($_[0] =~ /^[0-9] *[0-9]/) { tryMove($_[0]); return; }
  if ($_[0] =~ /^q$/) { exit; }
  if ($_[0] =~ /^x[0-9]/) { print "You may have the wrong number of numbers.\n"; return; }
  if ($_[0] =~ /[0-9]x/) { print "You may have the wrong number of numbers.\n"; return; }
  if ($_[0] =~ /^[az][0-9]/) { print "You may have one too few numbers.\n"; return; }
  if ($_[0] =~ /^z/) { print "Time passes more slowly than if you actually played the game.\n"; return; }
  if ($_[0] =~ /^\?/) { usage(); return; }
#cheats

  print "Command ($_[0]) wasn't recognized. Push ? for usage.\n";
}

sub anyChainAvailable
{
  for $temp(0..2)
  {
    my $sz = $#{$stack[$_[$temp]]};
    if ($sz >= 12)
	{
	  $gotStraight = 1;
	  for $back (0..12) { if ($stack[$_[$temp]][$sz] + $back != $stack[$_[$temp]][$sz-$back]) { $gotStraight = 0; } }
	  if (($gotStraight == 1) && (!$testing)) { print "You got the whole suit straight on row $_[$temp].\n"; return 0; }
	}
	return  canChain(@x[1], @x[2], -1) || canChain(@x[1], @x[3], -1) || canChain(@x[2], @x[3], -1) || canChain(@x[2], @x[1], -1) || canChain(@x[3], @x[1], -1) || canChain(@x[3], @x[2], -1);
  }
}

sub doAnotherGame
{
  $moveBar = 1;
  $quickMove = 0;

  if (!$anyMovesYet) { print "No hand-typed moves yet, so stats aren't recorded.\n"; initGame(); printdeck(); return; }
  else
  {
  if ($#lastTen == 9) { shift(@lastTen); }
  push(@lastTen, $youWon);

  if ($youWon) { $youWon = 0; $wins++; $wstreak++; $lstreak=0; if ($wstreak > $lwstreak) { $lwstreak = $wstreak; } }
  else { $losses++; $wstreak = 0; $lstreak++; if ($lstreak > $llstreak) { $llstreak = $lstreak; } }
  }

  open(A, ">scores.txt");
  print A "$wins,$losses,$wstreak,$lstreak,$lwstreak,$llstreak\n";
  print A join (",", @lastTen); print A "\n";
  close(A);

  if ($saveAtEnd)
  {
  print "(Adding complete game to undo-debug.txt.)\n";
  open(B, ">>undo-debug.txt"); print B "s=$wins-$losses\n1,1\nTC=" . join(",", @topCard) . "\nM=" . join(",", @undoLast) . "\n";
  for (1..6) { print B join(",", @{$stack[$_]}) . "\n"; }
  close(B);
  }

initGame(); printdeck();
}

sub saveDeck
{
  chomp($_[0]);
  my $filename = "al-sav.txt";
  my $overwrite = 0;
  
  open(A, "$filename");
  open(B, ">albak.txt");
  $lastSearchCmd = $_[0];
  while ($a = <A>)
  {
    print B $a;
	if ($a =~ /^;/) { last; }
    if ($a =~ /^$_[0]$/)
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
  if ($_[1] =~ /debug/) { $filename = "al.txt"; printNoTest("DEBUG test\n"); } else { $filename="al-sav.txt"; }
  chomp($_[0]);
  my $search = $_[0]; $search =~ s/^[lt]/s/gi;
  open(A, "$filename");
  my $li = 0;
  my @temp;
  my @testArray;
  my @reconArray;
  my $loadFuzzy = 0;
  if ($_[1]) { $loadFuzzy = 1; }
  
  my $q = <A>; chomp($q); @opts = split(/,/, $q); if (@opts[0] > 1) { $startWith = @opts[0]; } $vertical = @opts[1]; $collapse = @opts[2]; $autoOnes = @opts[3]; $beginOnes = @opts[4]; $autoOneSafe = @opts[5]; $autoOneFull = @opts[6]; # read in default values
  my $hidRow = 0;
  
  while ($a = <A>)
  {
    $li++;
    chomp($a);
	$fixedDeckOpt = 0;
	my $rowsRead = 0;
	if ($a =~ /;$/) { last; }
    if (("$a" eq "$search") || ($loadFuzzy && ($a =~ /$search/i)))
	{
	printNoTest("Found $search in $filename, line $li.\n");
	$lastSearchCmd = $a;
	$a = <A>; chomp($a); $a = lc($a); @temp = split(/,/, $a); $vertical = @temp[0]; $collapse = @temp[1];
	#topCards line
    $hidCards = 0;
   $cardsInPlay = 0; $drawsLeft = 5;
    for (1..52) { $inStack{$_} = 1; }
	while ($rowsRead < 6)
	{
	  $a = <A>; chomp($a); $a = lc($a);
	  $b = $a; $b =~ s/^[a-z]+=//gi; #b = the data for a
	  #print "Trying $a\n";
	  if ($a =~ /^tm=/)
	  {
	    $testing = 1;
	    @testArray=split(/,/, $b);
		$anyMovesYet = 1;
		next;
	  }
	  if ($a =~ /^fd=/i)
	  {
	    $fixedDeckOpt = 1;
	    @fixedDeck = split(/,/, $b);
		next;
	  }
	  if ($a =~ /^tc=/i)
	  {
		@topCard = split(/,/, $b);
		next;
	  }
	  if ($a =~ /^m=/i)
	  {
		@undoArray = split(/,/, $b);
		$anyMovesYet = 1;
		next;
	  }
	  if ($a =~ /^hc=/)
	  {
	    $hidRow++;
		@{backupCardUnder[$hidRow]} = split(/,/, $b);
		@{cardUnder[$hidRow]} = split(/,/, $b);
		next;
	  }
	  if (($a !~ /m=/i) && ($a =~ /[a-z]/) && ($a =~ /=/)) { print "Unknown command in save-file. Skipping $a.\n"; next; }
	  $rowsRead++;
	  @{$stack[$rowsRead]} = split(/,/, $a);
		#print "$rowsRead: @{$stack[$rowsRead]}\n";
	    for (0..$#{$stack[$rowsRead]})
		{
		if ($stack[$rowsRead][$_] =~ /[cdhs]$/i) { $stack[$rowsRead][$_] = revCard($stack[$rowsRead][$_]); }
		}
		#print "$rowsRead: @{$stack[$rowsRead]}\n";
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
	if ($#testArray > -1)
	{
      @undoArray = ();
	  $testing = 1;
	  $quietMove = 1;
	  my $errs = 0;
	  my $expVal = 0;
	  for (0..$#testArray)
	  {
	    if (@testArray[$_] =~ /=/)
		{
		  @q = split(/=/, @testArray[$_]);
		  @r = split(/-/, @q[0]);
		  $expVal = $stack[@r[0]][@r[1]];
		  printDebug("$expVal at @r[0] @r[1]\n");
		  if ($expVal >= 0)
		  {
		    if (@q[1] != $expVal) { $errs++; print "$search: @r[0],@r[1] should be @q[1] but is $expVal.\n"; }
			else
			{
			  printDebug("$search: @r[0],@r[1] should be $expVal and is.\n");
			}
		  }
		  else
		  {
		    $expVal = 0 - $expVal;
		    if ($q[1] == $expVal) { $errs++; print "$search: @r[0],@r[1] should not be $expVal but is.\n"; }
			else
			{
			  printDebug("$search: @r[0],@r[1] should not be $expVal and isn't.\n");
			}
		  }
    } else { procCmd(@testArray[$_]); }
		}
	  $quietMove = 0;
	  $testing = 0;
		  if ($errs == 0) { $totalTestPass++; print "Test $search succeeded.\n"; } else { print "Test $search had $errs errors.\n"; $totalTestFail++; if ($inMassTest) { push(@fail, $search); } }
		  close(A);
		  return;
	}
	else
	{
	}
		  if ($loadFuzzy)
		  {
		    while ($a = <A>)
			{
			  if ($a =~ /^s=/)
			  {
			    $a =~ s/^s=//g;
			    if ($a =~ /$search/) { print "Note: duplicate save game $a found too.\n"; }
			  }
			}
		  }
	printdeck();
	close(A);
	return;
	}
  }
  
  print "No $search found in $filename.\n";
}

sub runEachTest
{
  my @tests = ();
  open(A, "al.txt");
  while ($a = <A>) { if ($a =~ /^s=/) { $b = $a; chomp($b); $b =~ s/^.=//g; push(@tests, $b); } if ($a =~ /;$/) { last; } }
  close(A);
  
  @fail = ();
  
  $totalTestPass = 0;
  $totalTestFail = 0;
  
  $inMassTest = 1;
  for $t (@tests)
  {
    loadDeck($t, "debug");
  }
  $inMassTest = 0;
  print "Tests passed = $totalTestPass, test failed = $totalTestFail.\n";
  print "List of failures = @fail\n";
}

sub revCard
{
  my $retVal = 0;
  my $lc0 = $_[0];

  $last = $lc0; $last =~ s/.*(.)/$1/g;
  $retVal = $sre{$last};
	
  $lc0 =~ s/.$//g;
  if ($rev{$lc0}) { $retVal += $rev{$lc0}; } else { $retVal += $lc0; }

  return $retVal;
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
    my $card = $_[0]; $card =~ s/^(f|f=)//g; $card =~ s/\(.*//g;
	
	if ((!$hidden) && (!$undo) && ($cardsInPlay == 52)) { print "Too many cards out.\n"; return; }
	
	if ($card eq "0") { push(@force, $card); print "Forcing null, which is usually just for testing purposes.\n"; return; }
	if ($card =~ /[cdhs]/i) { print "Changing suit of $card to number.\n"; $card = revCard($card); }
	if ($card =~ /[^0-9]/) { print "You need to put in a numerical or card value. $card can't be evaluated.\n"; return; }
	if (($card <= 52) && ($card >= 1))
	{
	if (!$inStack{$card}) { print "$card (" . faceval($card) . ") already out on the board or in the force queue.\n"; return; }
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

my $deckTry = 0;

my $thisStartMoves = 0;

$printedThisTurn = 0;

$anyMovesYet = 0;

@force = ();

do
{ 

$thisStartMoves = 0;

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

drawSix(-1);

my @suitcard = (0,0,0,0);

for (1..6)
{
  @suitcard[suit(@topCard[$_])]++;  
}

for (0..3)
{
  if (@suitcard[$_] > 1) { $thisStartMoves += (@suitcard[$_] - 1); }
}

for $x (1..6)
{
  for $y(1..6)
  {
    if (@topCard[$x] - @topCard[$y] == 1) { $thisStartMoves++; }
  }
}

$deckTry++;
#print "$deckTry: $thisStartMoves vs $startWith, @topCard, suits @suitcard\n";

} while ((!$undo) && ($thisStartMoves < $startWith));

deckFix();

if ($startWith > 2) { print "Needed $deckTry tries, starting with $thisStartMoves 'points'.\n"; }

if (($autoOnes) || ($beginOnes) || ($autoOneSafe)) { $moveBar = 0; ones(0); $anyMovesYet = 0; }

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
  if ((!$undo) && ($drawsLeft < 6)) { push(@undoArray, "f$thiscard(" . faceval($thiscard) . ")" ); }
  }
  if ($drawsLeft == 6) { @topCard[$_] = $stack[$_][$#{$stack[$_]}]; }
}
  #print "Top cards: @topCard\n";
if ((!$undo) && ($drawsLeft < 6)) { push(@undoArray, "df"); }
$drawsLeft--;
$cardsInPlay += 6;
if (($autoOnes) && ($_[0] != -1))
{
  ones(0);
}
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
  if ($_[0] == -3) { return "**"; }
  my $x = $_[0] - 1;
  my $suit = @sui[$x/13];
  return "$vals[$x%13]$suit";
}

sub printdeckforce
{
  my $testold = $testing;
  my $undoold = $undo;
  my $qmold = $quickMove;
  $undo = $testing = $quickMove = 0;
  print "============start force print deck\n";
  printdeck();
  print "============end force print deck\n";
  $quickMove = $qmold;
  $undo = $undoold;
  $testing = $testold;
}

sub printdeck #-1 means don't print the ones
{
  if ($testing) { return; }
  if ($undo) { return; }
  if ($quickMove) { return; }
  if (($autoOneSafe) && ($_[0] != -1)) { ones(0); } # there has to be a better way to do this
  if ($printedThisTurn) { print "Warning tried to print this turn.\n"; return; }
  $printedThisTurn = 1;
  if ($vertical)
  { printdeckvertical(); }
  else
  { printdeckhorizontal(); }
}

sub printdeckhorizontal
{
  my $anyJumps = 0;
  for $d (1..6) { $anyJumps += jumpsFromBottom($d); }
  my @rowLength = ();

  for $d (1..6)
  {
    $thisLine = "$d:";
	if (($anyJumps > 0) && ($chainBreaks))
	{
	  my $temp = jumpsFromBottom($d);
	  if ($temp) { $thisLine = "($temp) $thisLine"; } else { $thisLine = "    $thisLine"; }
	}
    for $q (0..$#{$stack[$d]})
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
	if ($showMaxRows) { my $tlt = $thisLine; $tlt =~ s/^[0-9]: //g; @tmpArray = split(/[=\-: ]/, $tlt); @rowLength[$d] = $#tmpArray + 1; }
	if ($thisLine =~ [CDHS]) { @rowLength[$_]++; }
	print "$thisLine\n";
  }
  if ($showMaxRows)
  {
    my $maxRows = 0;
	for (1..6) { if (@rowLength[$_] > $maxRows) { $maxRows = @rowLength[$_]; } }
	print "($maxRows max row length) ";
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
  my $maxRows = 0;
  if ($chainBreaks)
  {
  for $row (1..6)
  {
    if ($temp = jumpsFromBottom($row)) { $myString .= "  ($temp)"; } else { $myString .= "     "; }
    @lookAhead[$row] = 0;
  }
  if ($myString =~ /[0-9]/) { print "$myString\n"; }
  }
  for $row (1..6)
  {
    print "   ";
	if ($stack[$row][0]) { print " "; } else { print "!"; }; print "$row";
  }
  print "\n";
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
  if ($foundCard) { print "$thisLine\n"; $maxRows++; }
  } while ($foundCard);
  if ($showMaxRows)
  {
    print "($maxRows max rows) ";
  }
  showLegalsAndStats();
}

sub showLegalsAndStats
{
  if (($undo) || ($quickMove)) { return; }
  my @idx;
  my @blank = (0,0,0,0,0,0);
  my @circulars = (0,0,0,0,0,0);
  my $canMakeEmpty = 0;
  $mbGood = "";
  
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
		if (($stack[$from][$thisEl] == $stack[$to][@idx[$to]] - 1) && ($stack[$from][$thisEl] % 13)) { print "+"; $anySpecial = 1; $mbGood = "$from$to"; }
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
  my $brkPoint = 24 * $drawsLeft;
  for my $breakRow (1..6)
  {
    #we deserve credit for an empty row, but how much?
    if ($stack[$breakRow][0] > 0) { $brkPoint++;  }
    for (0..$#{$stack[$breakRow]} - 1)
	{
	  if ($stack[$breakRow][$_] != -1)
	  {
	    if (($stack[$breakRow][$_] - $stack[$breakRow][$_+1] != 1) || (suit($stack[$breakRow][$_+1]) != suit($stack[$breakRow][$_+1])))
		{
		  $breaks++;
		  if (suit($stack[$breakRow][$_]) == suit($stack[$breakRow][$_+1]))
		  {
		    if ($stack[$breakRow][$_] < $stack[$breakRow][$_+1]) { $brkPoint += 2; } else { $brkPoint += 1; }
		  }
		  else { $brkPoint += 3; }
		}
	  }
	  else { $brkPoint += 4; }
	}
  }
  if ($chains != 48) # that means a win, no need to print stats
  {
  print "$cardsInPlay cards in play, $visible/$hidCards visible/hidden, $drawsLeft draws left, $chains chains, $order in order, $breaks breaks, $brkPoint break points.\n";
  }
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

sub barMove #this is necessary in some cases where we need to run two moves with one user command
{
  $moveBar = 1;
  if (!$errorPrintedYet) { $errorPrintedYet = 1; print $_[0]; }
}

sub tryMove
{
  my @q = split(/ */, $_[0]);
  my $from = @q[0];
  my $to = @q[1];
  
  #print "$_[0] becomes $from $to, $moveBar moves barred\n";
  if ($moveBar == 1) { if ($showBlockedMoves) { barMove("$from-$to blocked, as previous move failed.\n"); } else { $blockedMoves++; } return; }
  
  if (($from > 6) || ($from < 1) || ($to > 6) || ($to < 1)) { barMove("$from-$to is not valid. Rows range from 1 to 6.\n"); return; }
  
  if ($from==$to) { barMove("Oops, tried to switch a row with itself.\n"); return; }
  
  if (!$stack[$from][0]) { barMove("Empty row/column.\n"); return; } # note: this needs a better error message.

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
	  if (!$quickMove)
	  {
	    barMove("$from-$to: Card needs to be placed on empty stack or a same-suit card of greater value (kings high).\n");
	  }
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
  if (!$undo) { push(@undoArray, "$from$to"); if ($_[1] != -1) { $anyMovesYet = 1; } } #-1 means that we are in the "ones" subroutine so it is not a player-move

  printdeck();
  checkwin();
}

sub altUntil
{
  $altmoves = 0;
  my @cmds = split(//, $_[0]);
  my $from = @cmds[0];
  my $to = @cmds[1];
  my $totalMoves = 0;
  if (($from < 1) || ($from > 6) || ($to < 1) || ($to > 6)) { print "From/to must be between 1 and 6.\n"; }
  #print "$from$to trying\n";
  if (!canChain($from,$to) && !canChain($to, $from)) #do we need this
  {
    #if (canChain($to, $from)) { $temp = $from; $from = $to; $to = $temp; }
	print "These two rows aren't switchable.\n"; return;
  }
  $quickMove = 1;
  #print "$to$from trying\n";
  while (canChain($from, $to, $totalMoves) || canChain($to, $from, $totalMoves))
  {
    if (canChain($from, $to))
	{
    tryMove("$from$to"); #print "$to$from trying\n";
	}
	else
	{
    tryMove("$to$from"); #print "$to$from trying\n";
	}
	if ($quickMove == 0) { return; } # this means you won
    if ($moveBar == 1) { print "Move was blocked. This should never happen.\n"; last; }
	#$temp = $from; $from = $to; $to = $temp;
	$totalMoves++;
  }
  $quickMove = 0;
  printdeck();
  print "Made $totalMoves moves.\n";
  checkwin();
}

sub canChain
{
  if ($moveBar) { return 0; }
  if ($_[0] == $_[1]) { return 0; }
  my $toCard = $stack[$_[1]][$#{$stack[$_[1]]}];
  if ($toCard % 13 == 1) { return 0; } # if it is an ace, there's no way we can chain
  my $fromLoc = $#{$stack[$_[0]]};
  my $toLoc = $#{$stack[$_[1]]};
  if ($fromLoc == -1) { return 0; } # can't move from empty row
  my $fromCard = $stack[$_[0]][$fromLoc];
  if (suit($toCard) != suit($fromCard)) { if ($#{$stack[$_[1]]} != -1) { return 0; } } #can't move onto a different suit, period. But we can move onto an empty card.
  if (($toCard < $fromCard) && ($toCard)) { return 0; } # and of course smaller must move onto bigger
  #print "CanChain: on to $toCard From: $stack[$_[0]][$fromLoc-1] $stack[$_[0]][$fromLoc]\n";
  if ($fromLoc)
  {
    if (suit($stack[$_[0]][$fromLoc-1]) != suit($stack[$_[0]][$fromLoc])) { return 1; }
	if ($stack[$_[0]][$fromLoc-1] == -1) { return 1; }
  } # we can/should move if suits are different in the "from" row, or we can reveal a blank
  while (($fromLoc > 0) && ($stack[$_[0]][$fromLoc-1] -  $stack[$_[0]][$fromLoc] == 1)) # this detects how far back we can go
  {
    $fromLoc--;
  }
  if ($toLoc == -1) { if (suit($stack[$_[0]][$fromLoc-1]) != suit($stack[$_[0]][$fromLoc])) { if ($_[2] > 0) { print "With only 1 empty row, revealing new suit must be done manually e.g. $_[0]$_[1].\n"; } return 0; } } # 8H-7C-6C won't jump to 
  if ($fromLoc == $#{$stack[$_[0]]} - 12) { if ($_[2] >= 0) { print "Suit complete after twiddling. "; if ($fromLoc > 0) { print "Player must force move off."; } print "\n"; } return 0; } # KH-AH should not be moved. If it's at the top, useless. If not, the player should make that choice.
  if ($toCard - $stack[$_[0]][$fromLoc] == 1) # automatically move if we can create a bigger chain
  {
    return 1;
  }
  if (($fromLoc == 0) && ($fromCard < $toCard)) { return 1; } # 5h=ah will go on to x-kh=a8
  if (($fromLoc > 0) && ($stack[$_[0]][$fromLoc-1] < $stack[$_[0]][$fromLoc])) # 10H-9H-QH-JH case
  {
    #print "Ping\n";
    if (($toCard > $fromCard) || ($#{$stack[$_[1]]} == -1)) { return 1; } # higher card or empty allows for 2 moves in a row
    #if ($#{$stack[$_[1]]} == -1) { return 1; } 
  }
  return 0;
}

sub cleanStuffUp
{
  $moveBar = 0;
  my $s0 = botSuit($_[0]);
  my $s1 = botSuit($_[1]);
  if ($s0 != $s1) { return; }
  if (topCardInSuit($_[0]) > topCardInSuit($_[1]))
  {
    autoShuffle($_[0], $_[1], $_[2]);
    autoShuffle($_[1], $_[0], $_[2]);
  }
  else
  {
    autoShuffle($_[1], $_[0], $_[2]);
    autoShuffle($_[0], $_[1], $_[2]);
  }
}

sub topCardInSuit
{
  my $temp = $#{$stack[$_[0]]};
  while (($temp > 0) && (suit($stack[$_[0]][$temp]) == suit($stack[$_[0]][$temp]-1)) && ($stack[$_[0]][$temp-1] > $stack[$_[0]][$temp])) { $temp--; }
  return $stack[$_[0]][$temp];
}

sub botSuit
{
  return suit(lowCard($_[0]));
}

sub lowCard
{
  return $stack[$_[0]][$#{$stack[$_[0]]}]
}

sub firstEmptyRow
{
  my $retVal = 0;
  for my $rv (1..6)
  {
    if (!$stack[$rv][0]) { return $rv; }
  }
  return 0;
}

sub emptyRows
{
  my $retVal = 0;
  for (1..6) { if (!$stack[$_][0]) { $retVal++; } }
  return $retVal;
}

sub isEmpty
{
  if ($stack[$_[0]][0]) { return 0; } else { return 1; }
}

sub autoShuffleExt #autoshuffle 0 to 1 via 2, but check if there's a 3rd open if stuff is left on 2
{
  autoShuffle($_[0], $_[1], $_[2]);
  if (isEmpty($_[2]))
  {
    return;
  }
  if (!emptyRows()) { return; }
  #printdeckforce();
  my $fer = firstEmptyRow();
  $moveBar = 0;
  #print "Trying $_[2] to $_[1] via $fer.\n";
  autoShuffle($_[2], $_[1], $fer);
}

sub autoShuffle # autoshuffle 0 to 1 via 2
{
  if ($moveBar) { return; }
  my $count = $_[3];
  if (!$_[3])
  {
    $count = 1;
    my $x = $#{$stack[$_[0]]};
    my $y = $#{$stack[$_[1]]};
	while ($x > 0)
	{
	  #print "$stack[$_[0]][$x-1] vs $stack[$_[1]][$y]\n";
	  if (($y > -1) && ($stack[$_[0]][$x-1] > $stack[$_[1]][$y])) { last; } # e.g. KH-JH to QH only tries JH
	  if (suit($stack[$_[0]][$x]) != suit($stack[$_[0]][$x-1])) { last; }
	  if ($stack[$_[0]][$x] > $stack[$_[0]][$x-1]) { last; }
	  if (($stack[$_[0]][$x-1]) - ($stack[$_[0]][$x]) != 1) { $count++; }
	  #print "Moving from $stack[$_[0]][$x] to $stack[$_[0]][$x-1]\n";
	  $x--;
	}
	#print "Total alts = $count\n";
  }
  else { $count = $_[3]; }
  #die ($count);
  
  #print "From $_[0] to $_[1] to $_[2], $count.\n";
  if ($count < 0) { print "BUG.\n"; return; }
  if (($count == 1) || ($count == 0))
  {
    #print "Trying (1 card) $_[0] to $_[1]\n";
    if (!$moveBar) { tryMove("$_[0]$_[1]"); } return;
  }

  #print "$_[0] to $_[1], then $_[0] to $_[2], then $_[1] to $_[2].\n";  
  autoShuffle($_[0], $_[2], $_[1], $count - 1);
  if (!$moveBar)
  {
    tryMove("$_[0]$_[1]");
    autoShuffle($_[2], $_[1], $_[0], $count - 1);
  }
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
  @undoArray = ();
  printdeck();
}

sub placeUndoStart
{
  push(@undoArray, "n+");
}

sub placeUndoEnd
{
  if (@undoArray[$#undoArray] eq "n+") { pop(@undoArray); } else { push(@undoArray, "n-"); }
}

sub undo # 1 = undo just one move (u1) , 2 = undo to last cards-out (ud) 3 = undo last 6-card draw (ud1)
{
  $undo = 1;
  if ($undoDebug)
  {
    print "Writing to debug...\n";
    open(B, ">>undo-debug.txt");
	print B "========\n";
	print B "TC=" . join(",", @topCard) . "\n";
	print B "M=" . join (",", @undoArray) . "\n";
	for (1..6) { print B join(",", @{$stack[$_]}); print B "\n"; }
	close(B);
	if (-s "undo-debug.txt" > 100000) { print "WARNING trim undodebug file.\n"; }
  }
  #if ($#undoArray == -1) { print "Nothing to undo.\n"; return;}
  @undoLast = @undoArray;
  my $oldCardsInPlay = $cardsInPlay;
  @force = ();
  reinitBoard();
  #print "$cardsInPlay cards in play.\n";
  $x = $#undoArray;
  $temp = @undoArray[$x];
  #print "$x elts left\n";
  if (($_[0] == 2) || ($_[0] ==3)) { if ($oldCardsInPlay == 22) { print "Note--there were no draws, so you should use uu instead.\n"; $undo = 0; return; } }
  if ($x >= 0)
  {
	while (($x > 0) && ($temp eq "n+")) { pop(@undoArray); $x--; $temp = @undoArray[$x]; }
	if (($_[0] != 3) || ($temp ne "df")) # special case: Don't pop if we are near a DF anyway
	{
    $temp = pop(@undoArray);
	$x--;
	printDebug("Popped $temp\n");
	}
	if ($_[0] == 1)
	{
	while ((@undoArray[$x] =~ /^(f|n-|n\+)/) && ($x >= 0))
	{
	  $x--; $temp = pop(@undoArray);
	}
	}
	elsif (($_[0] ==3) && (@undoArray[$x] eq "df"))
	{
	  print "Already at a draw, so only going back one move.\n";
	  while ((@undoArray[$x] =~ /^[fd]/) && ($x > 0)) { $x--; pop(@undoArray); }
	}
	elsif (($_[0] == 2) || ($_[0] == 3))
	{
	  #print "1=============\n@undoArray\n";
	while ((@undoArray[$x] ne "df") && ($x > 0)) { $x--; pop(@undoArray); }
	  #print "2=============\n@undoArray\n";
	if (($_[0] == 3) && ($x > 0))  # encountered df.
	{
	  $temp = 0;
	  pop(@undoArray); $x = $#undoArray;
	  while ((@undoArray[$x] =~ /^f/) && ($x > 0))
	  {
	    $x--; pop(@undoArray); $temp++;
	  }
	  if ($temp != 6) { print "WARNING: popped wrong number of forces ($temp) in undo array. Push ul for full details.\n"; }
	}
	}
	elsif (($temp eq "n-"))
	{
	while ((@undoArray[$x] ne "n+") && ($x >= 0)) { $x--; pop(@undoArray); }
	}
	else
	{
	while ((@undoArray[$x] =~ /^(f|n\+)/) && ($x >= 0))
	{
	  $x--;
	  $temp = pop(@undoArray);
	  #print "extra-popped 1 $temp\n";
	}
	}
	while ((@undoArray[$x] =~ /^n\+/) && ($x >= 0)) # this is to get rid of stray N+
	{
	  $x--;
	  $temp = pop(@undoArray);
	  #print "extra-popped 2 $temp\n";
	}
  }
  #print "@undoArray\n";
  $undo = 1;
  for (0..$#undoArray)
  {
	#$undo = 0;
    #print "@undoArray[$_]\n";
    procCmd(@undoArray[$_]);
  }
  $undo = 0;
  printdeck(-1);
}

sub showhidden
{
  my @out = (0, 0, 0, 0);
  my $outs = "";
  
  if ($hidCards == 0) { print "Nothing hidden left.\n"; }
  my $lastSuit = -1;
  print "Still off the board:";
  for $j (sort { $a <=> $b } keys %inStack)
  {
    @out[suit($j)]++;
    if ($lastSuit != suit($j)) { if (@out[$lastSuit] > 0) { print " (@out[$lastSuit])"; } $lastSuit = suit($j); print "\n" . faceval($j); } else { print " " . faceval($j); }
  }
  if (@out[$lastSuit]) { print " (@out[$lastSuit])"; }
  print "\nTotal unrevealed: " . (keys %inStack) . "\n";
  for (0..3) { if (!@out[$_]) { $outs .= "@sui[$_] OUT. "; } }
  if ($outs) { print "$outs\n"; }
}

sub ones # 0 means that you don't print the error message, 1 means that you do
{
  if ($undo) { return 0; } # otherwise this is a big problem if we want to undo something automatic.
  my $onesMove = 0;
  my $totMove = 0;
  my $localAnyMove = $anyMovesYet;
  
  $moveBar = 0;
  
  my $quickStr = "";
  
  OUTER: do
  {
  $anyYet = 0;
  for (1..6)
  {
  my $temp = $#{$stack[$_]};
  if ($temp == -1) { @thisTopCard[$_] = -3; next; }
  while ($temp > 0)
  {
  if (($stack[$_][$temp] == $stack[$_][$temp-1]-1) && (suit($stack[$_][$temp-1]) == suit($stack[$_][$temp])))
  { $temp--; }
  else
  { last; }
  }
  @thisTopCard[$_] = $stack[$_][$temp];
  @thisBotCard[$_] = $stack[$_][$#{$stack[$_]}];
  }
  
  for $j (1..6)
  {
    for $i (1..6)
	{
	  if (canFlipQuick(@thisBotCard[$j], @thisTopCard[$j], @thisBotCard[$i]))
	  {
	    if (!$anyYet)
		{
		  $tempStr = "";
		  $quickMove = 1;
		  $tempStr .= "$j->$i=" . faceval(@thisBotCard[$j]);
		  if ($thisTopCard[$j] != $thisBotCard[$j]) { $tempStr .= "/" . faceval(@thisTopCard[$j]); }
		  $tempStr .= " -> " . faceval(@thisBotCard[$i]);
		  #if ((@thisBotCard[$j] == 27) && (@thisBotCard[$i] == 28)) { $undo = 0; $quickMove = 0; $autoOneSafe = 0; printdeck(); die; }
		  tryMove("$j$i", -1);
		  if (!$quickStr) { $quickStr .= "AUTO: $tempStr"; } else { if ($totMove % 5 == 0) { $quickStr .= "\n      "; } else { $quickStr .= ", "; } $quickStr .= "$tempStr"; }
		  $quickMove = 0; $anyYet = 1; $totMove++; #print "Move $totMove = $j to $i\n";
		}
	  }
	}
  }
  }
  while ($anyYet);
  if (($quickStr) && ($autoOneFull)) { print "$quickStr\n"; }
  if (!$totMove) { if ($_[0] == 1) { print "No moves found.\n"; } } else { print "$totMove auto-move(s) made.\n"; }
  
  #checkwin(-1);
}

sub canFlipQuick #can card 1 be moved onto card 3? card 2 is the top one
{
  #print "Trying $_[0]:$_[1] to $_[2], any moves = $anyMovesYet\n";
  if (suit($_[0]) != suit($_[2])) { return 0; }
  if ($_[2] - $_[1] != 1) { return 0; }
  if (!$anyMovesYet) { return 1; }
  #if (($_[0] % 13 == 1) && $autoOneSafe ) { return 1; }
  if ($autoOneSafe) #this is extended safe: 2h to 3h if ah is not on the board
  {
    my $temp = ($_[0] / 13) * 13 + 1;
	while ($temp < $_[0])
	{
	#print "$temp: $inStack{$temp}\n";
	if (!$inStack{$temp}) { return 0; }
	$temp++;
	}
	return 1;
  }
  if ($autoOnes) { return 1; }
  return 0;
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
  if ((!$undo) && (!$quickMove) && (!$inMassTest))
  {
  if ($suitsDone == 4) { if ($_[0] == -1) { printdeck(-1); } print "You win! Push enter to restart, or q to exit."; $x = <STDIN>; $youWon = 1; if ($x =~ /^q/i) { exit; } @lastWonArray = @undoArray; @lastFix = @fixedDeck; doAnotherGame(); return; }
  if ($suitsDone) { print "$suitsDone suit" . plur($suitsDone) . " completed.\n"; }
  }
}

sub plur
{
  if ($_[0] eq 1) { return ""; }
  return "s";
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
  my $sum = 0;
  my @wl = ("l", "w");
 print "$wins wins $losses losses\n";
 if ($wstreak) { print "Current win streak = $wstreak wins\n"; }
 elsif ($lstreak) { print "Current loss streak = $lstreak losses\n"; }
 print "Longest streaks $lwstreak wins $llstreak losses\n";
 print "Last ten games:";
 for (0..$#lastTen) { $sum += @lastTen[$_]; print " @wl[@lastTen[$_]]"; } print ", $sum wins.\n";
 printf("Win percentage = %d.%02d\n", ((100*$wins)/($wins+$losses)), ((10000*$wins)/($wins+$losses)) % 100);
}

sub saveDefault
{
  my $filename = "al-sav.txt";
  open(A, "$filename");
  <A>;
  open(B, ">albak.txt");
  print B "$startWith,$vertical,$collapse,$autoOnes,$beginOnes,$autoOneSafe,$showMaxRows,$saveAtEnd\n";
  while ($a = <A>) { print B $a; }
  close(A);
  close(B);
  `copy albak.txt al.txt`;
}

sub initGlobal
{
  $vertical = $collapse = 0;
  $startWith = 2;
  $youWon = 0;
  @sui = ("C", "D", "H", "S");
  @vals = ("A", 2, 3, 4, 5, 6, 7, 8, 9, 10, "J", "Q", "K");
  
  $sre{"c"} = 0;
  $sre{"d"} = 13;
  $sre{"h"} = 26;
  $sre{"s"} = 39;
  $rev{"a"} = 1;
  $rev{"j"} = 11;
  $rev{"q"} = 12;
  $rev{"k"} = 13;

  open(A, "al-sav.txt");
  my $a = <A>; chomp($a); my @opts = split(/,/, $a); $startWith = @opts[0]; $vertical = @opts[1]; $collapse = @opts[2]; $autoOnes = @opts[3]; $beginOnes = @opts[4]; $autoOneSafe = @opts[5]; $autoOneFull = @opts[6]; $showMaxRows = @opts[7]; $saveAtEnd = @opts[8]; close(A); # note showmaxrows and saveatend are global as of now
  
  #print "$a = first line\n";
}

sub showOpts
{
  print "Vertical view (v) @toggles[$vertical].\n";
  print "Collapsing (c) @toggles[$collapse].\n";
  print "Fixed deck (ra) @toggles[$fixedDeckOpt].\n";
  print "Ignore Empty on Force (e) @toggles[$emptyIgnore].\n";
  print "Show Chain Breaks (cb) @toggles[$chainBreaks].\n";
  print "Auto-Ones on Draw (1a) @toggles[$autoOnes].\n";
  print "Begin with shuffling one-aparts (1b) @toggles[$beginOnes].\n";
  print "Auto-Ones Safe (1s) @toggles[$autoOnesSafe].\n";
  print "Auto-Ones Full Desc (1f) @toggles[$autoOneFull].\n";
  print "Show blocked moves (sb) @toggles[$showBlockedMoves].\n";
  print "Show max rows (mr) @toggles[$showMaxRows].\n";
  print "Save undos at end (sae) @toggles[$saveAtEnd].\n";
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
$stats = <A>; chomp($stats);
@lastTen = split(/,/, $stats);
close(A);
}
}

sub printLastWon
{
  print "#printout of last win: undo to get the right alignment";
  print "s=last won\n1,1\n";
  print "TC=" . join(",", @lastFix) . "\n";
  print "M=" . join(",", @lastWonArray) . "\n";
  print "\n\n\n\n\n\n";
}

sub printNoTest
{
  if (!$inMassTest) { print $_[0]; }
}

sub printDebug
{
  if ($debug) { print "$_[0]"; }
}

sub printPoints
{
print<<EOT;
1 point for cards of the same suit or consecutive cards.
You must have at least 2 pairs of cards of the same suit (or 3 of one suit) since there are 6 cards and 4 suits. So you have 2 points automatically.
10 is the maximum since you could have all of the same suit in a row e.g. 6H through AH.
It is not allowed since 9 can take a few seconds, so 10 may take a minute or more.
2: 5867004/20358520=28.8184% or 1 in 3.4700
3: 7546400/20358520=37.0675% or 1 in 2.6978
4: 4832234/20358520=23.7357% or 1 in 4.2131
5: 1638076/20358520=8.0461% or 1 in 12.4283
6: 401260/20358520=1.9710% or 1 in 50.7365
7: 67144/20358520=0.3298% or 1 in 303.2068
8: 5810/20358520=0.0285% or 1 in 3504.0482
9: 560/20358520=0.0028% or 1 in 36354.5000
10: 32/20358520=0.0002% or 1 in 636203.7500
pts.pl runs this test.
EOT
}

sub usage
{
print<<EOT;
[1-6] moves that row, if there is exactly one suitable destination
[1-6][1-6] moves stack a to stack b
[1-6][1-6][1-6] moves from a to b, a to c, b to c.
a[1-6][1-6] moves stack a to b and back. If you end with 8h-2h-kh-qh, the kh-qh will go to the empty square. Use ud1 to undo this.
[1-6][1-6][1-6]x moves column a to column c via column b, extended. It may cause a blockage.
[1-6][1-6][1-6]w moves a to c via b, then c to a via b. It is useful for, say, kh-jh-9h-7h and qh.
[~!t][1-6][1-6][1-6] triages 3 columns with the same suit. It may cause a blockage.
v toggles vertical view (default is horizontal)
c toggles collapsed view (8h-7h-6h vs 8h=6h)
cb shows chain breaks e.g. KH-JH-9H-7H has 3
e toggles empty-ignore on eg if 2H can go to an empty cell or 6H, with it on, 1-move goes to 6H.
q/x quits.
r restarts, ry forces if draws are left.
(blank) or - prints the screen.
d draws 6 cards (you get 5 of these), df forces if "good" moves are left.
s=saves deck name
h=shows hidden/left cards
l=loads deck name
lf=loads deck name (fuzzy)
t=loads test
tf=full test
mr = show max rows
sd=save default
af=show force array
lw=show last won array
sw=start with a minimum # of points (x-1 points for x-suits where x >=2, 1 point for adjacent cards, can start with 2-6)
sw0=shows odds of points to start with
sb=show blocked moves toggle
u=undo
u1=undo one move
ud=undo to before last 6-card draw
ud1=undo to last 6-card draw
ul=last undo array (best used for debugging if undo goes wrong. Sorry, it's not perfect yet.)
sl=save last undo array (to undo-debug.txt)
du=hidden undo debug (print undos to undo-debug.txt, probably better to use ul)
uu=undo all the way to the start
1a=auto ones (move cards 1 away from each other on each other: not strictly optimal)
1b=begin ones (this is safe, as no card stacks are out of order yet)
1s=auto ones safe (only bottom ones visible are matched up)
1f=ones full description (default is off) tells all the hidden moves the computer makes with 1s
1p=push ones once
%=prints stats
o=prints options' current settings
debug shows debug text
EOT
}