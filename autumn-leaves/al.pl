####################################
#al.pl: a PERL simulation of Autumn Leaves, solitaire card game invented (?) by Toby Ord
#
#copyright 2015-16 and hopefully not 17 as I have other projects, but it was fun
#by Andrew Schultz
#
#featuring user conveniences, hints, statistics, save games, etc.
#
#? in-line gives hints
#
#source at https://raw.githubusercontent.com/andrewschultz/miscellany/master/autumn-leaves/al.pl
#project, changes, etc. at https://github.com/andrewschultz/miscellany/blob/master/autumn-leaves/al.pl

use strict;
use warnings;
use integer;
use List::Util 'shuffle';
use Algorithm::Permute; # for 720 test (cw/d)
use Storable qw(dclone);
use Devel::StackTrace;

#tracer
#my $trace = Devel::StackTrace->new; print $trace->as_string . "\n";

my $expected = 0;
my %sre, my %rev;

my $winsThisTime = 0, my $maxWins = 5;

my $i, my $j, my $k, my $x, my $y; # maybe a good idea to define locally too
my $startWith, my $vertical, my $collapse, my $autoOnes, my $beginOnes, my $autoOneSafe, my $sinceLast, my $autoOneFull = 0, my $showMaxRows = 0, my $saveAtEnd = 0, my $ignoreBoardOnSave = 0; #options

my $easyDefault = 0, my $fixedDeckOpt = 0, my $emptyIgnore = 0, my $chainBreaks = 0, my $showBlockedMoves = 0,; #options to init

my $usrInit = 0;

my $movesAtStart; # moves before making a command

my $undoEach; #unsaveable option

my $lastCommand ; # "g"
my $totalTestPass, my $totalTestFail; # testing counts
my $undoDebug; # must be set in-game

my $anySpecial, my $mbGood;
my $drawsLeft;

my $youWon;

my $lastSearchCmd;

my @lastWonArray, my @lastTopCard, my @cardUnder, my @backupCardUnder; # meta info
my @oneDeck, my @fixedDeck;
my @holdAry;

my $undidOrLoadThisTurn, my $errorPrintedYet, my $printedThisTurn, my $moveBar, my $anyMovesYet = 0, my $testing, my $shouldMove, my $currentlyLoadingSaving;
my $avoidWin, my $seventwenty;

my $backupFile = "albak.txt";

my @sui = ("-", "C", "D", "H", "S");
my @vals = ("A", 2, 3, 4, 5, 6, 7, 8, 9, 10, "J", "Q", "K");

my $beforeCmd;
my $showUndoBefore;

#testing global
my @fail;

my @force, my @initArray, my @pointsArray;
my @stack, my @outSinceLast;
my $debug = 0;
my $inMassTest, my $undo, my $quickMove;
my $wins=0, my $losses=0, my $lwstreak=0, my $llstreak=0, my $wstreak=0, my $lstreak=0, my @lastTen; #stat variables
my @cmds, my @pcts, my @undoArray, my @undoLast, my @toggles = ( "off", "on", "random" ); # 2 = random for easy-array. This is a hack, but eh, well...
my $hidCards;
my $cardsInPlay;
my $count = 0;
my $stack;
my $blockedMoves = 0;
my @topCard = ("");
my %inStack;
my %holds;
my $timesAuto = 0;
my $stillNeedWin = 0;

open(A, "altime.txt") || die ("No time lock file altime.txt, no play.\nSample file can look like this:\n1453547368\n86400\n\nYou can make the first number ridiculously big to disable this feature or make the second small to allow more frequent play.");
my $timeLast = <A>; chomp($timeLast);
my $time = time() - $timeLast;
my $del = <A>; chomp($del);
$time = $time - $del;
my $r1 = <A>;
my $r2 = <A>;
if (($r1 < 10001) || ($r1 > 19999)) { print "Save file corrupted.\n"; die; }
if (($timeLast % $r1) != $r2) { print "Save file corrupted.\n"; die; }
if ($time < 0)
{
  my $t = 0 - $time;
  print "Wait a bit and stuff, like ";
  no integer;
  if ($t <  60) { print "$t seconds"; }
  elsif ($t < 3600) { printf("%.2f minutes", $t/60); }
  elsif ($t < 86400) { printf("%.2f hours", $t/3600); }
  else { printf("%.2f days", $t/86400); }
  use integer;
  print ", or edit altime.txt like a big ol' cheater.\n"; exit; } # else { print "$time $del\n"; exit; }
close(A);

readCmdLine(); readScoreFile(); initGlobal();

initGame(); printdeck(0);

while (1)
{
  my $oneline = <STDIN>;
  @cmds = split(/;/, $oneline); for my $myCmd (@cmds) { procCmdFromUser($myCmd); if ($youWon == 1) { last; } }
  seeBlockedMoves();
}
exit;

sub readCmdLine # some global commands like difficulty, debug flags, etc
{
if ($ARGV[0])
{
  $count = 0;
  while ($count <= $#ARGV)
  {
    $a = lc($ARGV[$count]);
    if ($count <= $#ARGV) { $b = lc($ARGV[$count+1]); } else { $b = ""; }
    for ($a)
	{
	#print "Trying $a: $count\n";
    /^-?(sw)?[0-9]/ && do { $a =~ s/^[^0-9]*//g; if ($a < 0) { $a = -$a; } if ($a > 9) { print "That is too many points to start with. If you want 10, go with -ez.\n"; } else { procCmd("sw$a"); } $count++; next; };
	/^-?erd/ && do { $easyDefault = 2; $count++; next; };
	/^-?ezd/ && do { $easyDefault = 1; $count++; next; };
	/^-m(w)?/ && do { $maxWins = $b; $count += 2; next; };
	/^-?er/ && do { fillRandInitArray(); $count++; next; };
	/^-?ez/ && do { fillInitArray("8,9,10,11,12,13"); $count++; next; };
	/^-?[rf]/ && do { $usrInit = 1; if ($a =~ /^-[rf]=/) { $a =~ s/^-[rf]=//g; fillInitArray($a); $count++; } else { fillInitArray($b); $count += 2; } next; };
	/^?-dd/ && do { $debug = 2; $count++; next; };
	/^?-d/ && do { $debug = 1; $count++; next; };
	cmdUse(); exit;
	}
  }
}
}

sub procCmdFromUser #this is so they can't use debug commands
{
  if (($_[0] eq "n-") || ($_[0] eq "n+")) { print "This is a debug command, so I'm ignoring it.\n"; return; }
  $beforeCmd = $#undoArray;
  printDebug("$beforeCmd before command\n");
  $shouldMove = 0;
  procCmd($_[0]);
  my $afterCmd = $#undoArray;
  printDebug("$afterCmd,$beforeCmd,$anyMovesYet,$undidOrLoadThisTurn\n");
  if (($afterCmd - $beforeCmd > 1) && ($anyMovesYet) && (!$undidOrLoadThisTurn))
  {
  splice(@undoArray, $beforeCmd+1, 0, "n+");
  push(@undoArray, "n-");
  printDebug("pushing n+ to " . ($beforeCmd + 1) . "\n");
  checkWellForm();
  }
  $undidOrLoadThisTurn = 0;
  if ((!$errorPrintedYet) && ($shouldMove) && ($beforeCmd == $afterCmd)) { print "NOTE: no moves were made, though no error message was thrown.\n"; }
  if ($undoEach) { print "Undo array: @undoArray\n"; }
  $currentlyLoadingSaving = 0;
}

sub procCmd
{
  my $modCmd = $_[0];
  $errorPrintedYet = 0;
  $printedThisTurn = 0;
  $movesAtStart = $#undoArray;
  chomp($modCmd);
  $modCmd = lc($modCmd);
  $moveBar = 0;
  $modCmd =~ s/^\s+//g;

  if ((length($modCmd) > 0) && (length($modCmd) % 2 == 0))
  {
  my $halfLet = substr($modCmd, 0, length($modCmd)/2);
  if (($modCmd eq "$halfLet$halfLet") && ($modCmd ne "??")) { print "Duplicate command detected. Using $halfLet.\n"; $modCmd = $halfLet; }
  }

  my $letters = $modCmd; $letters =~ s/[^a-z?=]//gi;
  my $numbers = $modCmd;

  $numbers =~ s/[^0-9]//gi;
  my @numArray = split(//, $numbers);

  #meta commands first, or commands with equals
  if ($modCmd =~ /^%$/) { stats(); return; }
  if ($modCmd =~ /^l([bi]?)=/i) { loadDeck($modCmd); return; }
  if ($modCmd =~ /^lf([bi]?)=/i) { loadDeck($modCmd, 1); return; }
  if ($modCmd =~ /^lw=/i) { $avoidWin = 1; loadDeck($modCmd); $avoidWin = 0; return; }
  if ($modCmd =~ /^s([bi]?)=/i) { saveDeck($modCmd, 0); return; }
  if ($modCmd =~ /^sf([bi]?)=/i) { saveDeck($modCmd, 1); return; }
  if ($modCmd =~ /^t=/i) { loadDeck($modCmd, "debug"); return; }
  if ($modCmd =~ /^(f|f=)/) { forceArray($modCmd); return; }
  if ($modCmd =~ /^(ho|ho=)/) { holdArray($modCmd); return; }
  if ($modCmd =~ /^(b|b=)/) { holdArray($modCmd); return; }
  if ($modCmd =~ /^n[-\+]$/) { return; } # null move for debugging purposes
  if ($modCmd =~ /^q+$/) { writeTime(); exit; }
  if ($modCmd =~ /^q/) { print "If you want to exit, just type q."; return; } #don't want playr to quit accidentally if at all possible

  # toggles/commands with numbers that are hard to change
  if ($modCmd =~ /^1b$/) { $beginOnes = !$beginOnes; print "BeginOnes on draw $toggles[$beginOnes].\n"; return; }
  if ($modCmd =~ /^1a$/) { $autoOnes = !$autoOnes; print "AutoOnes on draw $toggles[$autoOnes].\n"; return; }
  if ($modCmd =~ /^1s$/) { $autoOneSafe = !$autoOneSafe; print "AutoOneSafe on move $toggles[$autoOneSafe].\n"; return; }
  if ($modCmd =~ /^1f$/) { $autoOneFull = !$autoOneFull; print "AutoOneFull writeup $toggles[$autoOneFull].\n"; return; }
  if ($modCmd =~ /^1p$/) { ones(1); printdeck(0); return; }

  #remove spaces. Note garbage. Valid commands are above.
  $modCmd =~ s/ //g; my $garbage = $modCmd; $garbage =~ s/[0-9a-z?]//gi; if ($garbage) { print "Warning: excess text ($garbage) in command\n"; }

  if ($letters ne "g") { $lastCommand = $modCmd; }

  for ($letters)
  {
    my $b4 = $#undoArray;
	/^$/ && do
	{
	  if ($numbers =~ /[0789]/) { print "Invalid column specified. Only 1-6 are valid.\n"; return; }
	  if ($numbers eq "") { printdeck(-1); return; } # no error on blank input, just print out. And -1 says don't try ones which removes a n-
	  if ($#numArray == 4)
	  {
	    if (($numArray[0] == $numArray[2]) && ($numArray[1] == $numArray[3])) { pop(@numArray); pop(@numArray); print "Removing duplicate number pair.\n"; }
	  }
	  if ($#numArray > 2) { print "Too many numbers.\n--one number shifts a stack to an empty array\n--two moves a row to another.\n--Three moves 1st-2nd 1st-3rd 2nd-3rd.\n"; return; }
	  if (($#numArray == 2) && isEmpty($numArray[2]) && isEmpty($numArray[1]) && ascending($numArray[0])) { print ("No need, already in order.\n"); return; }
	  if (cmdBadNumWarn($numbers, $letters)) { return; }
	  if ($#numArray == 1)
	  {
	    if ($numArray[0] == $numArray[1]) { print "Can't move stack onto itself.\n"; return; }
		if (isEmpty($numArray[0])) { print "Can't move from empty stack $numArray[0].\n"; return; }
		if (isEmpty($numArray[1]) && (perfAscending($numArray[0])) && (!$undo)) { print "The stack you wish to twiddle ($numArray[0]) is already in order!\n"; return; } # the computer may automatically shift it but we block the player from doing so because computers are perfect
		tryMove("$numArray[0]", "$numArray[1]");

  	    if (($b4 == $#undoArray) && (!$undo)) { if (!$moveBar) { print "($b4/$letters/$numbers) No moves made. Please check the stacks have the same suit at the bottom.\n"; $errorPrintedYet = 1; } }
		return;
	  }
      elsif ($#numArray == 2)
      { # detect 2 ways
	    if (($numArray[0] == $numArray[1]) ||($numArray[0] == $numArray[2]) || ($numArray[1] == $numArray[2])) { print "Duplicate rows in switch. Use x or w instead.\n"; return;}
	    my $possConflict = 0;
		if (isEmpty($numArray[0])) { print "From-row is empty.\n"; return; }
		if (ascending($numArray[0]) && isEmpty($numArray[2]) && (suit(botCard($numArray[1])) == suit(botCard($numArray[0]))))
		{
		  my $temp = $numArray[1];
		  $numArray[1] = $numArray[2];
		  $numArray[2] = $temp;
		  print "Switching last two rows.\n";
		}		
		if (perfAscending($numArray[0]) && isEmpty($numArray[1]))
		{ jumpSecondRow($numArray[0], $numArray[2]); return; }
		if (perfAscending($numArray[0]) && (lowNonChain($numArray[0]) + 1 != botCard($numArray[1])) && (lowNonChain($numArray[0]) + 1 != botCard($numArray[2])))
		{ jumpSecondRow($numArray[0], $numArray[2]); return; }
		if (isEmpty($numArray[0])) { print "Can't move from an empty stack.\n"; printAnyway(); return; }
		if ((!canMove($numArray[0], $numArray[1])) || (!canMove($numArray[0], $numArray[2]))) { $possConflict = 1; printDebug ("Possible conflict $numArray[0] $numArray[1] $numArray[2]\n"); }
        if ($numArray[0] == $numArray[1]) { print "Repeated number.\n"; return; }
        $shouldMove = 1;
	    $quickMove = 1;
	    tryMove("$numArray[0]", "$numArray[1]");
	    tryMove("$numArray[0]", "$numArray[2]");
	    tryMove("$numArray[1]", "$numArray[2]");
	    $quickMove = 0;
  	    if (($b4 == $#undoArray) && (!$undo))
		{
		  if (!$moveBar) { print "No moves made. Please check the stacks you tried to shift.\n"; $errorPrintedYet = 1; }
		}
		else
		{
		  printdeck(0);
		  if ($possConflict) { print "I was able to move some despite suits and/or card values not matching up or the first column not being the lowest value.\n"; }
		  checkwin();
		}
	    return;
      }
	  elsif ($#numArray == 0)
      {
        if ($numArray[0] !~ /[1-6]/) { print "Valid rows are to auto-move are 1-6.\n"; return; }
  	    my $totalRows = 0;
	    my $anyEmpty = 0;
		my $forceRow;
	    my $fromCardTop = $#{$stack[$numArray[0]]};
	    my $temp = 0;

	    while (($fromCardTop > 0) && ($stack[$numArray[0]][$fromCardTop] == $stack[$numArray[0]][$fromCardTop-1] - 1) && ($stack[$numArray[0]][$fromCardTop] % 13)) { $fromCardTop--; } # see if we can move the whole stack

        my $fromCard;
		if ($#{$stack[$numArray[0]]} == -1) { $fromCard = -1; } else { $fromCard = $stack[$numArray[0]][$fromCardTop]; }

        for my $tryRow (1..6)
	    {
	      my $toCard = botCard($tryRow);
	      if ($#{$stack[$tryRow]} < 0) { $anyEmpty++; }
	      #print "$fromCard - $toCard, " . cromu($fromCard, $toCard) . " $#{$stack[$tryRow]} && $emptyIgnore\n";
	      if ((cromu($fromCard, $toCard)) || (($#{$stack[$tryRow]} < 0) && !$emptyIgnore))
	      {
  	        if (($toCard - $fromCard == 1) && ($fromCard % 13))
		    {
		      tryMove("$numArray[0]", "$tryRow"); # force 4-3 if we have 4S, QS, 3S
		      return;
		    }
	        if ($tryRow != $numArray[0])
	        { if (($fromCardTop != 0) || ($#{$stack[$tryRow]} != -1)) { $totalRows++; $forceRow = $tryRow; } # empty, Kh-7h, 4h : 4h to 7h #print "$tryRow works. $#{$stack[$tryRow]}\n";
	        }
	      }
	    }
	    if ($totalRows == 0) { print "No row to move $numArray[0] to."; if ($anyEmpty) { print " There's an empty one, but you disabled it with e."; } print "\n"; return; }
	    elsif ($totalRows > 1)
	    {
	      if ((emptyRows() > 0) && ($totalRows > 1)) { print "First empty row is " . firstEmptyRow() . ".\n"; tryMove("$numArray[0]" , firstEmptyRow()); return; }
  	      print "Too many rows ($totalRows) to move $numArray[0] to.\n"; return;
	    }
	    else { if (isEmpty($numArray[0])) { print("Nothing to move."); return; } print "Forcing $numArray[0] -> $forceRow.\n"; tryMove("$numArray[0]", "$forceRow"); return; }
      }
	  return;
	};
    /^a$/ && do { if ($#numArray < 1) { print "Need 2 row numbers.\n"; return; } $shouldMove = 1; $modCmd =~ s/[a]//g; altUntil($modCmd); return; };
    /^af/ && do { cmdNumWarn($numbers, $letters); if ($#force == -1) { print "Nothing in force array.\n"; } else { print "Force array: " . join(",", @force) . "\n"; } return; };
    /^c$/ && do { cmdNumWarn($numbers, $letters); $collapse = !$collapse; print "Card collapsing $toggles[$collapse].\n"; return; };
    /^cb$/ && do { cmdNumWarn($numbers, $letters); $chainBreaks = !$chainBreaks; print "Showing bottom chain breaks $toggles[$chainBreaks].\n"; return; };
	/^c[wd]$/ && do { cmdNumWarn($numbers, $letters); check720(0); return; };
	/^c[wd]x$/ && do { cmdNumWarn($numbers, $letters); check720(1); return; };
    /^d$/ && do { cmdNumWarn($numbers, $letters); if (($anySpecial) && ($drawsLeft)) { print "Push df to force--there are still potentially productive moves."; if ($mbGood) { print " $mbGood is one."; } print "\n"; return; } else { drawSix(); printdeck(0); checkwin(); return; } };
    /^deckraw/ && do { cmdNumWarn($numbers, $letters); printdeckraw(); return; };
    /^df$/ && do { cmdNumWarn($numbers, $letters); drawSix(); printdeck(0); checkwin(); return; };
    /^dl$/ && do { if (cmdNumWarn($numbers, $letters, 1)) { print "Need an argument for debuglevel, which is currently $debug.\n"; return; } if (($numArray[0] > 2)) { print "Debug must be between 0 and 2.\n"; return; } print "Debug level was $debug, is "; $debug = $numArray[0]; print "$debug now.\n"; return; };
    /^du$/ && do { cmdNumWarn($numbers, $letters); $undoDebug = !$undoDebug; print "Undo debug now $toggles[$undoDebug].\n"; return; };
    /^e$/ && do { cmdNumWarn($numbers, $letters); $emptyIgnore = !$emptyIgnore; print "Ignoring empty cell for one-number move $toggles[$emptyIgnore].\n"; return; };
    /^er(d?)$/ && do { $easyDefault = 2; print "Easy default is now 6-in-a-row but random.\n"; return; };
    /^ez$/ && do { print "Wiping out move array and restarting the easiest possible start.\n"; $anyMovesYet = 0; if ($easyDefault == 2) { fillRandInitArray(); } else { fillInitArray("8,9,10,11,12,13"); } doAnotherGame(); return; };
    /^ezd$/ && do { $easyDefault = !$easyDefault; print "Easy default is now $toggles[$easyDefault].\n"; return; };
    /^g$/ && do { if (!defined($lastCommand)) { print "No last command.\n"; return; } cmdNumWarn($numbers, $letters); print "Retrying $lastCommand.\n"; procCmd($lastCommand); return; };
    /^h$/ && do { cmdNumWarn($numbers, $letters); showhidden(); return; };
    /^ha$/ && do { cmdNumWarn($numbers, $letters); printHoldArray(0); return; };
	/^ib$/ && do { cmdNumWarn($numbers, $letters); $ignoreBoardOnSave = !$ignoreBoardOnSave; print "Adding IGNORE to save-position $toggles[$ignoreBoardOnSave].\n"; return; };
    /^is$/ && do { cmdNumWarn($numbers, $letters); printHoldArray(1); return; };
    /^ll$/i && do { cmdNumWarn($numbers, $letters); if (!$lastSearchCmd) { print "Can't load last--we haven't loaded a game in the first place.\n"; return; } loadDeck($lastSearchCmd); return; };
    /^lu$/ && do { cmdNumWarn($numbers, $letters); if ($fixedDeckOpt) { peekAtCards(); } else { print "Must have fixed-deck card set.\n"; } return; };
    /^lw$/ && do { cmdNumWarn($numbers, $letters); printLastWon(); if ($modCmd =~ /^lw=/) { saveLastWon($modCmd); } return; };
    /^mr$/ && do { cmdNumWarn($numbers, $letters); $showMaxRows = !$showMaxRows; print "Show Max Rows $toggles[$showMaxRows].\n"; return; };
    /^o$/ && do { cmdNumWarn($numbers, $letters); showOpts(); return; };
    /^(os|so)$/ && do { cmdNumWarn($numbers, $letters); saveOpts(); return; };
    /^pl$/ && do { cmdNumWarn($numbers, $letters); if ($#pointsArray > -1) { for my $z (0..$#pointsArray) { if ($z > 0) { print ", "; } print ($z+1); print "="; print $pointsArray[$z]; } print "\n"; } else { print "No draws yet.\n"; } return; };
     /^r$/ && do {
      cmdNumWarn($numbers, $letters);
      if ($drawsLeft) { print "Use RY to clear the board with draws left.\n"; return; } if ($modCmd =~ /^ry=/) { $modCmd =~ s/^ry=//g; fillInitArray($modCmd); }
	  doAnotherGame();
	  return;
    };
    /^ra$/ && do { if (($drawsLeft < 5) || ($hidCards < 16)) { print "Need to restart to toggle randomization.\n"; return; } $fixedDeckOpt = !$fixedDeckOpt; print "fixedDeck card-under $toggles[$fixedDeckOpt].\n"; return; };
	/^rct$/ && do { cmdNumWarn($numbers, $letters); for my $b ('c', 'd', 'h', 's') { for my $a ('a', 2, 3, 4, 5, 6, 7, 8, 9, 10, 'j', 'q', 'k') { print "$a$b" . revCard("$a$b") . " "; } print "\n"; } return; };
	/^rd$/ && do { if ($#undoLast <= $#undoArray) { print "Last redo array is no larger than current undo array. Aborting.\n"; return; }
	for (0..$#undoArray) { if ($undoArray[$_] ne $undoLast[$_]) { print "Redo array and undo array mismatch. Aborting.\n"; return; } }
	$undo = 1; for my $rdmove ($#undoArray+1..$#undoLast) { procCmd($undoLast[$rdmove]); } $undo = 0;
	printdeck(0);
	return;
	};
    /^ry$/ && do {
      cmdNumWarn($numbers, $letters);
      if ($drawsLeft) { print "Forcing restart despite draws left.\n"; } if ($modCmd =~ /^ry=/) { $modCmd =~ s/^ry=//g; fillInitArray($modCmd); }
	  doAnotherGame();
	  return;
    };
    /^sae$/ && do { cmdNumWarn($numbers, $letters); $saveAtEnd = !$saveAtEnd; print "Save at end to undo-debug.txt now $toggles[$saveAtEnd].\n"; return; };
    /^sb$/ && do { cmdNumWarn($numbers, $letters); $showBlockedMoves = !$showBlockedMoves; print "Show blocked moves $toggles[$showBlockedMoves].\n"; return; };
    /^sd$/ && do { cmdNumWarn($numbers, $letters); saveDefault(); return; };
    /^sl$/ && do { open(B, ">>undo-debug.txt"); print B "Last undo array info=====\nTC=" . join(",", @topCard) . "\nM=" . join(",", @undoLast) . "\n"; close(B); print "Last undo array info saved to undo-debug.txt.\n"; return; };
    /^sol$/ && do { cmdNumWarn($numbers, $letters); $sinceLast = !$sinceLast; print "See overturned since last now $toggles[$sinceLast].\n"; return; };
    /^su$/ && do { cmdNumWarn($numbers, $letters); $showUndoBefore = !$showUndoBefore; print "ShowUndoBefore now $toggles[$showUndoBefore].\n"; return; };
    /^sw$/ && do { if (!$numbers) { printPoints(); return; }
    if (($numbers < 2) || ($numbers > 9)) { print "You can only fix 2 through 9 to start. Typing sw0 gives odds of starting points,\n"; return; }
    $startWith = $numbers;
    if ($startWith > 7) { print "WARNING: this may take a bit of time to set up, and it may ruin some of the game's challenge, as well.\n"; } print "Now $startWith points (consecutive cards or cards of the same suit) needed to start. sw0 prints the odds.\n"; return;
    };
    /^[!t~`]$/ && do {
    if (cmdBadNumWarn($numbers, $letters)) { return; }
    if (cmdNumWarn($numbers, $letters, 1)) { return; }
      my $didAny;
	  my $empties;
	  my $localFrom, my $localTo, my $curMinToFlip;
	  printNoTest("3-waying stacks $numArray[0], $numArray[1] and $numArray[2].\n");
      $shouldMove = 1;
	  $quickMove = 1;
      while (anyChainAvailable($numArray[0], $numArray[1], $numArray[2]))
	  {
	    $empties = 0;
	    for (1..3) { if ($#{$stack[$_]} == -1) { $empties++; } }
	    if ($empties == 2) { print "You made a full chain!\n"; last; }
	    $localFrom = 0; $localTo = 0;
	    $curMinToFlip = 0;
		my $foundChain = 0;
	    for my $j (1..3) #this is so we pull the lowest card onto the lowest remaining. Not fully workable eg (other)-7-6-5 3-2-1-j-10-9 k-q-8-4 will lose
	    #we'd need a check for "lowest" and "safest" and "safest" trumps "lowest" but if there is nothing else, "lowest"
  	    {
	      for my $k (1..3)
		  {
		    if (canChain($numArray[$j], $numArray[$k]))
		    {
  		      $foundChain = 1;
			  if (($stack[$numArray[$k]][$#{$stack[$numArray[$k]]}] < $curMinToFlip) || ($curMinToFlip == 0)) { $localFrom = $j; $localTo = $k; }
		    }
		    else { }
		  }
	    }
	    tryMove("$numArray[$localFrom]", "$numArray[$localTo]");
	    if ($foundChain)
	    {
	      $didAny = 1;
	    }
	  }
	  $quickMove = 0;
	  if (!$testing)
	  {
	  if ($didAny) { printdeck(0); print "$didAny total shifts.\n"; checkwin(); } else { print "No shifts available.\n"; }
	  }
	  checkwin();
	  return;
    };
    /^tf$/ && do { runEachTest(); return; };
    /^u$/ && do { if (!$numbers) { undo(0); } else { if ($numbers > 10) { print "Use um for mass undo--this is to avoid u351 or something by mistake.\n"; return; } undo(1, $numbers); } return; };
    /^ua$/ && do { cmdNumWarn($numbers, $letters); print "Top cards to start:"; for (1..6) { print " $topCard[$_](" . faceval($topCard[$_]) . ")"; } print "\nMoves (" . ($#undoArray+1) . "): " . join(",", @undoArray) . "\n"; return; };
 	/^ub$/ && do { cmdNumWarn($numbers, $letters); undo(3); return; };
 	/^ud$/ && do { cmdNumWarn($numbers, $letters); undo(2); return; };
    /^ue$/ && do { cmdNumWarn($numbers, $letters); $undoEach = !$undoEach; print "UndoEach now $toggles[$undoEach].\n"; return; };
    /^ul$/ && do { cmdNumWarn($numbers, $letters); print "Last undo array info=====\nTC=" . join(",", @topCard) . "\nM=" . join(",", @undoLast) . "\n"; return; };
    /^um$/ && do { if (!$numbers) { undo(0); } else { undo(1, $numbers); } return; };
	/^us$/ && do { cmdNumWarn($numbers, $letters); $undidOrLoadThisTurn = 1; undoToStart(); return; };
    /^v$/ && do { cmdNumWarn($numbers, $letters); $vertical = !$vertical; print "Vertical view $toggles[$vertical].\n"; return; };
    /^[wy]$/ && do
	{
	  if ($#numArray != 2) { print "Y/W requires 3 numbers: from, middle, to.\n"; return; }
	  if (isEmpty($numArray[2]) && isEmpty($numArray[1]) && ascending($numArray[0])) { print ("No need, already in order.\n"); return; }
	  thereAndBack(@numArray);
	  return;
	};
    /^x$/ && do
    {
	  if (cmdBadNumWarn($numbers, $letters)) { return; }
	  if ($#numArray == 0)
	  {
	    expandOneColumn($numbers);
		if (emptyRows() == 2) #this checks if we can redo the command
		{
		while(onesuit($numbers) && !ascending($numbers))
		{
		my $oldmove = $#undoArray;
		expandOneColumn($numbers);
		if ($#undoArray == $oldmove) { print("Debug note: broke out of potential infinite loop."); last; }
		}
		}
		printdeck(0);
		checkwin();
		return;
	  }
	  if ($#numArray == 2)
      {
	    if ((botSuit($numArray[0]) != botSuit($numArray[1])) && (!isEmpty($numArray[1]))) { print "Wrong middle suit.\n"; return; }
	    if ((botSuit($numArray[0]) != botSuit($numArray[2])) && (!isEmpty($numArray[2]))) { print "Wrong to-from suit.\n"; return; }
        $shouldMove = 1;
	    $b4 = $#undoArray;
	    $quickMove = 1;
		#printDebug(1);
        autoShuffleExt($numArray[0], $numArray[2], $numArray[1]);
		#printDebug(2);
	    $quickMove = 0;
	    if ($b4 == $#undoArray) { if (!$moveBar) { print "No moves made. Please check the stacks you tried to shift.\n"; $errorPrintedYet = 1; } } else { printdeck(0); checkwin(); }
	    return;
      }
	  if ($#numArray == 3) { print "Too many numbers. "; }
	  print "x (1 number) spills a row. x (3 numbers) sends 1st to 3rd via 2nd.\n"; return;
	};
    /^wf$/ && do { checkWellForm(); return; };
    /^z$/ && do { cmdNumWarn($numbers, $letters); print "Time passes more slowly than if you actually played the game.\n"; return; };
    /^\?\?/ && do { cmdNumWarn($numbers, $letters); usageDet(); return; };
    /^\?/ && do { cmdNumWarn($numbers, $letters); usage(); return; }; #anything below here needs sorting
  #if ($modCmd =~ /^[0-9]{2}[^0-9]/) { $shouldMove = 1; $modCmd = substr($modCmd, 0, 2); tryMove($modCmd); tryMove(reverse($modCmd)); return; }
  }; # end letters for-loop
  print "Command ($modCmd) ";
  if ($numbers && $letters) { print "($letters/$numbers) "; }
  print "wasn't recognized. Push ? for basic usage and ?? for in-depth usage.\n";
}

sub canDraw
{
  my $x = $inStack{$_[0]} || $holds{$_[0]}; if (!$x) { $x = 0; }
  return $x;
}

sub suitstat
{
  my $base = $_[0] * 13 + 1;
  my $leftInSuit = 0;
  for my $card ($base..$base+12) { $leftInSuit += canDraw($card); }
  if (canDraw($base+1) && canDraw($base+2) && !canDraw($base)) { return 2; } #3h & 2h but not ah missing, can win
  if ($leftInSuit == 2)
  {
    if (canDraw($base) && canDraw($base+12)) { return 1; } #kh & ah missing, trickier
  }
  if (($leftInSuit > 1) && canDraw($base)) { return 3; } #7h & ah missing, always doable I think/hope
  if (canDraw($base)) { return 4; }
  return 0;
}

sub jumpSecondRow
{
  if (isEmpty($_[1]) && (perfAscending($_[0])) && (!$undo)) { print "Flipping to another empty row wouldn't do anyting. Stack $_[0] is already in order.\n"; return;  }
  print "Don't need a third row to move from $_[0] to $_[1].\n"; tryMove("$_[0]", "$_[1]"); return;
}

sub check720
{
  my @suitStatus = (0, 0, 0, 0, 0);
  $stillNeedWin = $_[0];
  for (0..3) { $suitStatus[suitstat($_)]++; }
  if ($drawsLeft != 1)
  {
    $stillNeedWin = 0;
    if ($suitStatus[0] ==4) { print "Even with >1 draw left, you're still pretty blocked.\n"; return; }
    print "You probably have a chance, but you need to have 1 draw left to use the check-auto-win command.\n"; return;
  }
  my @initArray = ();
  my $couldWork = 0;
  print "Checking for draw-to-win/win-on-draw...\n";
  if ($hidCards >= 6) { print "Too many cards out. It's very doubtful you can win this unless the deck is rigged, and it'd take too much time.\n"; return; }
  if ($hidCards > 2)
  {
    print "It may take a while to see all possibilities, and there's not likely to be a win. Tally anyway?"; my $q = <STDIN>; if ($q !~ /y/) { print "OK.\n"; return; }
	my $fact = 720; for (1..$hidCards) { $fact = $fact * (6 + $_); }
	print "Total possibilities = " . $fact . "\n";
  }
  for (1..52) { if ($inStack{$_} || $holds{$_}) { push(@initArray, $_); if (($_ % 13 != 1) && ($inStack{13*(($_-1)/13)+1})) { $couldWork = 1; } } }
  if (emptyRows() < 2) { print "You don't seem to have enough empty rows for an easy forced win, except in extreme circumstances.\n"; }
  elsif ($suitStatus[0] == 4)
  {
    print "With all aces out, no easy draw-to-wins are expected.\n";
  }
  else
  {
  if ($suitStatus[3])
  {
    if (allAscending()) { print "A suit without an ace is missing another card, so there should be draw-to-wins.\n"; }
    else { print "Not everything's in order, yet. It looks like you can still do a bit more to maybe increase the number of draw-to-wins possible, but we'll try anyway.\n"; }
  }
  elsif ($suitStatus[2])
  {
    print "A 2 and a 3 of the same suit are missing, so the final auto-sweep may have them pick up the Ace for a possible win.\n";
  }
  elsif ($suitStatus[1])
  {
    print "You're missing the K and A of a suit, which can in rare cases help a bit, but probably not.\n";
  }
  elsif ($suitStatus[4])
  {
    print "You're missing an ace in a suit, but nothing else, so you don't have enough.\n";
  }
  if ($hidCards == 1) { print "With a card still to pull, you may need a bit of luck for a draw-to-win.\n"; }
  if ($hidCards >= 2) { print "Draws may appear in random order, so the tally may not be exact or consistent.\n"; }
  }
  my $count = 0;
  my $thiswin;
  my $oldCardsInPlay = $cardsInPlay;
  my $wins =0;
  my $firstPermu = "";
  my @backupArray = @undoArray;
  Algorithm::Permute::permute {
  my @array2 = @{dclone(\@stack)};
  $count++;
  if (($count >= 1000) && ($count % 1000 == 0)) { print "$count so far.\n"; }
  @force = @initArray;
  drawSix();
  $seventwenty = 1;
  for (@initArray) { $inStack{$_} = 0; $holds{$_} = 0; }
  $printedThisTurn = 0;
  ones(0);
  $thiswin = checkwin();
  $seventwenty = 0;
  if ($thiswin == 1) { if (!$firstPermu) { for (0..5) { $firstPermu .= " " . faceval($initArray[$_]); } } $wins++; }
  @stack = @{dclone(\@array2)};
  $drawsLeft = 1;
  } @initArray;
  $seventwenty = 0;
  if ($wins)
  { print "$wins of $count draw-to-win" . plur($wins) . ". The first one is$firstPermu.\n"; %holds = (); }
  else
  { print "No draw-to-wins found.\n"; }
  @outSinceLast = ();
  for (@initArray) { if (!$holds{$_}) { $inStack{$_} = 1; } else { $holds{$_} = 1; } }
  @force=();
  @undoArray = @backupArray;
  $cardsInPlay = $oldCardsInPlay;
  if (($stillNeedWin) && ($wins))
  {
    if ($count % $wins) { no integer; $expected = sprintf("%.2f", $count / $wins); } else { $expected = $count / $wins; }
    
    $timesAuto = 0;
     while ($stillNeedWin)
	 {
	   $timesAuto++;
        procCmdFromUser("d");
		if ($stillNeedWin)
		{
		procCmdFromUser("u");
		}
		%holds = ();
	 }
  }
  $stillNeedWin = 0;
}

sub perfAscending
{
  for my $q (0..$#{$stack[$_[0]]}-1)
  {
    #print "$q: $stack[$_[0]][$q] - $stack[$_[0]][$q+1]\n";
    if (($stack[$_[0]][$q] - $stack[$_[0]][$q+1] != 1) || ($stack[$_[0]][$q] % 13 == 1))
	{
	  if (($stack[$_[0]][$q] % 13 == 1) && ($stack[$_[0]][$q+1] % 13 == 0) && ($stack[$_[0]][0] % 13 == 0)) { }
	  else { return 0; }
	}
  }
  return 1;
}

sub thereAndBack
{
    my $oldEmptyRows = emptyRows();
	my $b4 = $#undoArray;
	my $wayb4 = $b4;
	my $wrongOrder = 0;
	if (isEmpty($_[2]) && !isEmpty($_[1]))
	{
	  my $temp = $_[2]; $_[2] = $_[1]; $_[1] = $temp;
	  $wrongOrder = 1;
	}
	if (!canMove($_[0], $_[2]) && !canMove($_[2], $_[0])) { print "Can't move $_[0] onto $_[2].\n"; return; }
	if (!canMove($_[0], $_[1])) { print "Can't move $_[0] through $_[1].\n"; return; }
    $shouldMove = 1;
	$quickMove = 1;
	
	my $thiscount = 0;
	
	do
	{
	$b4 = $#undoArray;
	my $oldSuit = botSuit($_[0]);
    autoShuffleExt($_[0], $_[2], $_[1], botSuit($_[0]));
	if ($b4 != $#undoArray) { $errorPrintedYet = 1; } # this is a bit of a hack. No error is printed yet, but if we made a successful move, we may print a misleading error.
	if ($oldSuit == botSuit($_[2])) # don't even try a comeback if there's a different suit.
	{
    autoShuffleExt($_[2], $_[0], $_[1], botSuit($_[0]));
	}
	
	$thiscount++; if ($thiscount == 25) { print"Loop took too many times. Breaking. Suggest undo-save to figure why.\n"; last; }
	
	} while (($#undoArray > $b4) && ($lastCommand =~ /y/) && (!isEmpty($_[0])) && (!isEmpty($_[2])));
	$quickMove = 0;
	if ($wayb4 == $#undoArray) { if (!$moveBar) { print "No moves made. Please check the stacks you tried to shift.\n"; $errorPrintedYet = 1; } } else
	{
	  printdeck(0);
	  if ($wrongOrder)
	  {
	  print "NOTE: I switched the last two numbers, since you specified to an empty row. You can UNDO if it doesn't work for you.\n";
	  }
	  checkwin();
	}
	return;
}

sub expandOneColumn
{
    my $oldEmptyRows = emptyRows();
    if (emptyRows() < 2) { print "Not enough empty rows.\n"; return; }
    if ($_[0] !~ /[1-6]/) { print "Not a valid row.\n"; return; }
	my @rows = (0, 0);
	my $thisRow = $_[0]; $thisRow =~ s/x//g;
    my $fromSuit = botSuit($thisRow);
	if ($#{$stack[$thisRow]} == -1) { print "Nothing to spill in row $thisRow.\n"; return; }
	if (($thisRow < 1) || ($thisRow > 6)) { print "Not a valid row to shuffle. Please choose 1-6.\n"; die; }
	for my $emcheck (1..6)
	{
	  my $fromrow;
	  #print "$emcheck: $stack[$emcheck][0], @{$stack[$emcheck]}\n";
	  if (!$stack[$emcheck][0])
	  {
	    if ($rows[0]) { $rows[1] = $emcheck; $fromrow = $rows[0]; last; }
	    else
	    {
	    $rows[0] = $emcheck; $fromrow = $rows[1];
	    }
	  }
	}

	my $tempAsc = ascending($thisRow);

	if ($tempAsc == 1) { print "Row $thisRow is already in order.\n";  return; } elsif ($tempAsc > 1) { print "Row $thisRow is already in order, with a suit done. Moving the bottom suit would only clog up a row.\n"; return; }

    $shouldMove = 1;

	$errorPrintedYet = 1; # a bit fake, but we already error checked above.
	$quickMove = 1;
	printDebug("Row $thisRow: " . botSuit($thisRow) . " " . botSuit($rows[0]) . " (" . botCard($rows[0]) . ", row $rows[0]) " . botSuit($rows[1]) . " (" . botCard($rows[1]) . ", row $rows[1])\n");
	if (botSuit($thisRow) == $fromSuit)
	{
    if ((botSuit($thisRow) == botSuit($rows[0])) || (botSuit($rows[0]) == -1))
	{
	  printDebug("x-command 1\n");
	  autoShuffleExt($thisRow, $rows[0], $rows[1]);
	}
	elsif ((botSuit($thisRow) == botSuit($rows[1])) || (botSuit($rows[1]) == -1))
	{
	  printDebug("x-command 2\n");
	  autoShuffleExt($thisRow, $rows[1], $rows[0]);
	}
	}
	if (emptyRows() > 1)
	{
	  my $thisRow = firstEmptyRow();
	  printDebug("x-command 3\n");
	  if (($thisRow != $rows[0]) && ($thisRow != $rows[1])) { autoShuffleExt($rows[0], $thisRow, $rows[1]); autoShuffleExt($rows[1], $thisRow, $rows[0]); }
	}
	if (botSuit($thisRow) == $fromSuit)
	{
	  my $count = 0;
	  printDebug("Trying extra\n");
      while ((isEmpty($rows[1]) + isEmpty($rows[0]) + isEmpty($thisRow) < 2) && suitsAligned(suit(botCard($rows[0])), suit(botCard($rows[1])), suit(botCard($thisRow)), $fromSuit))
	  {
	    my $beforeCmd = $#undoArray;
		$count += 1; if ($count == 20) { print"Oops. This took too long, bailing.\n"; last; }
	    printDebug ("Shift $count\n");
	    $errorPrintedYet = 1; # very hacky but works for now. The point is, any move should work, and the rest will be cleaned up by the ext function
	    my $from = lowestOf($rows[0], $thisRow, $rows[1]);
  	    printDebug ("Lowest row is $from, card " . faceval(botCard($from)) . " of $rows[0] $rows[1] $thisRow\n");
	    if ($from == $rows[0]) { if (botCard($thisRow) > botCard($rows[1])) { autoShuffleExt($rows[0], $thisRow, $rows[1]); } else { autoShuffleExt($rows[0], $rows[1], $thisRow); } }
	    elsif ($from == $rows[1]) { if (botCard($thisRow) > botCard($rows[0])) { autoShuffleExt($rows[1], $thisRow, $rows[0]); } else { autoShuffleExt($rows[1], $rows[0], $thisRow); } }
	    else { if (botCard($rows[0]) < botCard($rows[1])) { autoShuffleExt($thisRow, $rows[0], $rows[1]); } else { autoShuffleExt($thisRow, $rows[1], $rows[0]); } }
		if ($#undoArray == $beforeCmd) { printDebug("Nothing turned over turn $count."); last; }
	  }
	}
	if (isEmpty($rows[1]) + isEmpty($rows[0]) == 1)
	{
	  my $eRow = $rows[0];
	  if (isEmpty($rows[1])) { $eRow = $rows[1]; }
	  my $oRow = $rows[0] + $rows[1] - $eRow;
	  if (botSuit($thisRow) == botSuit($oRow) && (topish($oRow) < topish($thisRow))) #special case if a you have, say, JS and KS-9S-7S left
	  {
	  #autoShuffleExt($thisRow, $eRow, $oRow);
	  $moveBar = 0;
	  autoShuffleExt($thisRow, $oRow, $eRow);
	  }
	}
	$quickMove = 0;
	return;
}

sub topish
{
  if (isEmpty($_[0])) { return -1; }
  my $temp = $#{$stack[$_[0]]};
  my $sui = suit($stack[$_[0]][$temp]);

  while (($temp >= 0) && (suit($stack[$_[0]][$temp]) == $sui))
  {
    $temp--;
  }
  $temp++;
  return ($stack[$_[0]][$temp]);
}

sub cmdNumWarn # Arg: numbers, letters, (requires numbers?)
{
  if ($#_ < 1) { print "WARNING: wrong # of parameters called to cmdNumWarn.\n"; my $trace = Devel::StackTrace->new; print $trace->as_string . "\n"; return 0; }
  my $let = $_[1];
  if (!$let) { $let = "(empty)"; }
  if (($#_ < 2) && ($_[0] ne "")) { print "WARNING: command $let does not require numbers.\n"; return 1; }
  if (($#_ >= 2) && ($_[0] eq "")) { print "WARNING: command $let requires numbers.\n"; return 1; }
  return 0;
}

sub cmdBadNumWarn
{
  if ($#_ < 1) { print "WARNING: wrong # of parameters called to cmdBadNumWarn.\n"; my $trace = Devel::StackTrace->new; print $trace->as_string . "\n"; return 0; }
  my $let = $_[1];
  if (!$let) { $let = "(empty)"; }
  if ($_[0] =~ /[0789]/) { print "WARNING: command $let requires only numerals 1-6.\n"; return 1; }
  return 0;
}

sub lowestOf
{
  my $lowRow = $_[0];
  my $botCard = botCard($_[0]);
  my $b = botCard($_[1]);
  if  (($b < $botCard) && ($b > 0)) { $botCard = $b; $lowRow = $_[1]; }
  my $c = botCard($_[2]);
  if  (($c < $botCard) && ($c > 0)) { $botCard = $c; $lowRow = $_[2]; }
  return $lowRow;
}

sub canMove
{
  #print botSuit($_[0]) . " vs " . botSuit($_[1]) . " suits\n";
  #print botCard($_[0]) . " vs " . botCard($_[1]) . " cards\n";
  if ($#{$stack[$_[1]]} == -1) { return 1; }
  if (botSuit($_[0]) != botSuit($_[1])) { return 0; }
  if (botCard($_[0]) > botCard($_[1])) { return 0; }
  return 1;
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

sub anyChainAvailable
{
  for my $temp (0..2)
  {
    my $sz = $#{$stack[$_[$temp]]};
    if ($sz >= 12)
	{
	  my $gotStraight = 1;
	  for my $back (0..12) { if ($stack[$_[$temp]][$sz] + $back != $stack[$_[$temp]][$sz-$back]) { $gotStraight = 0; } }
	  if (($gotStraight == 1) && (!$testing)) { print "You got the whole suit straight on row $_[$temp].\n"; return 0; }
	}
	return canChain($_[1], $_[2], -1) || canChain($_[1], $_[0], -1) || canChain($_[2], $_[0], -1) || canChain($_[2], $_[1], -1) || canChain($_[0], $_[1], -1) || canChain($_[0], $_[2], -1);
	#test this somehow
  }
}

sub processGame
{
  $moveBar = 1;
  $quickMove = 0;

  if (!$anyMovesYet) { print "No hand-typed moves yet, so stats aren't recorded.\n"; return; }
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

}

sub doAnotherGame
{

@cmds = ();

processGame();
initGame();
printdeck(0);
}

sub copyAndErase
{
  `copy $backupFile $_[0]`;
  `erase $backupFile`;
}

sub saveLastWon
{
  my $filename = "al-sav.txt";

  my $truncated = $_[0]; $truncated =~ s/^lw=//g;

  open(A, "$filename");
  open(B, ">$backupFile");
  while ($a = <A>)
  {
    print B $a;
  }
  print B "s=$truncated\n";
  print B "TC=" . join(",", @topCard) . "\n";
  print B "M=" . join(",", @undoArray) . "\n";
  for (1..6) { print B join(",", @{$stack[$_]}); print B "\n"; }
  close(B);
  close(A);
  copyAndErase($filename);
  print "Last-won $truncated is appended.\n";
}

sub saveDeck
{
  $undidOrLoadThisTurn = 1; $currentlyLoadingSaving = 1;
  chomp($_[0]);
  my $filename = "al-sav.txt";
  my $overwrite = 0;
  my $ignorePrintedCards = $ignoreBoardOnSave;

  my $prefix = $_[0]; $prefix =~ s/=.*//g;
  if ($prefix =~ /i/) { $ignorePrintedCards = 1; }
  if ($prefix =~ /b/) { $ignorePrintedCards = 0; }

  open(A, "$filename");
  open(B, ">$backupFile");
  $lastSearchCmd = $_[0];
  if ($lastSearchCmd =~ /^s[a-z]+=/i)
  {  printDebug("Trimming $lastSearchCmd to ");
    $lastSearchCmd =~ s/^s[a-z]+=/s=/gi;
	printDebug("$lastSearchCmd\n");
  } # get rid of that extra garbage

  my $topCards = "";
  if ($#topCard > -1) { $topCards = join(",", @topCard); }
  my $undoArys = "";
  if ($#undoArray > -1) { $undoArys = join(",", @undoArray); }
  my $fullWriteString = "$vertical,$collapse\nTC=$topCards\nM=$undoArys\n";
  if ($ignorePrintedCards) { $fullWriteString .= "IGNORE\n"; }
  if ($fixedDeckOpt)
  {
    $fullWriteString .= "FD=" . join(",", @oneDeck) . "\n";
    for (1..6) { $fullWriteString .= "HC=" . join(",", @{$backupCardUnder[$_]}) . "\n"; }
  }
  for (1..6) { $fullWriteString .= join(",", @{$stack[$_]}) . "\n"; }

  while ($a = <A>)
  {
    print B $a;
	if ($a =~ /^;/) { last; }
    if ($a =~ /^s=$lastSearchCmd$/i)
	{
	  if ($_[1] == 0) { print "Already an entry named $lastSearchCmd. Use sf= to force.\n"; close(B); close(A); return; } #we don't care if the backup file is mashed. It'll be re-overwritten anyway
      print "Overwriting entry $lastSearchCmd\n";
	  $overwrite = 1;
	  <A>;
	  print B $fullWriteString;
	  for (1..6) { <A>; }
	}
  }

  if (!$overwrite)
  {
    print B "$lastSearchCmd\n";
    print B $fullWriteString;
	for (1..6) { <A>; }
  }

  while ($a = <A>) { print B $a; }

  close(A);
  close(B);

  copyAndErase($filename);

  print "OK, saved.\n";
  if (!$youWon) { printdeck(0); }
}

sub loadDeck
{
  my $filename;
  if ($#_ > -1) { if ($_[0] =~ /debug/) { $filename = "al.txt"; printNoTest("DEBUG test\n"); } else { $filename="al-sav.txt"; } }
  chomp($_[0]);
  my $search = $_[0]; $search =~ s/^[lt]/s/gi;
  open(A, "$filename") || do { print "Can't find $filename, bailing\n"; return; };
  my $li = 0;
  my @temp;
  my @testArray;
  my @reconArray;
  my $loadFuzzy = 0;
  my $overrideLoadIgnore = 0;
  if ($_[1]) { $loadFuzzy = 1; }

  my $loadIgnore = $ignoreBoardOnSave;
  my $prefix = $_[0]; $prefix =~ s/=.*//g;
  if ($prefix =~ /i/) { $loadIgnore = 1; }
  if ($prefix =~ /b/) { $loadIgnore = 0; $overrideLoadIgnore = 1; }

  my $q = <A>; chomp($q); my @opts = split(/,/, $q); if ($opts[0] > 1) { $startWith = $opts[0]; } $vertical = $opts[1]; $collapse = $opts[2]; $autoOnes = $opts[3]; $beginOnes = $opts[4]; $autoOneSafe = $opts[5]; $sinceLast = $opts[6]; if (!$easyDefault) { $easyDefault = $opts[7]; } $autoOneFull = $opts[8]; # read in default values
  my $hidRow = 0;

  while ($a = <A>)
  {
    $li++;
    chomp($a);
	$fixedDeckOpt = 0;
	my $rowsRead = 0;
	my $ignoreThis = 0;
	if ($a =~ /;$/) { last; }
    if (("$a" eq "$search") || ($loadFuzzy && ($a =~ /$search/i)))
	{
	printNoTest("Found $search in $filename, line $li.\n");
	$lastSearchCmd = $a;
	$a = <A>; chomp($a); $a = lc($a); @temp = split(/,/, $a); $vertical = $temp[0]; $collapse = $temp[1];
	#topCards line
    $hidCards = 0;
   $cardsInPlay = 0; $drawsLeft = 5;
    for (1..52) { $inStack{$_} = 1; }
	while ($rowsRead < 6)
	{
	  $a = <A>;
	  if (!defined($a) || ($a =~ /^s=/i))
	  {
	    print "File ended before read was complete. Hopefully, that just means " . (6-$rowsRead) . " empty row" . plur(6-$rowsRead) . ".\n"; for my $j ($rowsRead+1..6) { @{$stack[$j]} = (); }
		last;
	  }
	  chomp($a); $a = lc($a);
	  $b = $a; $b =~ s/^[a-z]+=//gi; #b = the data for a
	  printDebug("Trying $a\n");
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
	  if ($a =~ /^h=/i)
	  {
		my @tempAry = split(/,/, $b);
		for my $holdEl (@tempAry) { if ($holdEl) { $holds{$holdEl} = 1; $inStack{$holdEl} = 0; } }
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
		${backupCardUnder[$hidRow]} = split(/,/, $b);
		${cardUnder[$hidRow]} = split(/,/, $b);
		next;
	  }
	  if (($a =~ /^ignore/) && (!$overrideLoadIgnore)) { $ignoreThis = 1; }
	  if (($a !~ /m=/i) && ($a =~ /[a-z]/) && ($a =~ /=/)) { print "Unknown command in save-file. Skipping $a.\n"; next; }
	  $rowsRead++;
	  if ($ignoreThis) { $undo = 1; reinitBoard(); for my $saveCmd (@undoArray) { procCmd($saveCmd); print "$saveCmd\n"; } $undo = 0; last; }
	  else
	  {
	  %holds = ();
	  @holdAry = ();
	  my @loadedArray = split(/,/, $a); # here we read in an array and process it for 3-7, etc., but initialize everything first of course
	  my $loadedIndex = 0;
	  my $outIndex = 0;
	    @{$stack[$rowsRead]} = ();
	    for (0..$#loadedArray)
		{
		if ($loadedArray[$loadedIndex] =~ /.[-=]/)
		{
		  my @fromTo = split(/[-=]/, $loadedArray[$loadedIndex]); my $upper = revCard($fromTo[0]); my $lower = revCard($fromTo[1]);
		  my $temp;
		  #print "$fromTo[0] $upper <-> $fromTo[1] $lower\n";
		  if (($lower < 0) || ($upper > 52)) { print "Uh oh bad bail, lower = $lower, upper = $upper in @fromTo.\n"; close(A); return; }
		  if (suit($lower) != suit($upper)) { print "Uh oh suits are wrong, $fromTo[0] vs $fromTo[1].\n"; close(A); return; }
		  if ($lower > $upper) { $temp = $lower; $lower = $upper; $upper = $temp; }
		  for ($temp = $upper; $temp >= $lower; $temp--) { $stack[$rowsRead][$outIndex] = $temp; $outIndex++; delete ($inStack{$temp}); }
		  $loadedIndex++;
		}
		elsif ($loadedArray[$loadedIndex] =~ /[cdhs]$/i) { $stack[$rowsRead][$outIndex] = revCard($loadedArray[$loadedIndex]); $loadedIndex++; $outIndex++; }
		else { $stack[$rowsRead][$outIndex] = $loadedArray[$loadedIndex]; $loadedIndex++; $outIndex++; }
		}
		#print "$rowsRead: @{$stack[$rowsRead]}\n";
	    for my $card (@{$stack[$rowsRead]})
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
	}
	if ($#testArray > -1)
	{
      @undoArray = ();
	  $testing = 1;
	  my $quietMove = 1;
	  my $errs = 0;
	  my $expVal = 0;
	  for (0..$#testArray)
	  {
	    if ($testArray[$_] =~ /=/)
		{
		  my @q = split(/=/, $testArray[$_]);
		  my @r = split(/-/, $q[0]);
		  $expVal = $stack[$r[0]][$r[1]];
		  printDebug("$expVal at $r[0] $r[1]\n");
		  if ($expVal >= 0)
		  {
		    if ($q[1] != $expVal) { $errs++; print "$search: $r[0],$r[1] should be $q[1] but is $expVal.\n"; }
			else
			{
			  printDebug("$search: $r[0],$r[1] should be $expVal and is.\n");
			}
		  }
		  else
		  {
		    $expVal = 0 - $expVal;
		    if ($q[1] == $expVal) { $errs++; print "$search: $r[0],$r[1] should not be $expVal but is.\n"; }
			else
			{
			  printDebug("$search: $r[0],$r[1] should not be $expVal and isn't.\n");
			}
		  }
    } else { procCmd($testArray[$_]); }
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
    $currentlyLoadingSaving = 1; # this is a hack and I can do better. But...if we don't see
	printdeck(0);
	if (!$avoidWin) { checkwin(); }
	close(A);
	$undidOrLoadThisTurn = 1;
	return;
	}
  }

  print "No $search found in $filename.\n";
}

sub printUndoArray
{
  if ($debug) { for my $z (0..$#undoArray+1) { print "$z=$undoArray[$z], "; } print "\n"; }
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
  for my $t (@tests)
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

  if ($_[0] !~ /^(k|q|j|a|10|9|8|7|6|5|4|3|2|1)[cdhs]$/i) { return -1; } # invalid

  my $last = $lc0; $last =~ s/.*(.)/$1/g;
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

sub printHoldArray
{
  if (keys %holds == 0) { print "No holds.\n"; return; }
  print "Holds:";
  for my $x (sort { $a <=> $b } keys %holds) { print " " . faceval($x); }
  print "\n";
  if ($_[0] == 0) { return; }
  print "InStack:";
  for my $x (sort { $a <=> $b } keys %inStack) { print " " . faceval($x); }
  print "\n";
}

sub holdArray
{
    my $card = $_[0]; $card =~ s/^(ho|ho\=|b|b\=)//g; $card =~ s/\(.*//g;
	if (!$card) { print "Need argument for card to hold.\n"; return; }
	my $cardNum = revCard($card);
	if (revCard($card) != -1) { $cardNum = revCard($card); }
	printDebug("$card card $cardNum card num\n");
	if (($cardNum > 52) || ($cardNum < 1)) { print "Need to input (A,2-9,JQK)(CDHS) or a number from 1 to 52, 1=clubs, 14=diamonds, 27=hearts, 40=spades."; }
	my $cardTxt = faceval($cardNum);
	for my $q (@force) { if ($cardNum == $q) { print "$cardTxt already in force array.\n"; return; } }
	if (keys %inStack == 0) { print "Can't hold any more cards.\n"; }
	if ((!$inStack{$cardNum}) && (!$holds{$cardNum})) { print "$cardNum not in stack or holds.\n"; return; }
	if ($holds{$cardNum})
	{
	  print "Removing $cardTxt from holds.\n"; delete($holds{$cardNum}); $inStack{$cardNum} = 1;
	  for my $idx (0..$#holdAry) { if ($holdAry[$idx] == $cardNum) { splice(@holdAry,$idx,1); last; } }
	}
	else
	{ $holds{$cardNum} = 1; delete($inStack{$cardNum}); if (!$undo) { print "Adding $cardTxt to holds.\n"; push(@undoArray, "b$cardNum"); } push(@holdAry, $cardNum); }
}

sub forceArray
{
    my $card = $_[0]; $card =~ s/^f(=?)//gi; $card =~ s/\(.*//g;
	my $cardNum = $card;

	if ((!$undo) && ($cardsInPlay == 52)) { print "Too many cards out.\n"; return; }

	if ($card eq "0") { push(@force, $card); print "Forcing null, which is usually just for testing purposes.\n"; return; }
	if ($card =~ /[cdhs]/i)
	{
	  if (revCard($card) == -1) { print "Bad number value for card $card. (KQJA/1-10)(CDHS) is needed.\n"; return; }
	  $cardNum = revCard($card);
	}
	elsif ($card eq "") { print "Empty value for forcing the move.\n"; return; }
	elsif ($card =~ /[^0-9]/) { print "You need to put in a numerical or card value. $card can't be evaluated.\n"; return; }
	if (($cardNum <= 52) && ($cardNum >= 1))
	{
	if ($holds{$cardNum}) { print "$card (" . faceval($cardNum) . ") being held to the end.\n"; return; }
	if (!$inStack{$cardNum}) { print "$card (" . faceval($cardNum) . ") already out on the board or in the force queue.\n"; return; }
	push (@force, $cardNum); delete ($inStack{$cardNum}); if ((!$undo) && (!$quickMove)) { print faceval($cardNum) . " successfully pushed.\n"; }
	return;
	}

	for my $su (0..$#sui)
	{
	  if ($cardNum =~ /$su/)
	  {
	    my $dumpVal = 13 * $_; $cardNum =~ s/$su//g;
		for my $fv (0..$#vals) { if ($cardNum =~ /$fv/) { $dumpVal += ($fv + 1); print "$_[0] successfully pushed.\n"; return; } }
	  }
	}
  print "Card must be of the form [A23456789 10 JQK][CDHS], or the matching number.\nFace value = C=0 D=13 H=26 S=39.\n";
  return;
}

sub fillRandInitArray # anything in a row, but of course QH-KH-AD-2D-3D-4D needs to be DQ'd
{
  my $baseVal = 1 + rand(8);
  my $baseCard = rand(4) * 13 + $baseVal;
  #printDebug("$baseCard.." . $baseCard+5 . "\n");
  my $fillString = sprintf("%d,%d,%d,%d,%d,%d", $baseCard, $baseCard+1, $baseCard+2, $baseCard+3, $baseCard+4, $baseCard+5);
  fillInitArray($fillString);
}

sub fillInitArray
{
  my @cards = split(/,/, $_[0]);
  for (0..$#cards)
  {
    my $this = $cards[$_];
    if ($this =~ /^[0-9]+/) { if (($this > 52) || ($this < 1)) { die ("Entry $_, $this, is not 1-52.\n"); } }
	else
	{
	if (revCard($this) == -1) { die ("Entry $_, $this, is not a valid card format.\n"); }
	$cards[$_] = revCard($this);
	}
  }
  if ($#cards > 6)
  {
    print "Too many in the initial array.\n";
	splice(@cards, 6, $#cards-5);
  }
  @initArray = @cards;
}

sub initGame
{

printDebug("init'ing game\n");

my $forced = 0;

$undidOrLoadThisTurn = 0;
$printedThisTurn = 0;

$anyMovesYet = 0;

@pointsArray = ();

%holds = ();

if ($usrInit) { @force = @initArray; $forced = 1; }
elsif ($easyDefault == 1) { @force = (8, 9, 10, 11, 12, 13); $forced = 1; }
elsif ($easyDefault == 2) { fillRandInitArray(); @force = @initArray; $forced = 1; }
elsif ($#initArray == -1) { @force = (); } else { @force = @initArray; $forced = 1; }

my $deckTry = 0;
my $thisStartMoves = 0;

do
{

@outSinceLast = ();

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

my @suitCard = (0,0,0,0,0);

for (1..6)
{
  $suitCard[suit($topCard[$_])]++;
}

for (1..4)
{
  if ($suitCard[$_] > 1) { $thisStartMoves += ($suitCard[$_] - 1); }
}

for my $x (1..6)
{
  for my $y(1..6)
  {
    if ($topCard[$x] - $topCard[$y] == 1) { $thisStartMoves++; }
  }
}

$deckTry++;
#print "$deckTry: $thisStartMoves vs $startWith, @topCard, suits @suitcard\n";

} while ((!$undo) && ($thisStartMoves < $startWith) && (!$forced));

deckFix();

if ($forced) { print "You start with $thisStartMoves 'points'.\n"; }
elsif ($startWith > 2) { print "Succeeded on try $deckTry, starting with $thisStartMoves 'points'.\n"; }

@initArray = ();

if (($autoOnes) || ($beginOnes) || ($autoOneSafe))
{
  $moveBar = 0; ones(0); $anyMovesYet = 0;
  if ($#undoArray > 1) { splice(@undoArray, 0, 0, "n+"); push(@undoArray, "n-");  }
}

}

sub drawSix
{
if ($drawsLeft == 0) { print "Can't draw any more!\n"; return; }
if ($drawsLeft != 6)
{
  $anyMovesYet = 1;
  my @q = breakScore(); push (@pointsArray, $q[0] . "/" . $q[1]); } # this is the initial draw so it can't count as a move.
for (1..6)
{
  if ($fixedDeckOpt)
  {
  push(@{$stack[$_]}, $fixedDeck[0]);
  shift(@fixedDeck);
  }
  else
  {
  my $thiscard = randcard();
  push (@{$stack[$_]}, $thiscard);
  if ((!$undo) && ($drawsLeft < 6)) { push(@undoArray, "f$thiscard(" . faceval($thiscard) . ")" ); }
  }
  if ($drawsLeft == 6) { $topCard[$_] = $stack[$_][$#{$stack[$_]}]; }
}
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
  my $rand;
  while (($#force > -1) && ($force[0] eq "0")) { shift(@force); }
  if (defined($force[0])) { $rand = $force[0]; shift(@force); delete $inStack{$rand}; }
  else
  {
  #print (keys %inStack) . " in stack, " . (keys %holds) . " in holds.\n";
  my $q;
  if ($debug)
  {
  print "Stack:";
  foreach $q (keys %inStack) { print " $q"; }
  print " Holds:";
  foreach $q (keys %holds) { print " $q"; }
  print "\n";
  }
  if ((keys %inStack) > 0)
  {
  $rand = (keys %inStack)[rand keys %inStack];
  delete $inStack{$rand};
  }
  else
  {
  if (defined($holdAry[0]))
  {
  $rand = $holdAry[0];
  print "Deleting specific $rand\n";
  shift(@holdAry);
  }
  else
  {
  print "Deleting random $rand\n";
  $rand = (keys %holds)[rand keys %holds];
  }
  delete $holds{$rand};
  }
  }
  printDebug("Returning $rand. Left: " . (keys %inStack) . ", " . (keys %holds) . " holds.\n");
  $errorPrintedYet = 1; # we have already made a successful move to get this to reveal, or we are just drawing. Anything else is okay. Drawing a card we sweep up later can throw misc errors
  push(@outSinceLast, $rand);
  return $rand;
}

sub faceval
{
  if ($_[0] == -1) { return "**"; }
  if ($_[0] == -3) { return "**"; }
  my $x = $_[0] - 1;
  my $suit = @sui[$x/13+1];
  return "$vals[$x%13]$suit";
}

sub printdeckforce
{
  my $testold = $testing;
  my $undoold = $undo;
  my $qmold = $quickMove;
  $undo = $testing = $quickMove = 0;
  print "============start force print deck\n";
  printdeck(0);
  print "============end force print deck\n";
  $quickMove = $qmold;
  $undo = $undoold;
  $testing = $testold;
}

sub ping
{
  if ($debug) { print("PING debug\n"); }
}

sub printDebugAnyway
{
  if ($debug) { printAnyway(); }
}

sub printAnyway
{
  my $qm = $quickMove;
  my $ud = $undo;
  my $te = $testing;
  $testing = 0; $undo = 0; $quickMove = 0;

  $printedThisTurn = 0;
  printdeck(0);
  $printedThisTurn = 0;
  $quickMove = $qm;
  $undo = $ud;
  $testing = $te;
}

sub printdeck #-1 means don't print the ones and also it avoids the ones-ish getting rid of the n- at the end
{
  if ($testing) { return; }
  if ($undo) { return; }
  if ($quickMove) { return; }
  if ($stillNeedWin) { ones(0); checkwin(); return; }
  if (($autoOneSafe) && ($_[0] != -1) && ($anyMovesYet)) { ones(0); } # there has to be a better way to do this
  if ($printedThisTurn) { print "Warning tried to print this turn.\n"; return; }
  $printedThisTurn = 1;
  if (!$anyMovesYet) { print "========NO MANUAL MOVES MADE YET========\n"; }
  if ($vertical)
  { printdeckvertical(); }
  else
  { printdeckhorizontal(); }
}

sub printdeckhorizontal
{
  my $anyJumps = 0;
  for my $d (1..6) { $anyJumps += jumpsFromBottom($d); }
  my @rowLength = ();

  for my $d (1..6)
  {
    my $thisLine = "$d";
	if ($#{$stack[$d]} == -1) { $thisLine .= "E"; } elsif (ascending($d)) { $thisLine .= ">"; } else { $thisLine .= ":"; }
	if (($anyJumps > 0) && ($chainBreaks))
	{
	  my $temp = jumpsFromBottom($d);
	  if ($temp) { $thisLine = "($temp) $thisLine"; } else { $thisLine = "    $thisLine"; }
	}
    for my $q (0..$#{$stack[$d]})
	{
	my $t1 = $stack[$d][$q];
	if (!$t1) { last; }
	my $t2 = $stack[$d][$q-1];
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
	if ($showMaxRows) { my $tlt = $thisLine; $tlt =~ s/^[0-9]: //g; my @tmpArray = split(/[=\-: ]/, $tlt); $rowLength[$d] = $#tmpArray + 1; }
	if ($thisLine =~ /[CDHS]/) { $rowLength[$_]++; }
	print "$thisLine\n";
  }
  if ($showMaxRows)
  {
    my $maxRows = 0;
	for (1..6) { if ($rowLength[$_] > $maxRows) { $maxRows = $rowLength[$_]; } }
	print "($maxRows max row length) ";
  }
  showLegalsAndStats();
}

sub printdeckraw
{
  for my $d (1..6)
  {
    print "$d: ";
    for my $q (0..$#{$stack[$d]}) { if ($stack[$d][$q]) { print faceval($stack[$d][$q]) . " "; } }
	print "\n";
  }
  showLegalsAndStats();
  print "Left: "; for my $j (sort { $a <=> $b } keys %inStack) { print " $j"; } print "\n";

  print "$cardsInPlay cards in play, $drawsLeft draw" . plur($drawsLeft) . " left.\n";
}

sub jumpsFromBottom
{
    my $thisdif = 0;
    for (my $thisone = $#{$stack[$_[0]]}; $thisone >= 1; $thisone--  )
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
  for my $row (1..6)
  {
    if ($temp = jumpsFromBottom($row)) { $myString .= "  ($temp)"; } else { $myString .= "     "; }
    $lookAhead[$row] = 0;
  }
  if ($myString =~ /[0-9]/) { print "$myString\n"; }
  }
  for my $row (1..6)
  {
    print "   ";
	if ($#{$stack[$row]} == -1) { print "!"; } elsif (ascending($row)) { print "^"; } elsif (onesuit($row)) { print "%"; } else { print " "; }
	print "$row";
  }
  print "\n";
  my $foundCard;
  do
  {
  $foundCard = 0;
  my $thisLine = "";
  for my $row (1..6)
  {
    if ($stack[$row][$deckPos[$row]])
	{
	$thisLine .= " ";
	$foundCard = 1;
	#if ($stack[$row][$deckPos[$row]] % 13 != 10) { $thisLine .= " "; }
	if ($collapse)
	{
	if ($lookAhead[$row])
	{
	my $eq = 0;
	while(($deckPos[$row] < $#{$stack[$row]}) && (($stack[$row][$deckPos[$row]] - $stack[$row][$deckPos[$row]+1]) == 1) && ($stack[$row][$deckPos[$row] +1] % 13)) { $deckPos[$row]++; $eq = 1; }
	if ($stack[$row][$deckPos[$row]] % 13 != 10) { $thisLine .= " "; }
	if ($eq) { $thisLine .= "="; } else { $thisLine .= "-"; }
	$thisLine .= faceval($stack[$row][$deckPos[$row]], 1);
	$lookAhead[$row] = 0;
	$eq = 0;
	}
	else
	{
	if ($stack[$row][$deckPos[$row]] % 13 != 10) { $thisLine .= " "; }
	$thisLine .= " " . faceval($stack[$row][$deckPos[$row]], 1);
	}
	if ($deckPos[$row] < $#{$stack[$row]})
	{
	if ((($stack[$row][$deckPos[$row]] - $stack[$row][$deckPos[$row]+1]) == 1) && ($stack[$row][$deckPos[$row] +1] % 13))
	{
	  $lookAhead[$row] = 1;
	  #print "$row: $stack[$row][$deckPos[$row]] to $stack[$row][$deckPos[$row]+1]: DING!\n";
	}
	}
	$deckPos[$row]++;
	}
	else
	{
	if ($stack[$row][$deckPos[$row]] % 13 != 10) { $thisLine .= " "; }
	$thisLine .= " " . faceval($stack[$row][$deckPos[$row]], 1);
	$deckPos[$row]++;
	}
	}
	else { $thisLine .= "     "; }
  }
  if ($foundCard) { print "$thisLine\n"; $maxRows++; }
  } while ($foundCard);
  if ($showMaxRows)
  {
    print "($maxRows max row length) ";
  }
  showLegalsAndStats();
}

sub showLegalsAndStats
{
  if (($undo) || ($quickMove)) { return; }
  my @idx;
  my @blank = (0,0,0,0,0,0,0);
  my @circulars = (0,0,0,0,0,0,0);
  my $canMakeEmpty = 0;
  my $allBalanced = 0;
  $mbGood = "";
  my $curEl;
  my $thisEl;

  for my $d(1..6)
  {
    $curEl = 0;
    while ($stack[$d][$curEl]) { $curEl++; }
	$idx[$d] = $curEl - 1;
	if ($idx[$d] < 0) { $blank[$d] = 1; $idx[$d] = 0; }
  }
  #for $thi (0..5) { print "Stack $thi ($idx[$thi]): $stack[$thi][$idx[$thi]]\n"; }
  $anySpecial = 0;
  print "Legal moves:";
  my $legal = "";
  my $recc = "";
  my $moveStr = "";
  for my $from (1..6)
  {
    for my $to (1..6)
	{
	  $moveStr = "";
	  my $recThis = 0;
	  if ($from == $to) { next; }
	  elsif ($blank[$to] == 1) { }
	  elsif (($#{$stack[$from]} != -1) && (cromu($stack[$from][$idx[$from]], $stack[$to][$idx[$to]])))
	  {
	    $thisEl = $idx[$from];
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
		  $moveStr .= "*"; $circulars[$to]++;
		  if (($stack[$from][$thisEl-1] % 13 == 1) && ($stack[$from][$thisEl] % 13 == 0) && ($thisEl % 13 == 0)) {} else { $anySpecial = 1; } # e.g KH=AH then KD is okay
		  }
		elsif (($stack[$from][$thisEl-1] < $stack[$from][$thisEl]) && ($stack[$from][$thisEl-1] != -1))
		  {
		  $moveStr .= "<"; $anySpecial = 1;
		  }
		}
		else
		{
		  $moveStr .= "E"; $canMakeEmpty = 1; $recThis = 1;
		}
		if (suit($stack[$from][$thisEl-1]) == suit($stack[$from][$thisEl]))
		{
		  if (suit($stack[$from][$thisEl]) == suit($stack[$to][$idx[$to]]))
		  {
		    if (($stack[$from][$thisEl] < $stack[$to][$idx[$to]]) && ($stack[$from][$thisEl] < $stack[$from][$thisEl-1]))
			{
			  $moveStr .= "C"; $circulars[$to]++;
			}
		  }
		}
		$moveStr = " $moveStr$from$to";
		if (($stack[$from][$thisEl] == $stack[$to][$idx[$to]] - 1) && ($stack[$from][$thisEl] % 13)) { $recThis = 1; $moveStr = "$moveStr+"; $anySpecial = 1; $mbGood = "$from$to"; }
		if ($recThis) { $recc .= $moveStr; } else { $legal .= $moveStr; }
	  }
	  if (!$stack[$to][0] && $stack[$from][0])
	  {
	    $legal .= " $from$to" . "e";
		if (!$emptyIgnore)
		{
		  if (!ascending($from)) { $anySpecial = 1; }
		}
	  }
	} #?? maybe if there is no descending, we can check for that and give a pass
  }
  if ($recc) { print "$recc"; }
  if ($recc && $legal) { print " |"; }
  print "$legal";
  for my $toPile (1..6) { if ($circulars[$toPile] > 1) { $anySpecial = 1; print " " . ('X' x ($circulars[$toPile]-1)) . "$toPile"; } }
  if (allAscending() && ($drawsLeft) && (emptyRows() < 2))
  {
    my $foundDup = 0; my $otherDup = 0; my $gotOne = 0;
    if (emptyRows() == 0)
	{
	  for my $i (1..6)
	  {
		if (isEmpty($i)) { next; }
	    for my $j ($i+1..6)
		{
		  if (($i == $j) || ($gotOne)) { next; }
		  if (suit($stack[$i][0]) == suit($stack[$j][0])) { if (!$foundDup) { $foundDup = $i; $otherDup = $j; } elsif ($foundDup == $i) { print " (3 of a kind, you can merge)"; $gotOne = 1; } }
		}
	  }
	  if ($gotOne && $foundDup) { print " (close, but merge $foundDup/$otherDup?)"; }
	  else { print " (recommend drawing)"; }
	}
	else
	{
	  for my $i (1..6)
	  {
		if (isEmpty($i)) { next; }
	    for my $j ($i+1..6)
		{
		  if (isEmpty($j)) { next; }
		  if (($i == $j) || ($gotOne)) { next; }
		  if (suit($stack[$i][0]) == suit($stack[$j][0])) { if (!$foundDup) { print " (close, but merge $i/$j?)"; $foundDup = $i; } $gotOne = 1; }
		}
	  }
	  if (!$gotOne) { print " (recommend drawing)"; }
	}
  }
  elsif ((!$anySpecial) && ($drawsLeft) && (!$canMakeEmpty))
  {
    print " (recommend drawing)";
  }
  elsif ($drawsLeft)
  {
    my $recDraw = 1;
    for my $q (1..6) { if (!ascending($q)) { $recDraw = 0; } }
	if ($recDraw)
	{
	  if (oneRowPerSuit()) { print " (you're clear to draw)"; } else { print " (almost clear to draw)"; }
	}
	elsif (emptyRows())
	{
	  my $fixYet = 0;
	  for my $q (1..6) { if (!ascending($q)) { if ($fixYet) { print "/$q"; } else { print " (maybe fix $q"; $fixYet = 1; } } }
	  if ($fixYet) { print ")"; }
	}
  }
  print "\n";

  my $chains = 0; my $order = 0;
  for my $col (1..6)
  {
    my $entry = 1;
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
    for my $row (1..6)
	{
	  for my $card (1..$#{$stack[$row]})
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
	 if (($gotEmpty) || ($canMakeEmpty)) { if ($chains != 48) { print "You can still create an empty slot.\n"; } } else { print "You don't have any productive moves left. This position looks lost, unless you wish to UNDO.\n"; }
  }

  if ($chains != 48) # that means a win, no need to print stats
  {
  printOutSinceLast();
  my ($brkPoint , $brkFull, $breaks) = breakScore();
  my $visible = $cardsInPlay - $hidCards;
  @outSinceLast = (); #need to clear anyway and if it's toggled mid-game...
  print "$cardsInPlay cards in play";
  my $allOut = "";
  my @cardCount = (0,0,0,0);
  for (1..4)
  {
    my $thisDone = 1;
    for my $idx($_ * 13 - 12 .. $_ * 13)
	{
	  if ($inStack{$idx} || $holds{$idx}) { $thisDone = 0; } else { $cardCount[($idx-1)/13]++; }
	}
	if ($thisDone) { $allOut .= $sui[$_]; }
  }
  my $vis = join("-", @cardCount);
  if (($allOut) && ($visible < 52)) { print "($allOut out)"; }
  print ", $visible($vis)/$hidCards visible/hidden.\n$drawsLeft draw" . plur($drawsLeft) . " left, $chains chain" . plur($chains) . ", $order in order, $breaks break" . plur($breaks) . ", $brkFull($brkPoint) break-remaining score.\n";
  }
}

sub breakScore
{
  my $brkPoint = 0;
  my $visible = $cardsInPlay - $hidCards;
  my $breaks = 0;
  for my $breakRow (1..6)
  {
    my $consecutives = 0;
    #we deserve credit for an empty row, but how much?
    if (($#{$stack[$breakRow]} > -1) && ($stack[$breakRow][0] > 0))
	{
	  $brkPoint++;
	}
    for (0..$#{$stack[$breakRow]} - 1)
	{
	  if ($stack[$breakRow][$_] != -1)
	  {
	    if (($stack[$breakRow][$_] - $stack[$breakRow][$_+1] != 1) || (suit($stack[$breakRow][$_]) != suit($stack[$breakRow][$_+1])))
		{
		  $consecutives = 0;
		  $breaks++;
		  if (suit($stack[$breakRow][$_]) == suit($stack[$breakRow][$_+1]))
		  {
		    if ($stack[$breakRow][$_] < $stack[$breakRow][$_+1]) { $brkPoint += 2; } else { $brkPoint += 1; }
		  }
		  else { $brkPoint += 3; }
		}
		else { $consecutives++; if ($consecutives == 12) { $brkPoint--; } if ($consecutives > 11) { printDebug("$consecutives consecutives.\n"); } }
	  }
	  else { $brkPoint += 4; }
	}
  }
  return ($brkPoint, $brkPoint + 24 * $drawsLeft, $breaks);
}

sub printOutSinceLast
{
  if (($#outSinceLast != -1) && $sinceLast)
  {
    print "(";
	for (0..$#outSinceLast) { if ($_ > 0) { print ", "; } print faceval($outSinceLast[$_]); }
	print " out since last)\n";
  }
}

sub oneRowPerSuit
{
  my @q = (0, 0, 0, 0, 0);
  my $st;
  my $ind;
  for my $st (1..6)
  {
    for my $ind (0..$#{$stack[$st]})
	{
	  my $temp = suit($stack[$st][$ind]);
	  if (($q[$temp] > 0) && ($q[$temp] != $st)) { return 0; }
	  $q[$temp] = $st;
	}
  }
  return 1;
}

sub allAscending
{
  for my $i (1..6)
  {
    if (!ascending($i)) { return 0; }
  }
  return 1;
}

sub onesuit
{
  my $size = $#{$stack[$_[0]]};
  if ($size == -1) { return 0; }
  if ($size == 0) { return 1; }
  my $mainSuit = suit($stack[$_[0]][0]);
  for my $x (1..$size)
  {
   if (suit($stack[$_[0]][$x]) != $mainSuit) { return 0; }
  }
  return 1;
}

sub ascending
{
  my $extra = 0;
  if ($#{$stack[$_[0]]} == -1) { return 1; } #empty stack ok
  if ($stack[$_[0]][0] == -1) { return 0; } #still to draw not OK
  my $lower, my $upper;
  for (1..$#{$stack[$_[0]]})
  {
    $lower = $stack[$_[0]][$_];
    $upper = $stack[$_[0]][$_-1];
	if (suit($lower) != suit($upper))
	{
	  printDebug("b4 $_: $lower vs $upper\n");
	  if (($_ % 13 == 0) && ($lower % 13 == 0) && ($upper % 13 == 1)) { $extra = 1; } else { return 0; } # very special case KC=AC KH-etc.
	  printDebug("a $_: $lower vs $upper\n");
	}
    elsif ($stack[$_[0]][$_] > $stack[$_[0]][$_-1]) { return 0; }
  }
  return 1 + $extra;
}

sub suit
{
  if (!defined($_[0])) { return -1; }
  if (($#_ == -1) || ($_[0] == -1)) { return -1; }
  return ($_[0]+12) / 13;
}

sub cromu
{
  if (!defined($_[0])) { return 0; }
  if ($#_ < 1) { return 0; }
  #my $trace = Devel::StackTrace->new; print $trace->as_string . "\n";
  if ($_[0] >= $_[1]) { return 0; }
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
  if ($#_ < 1) { print "Oops, don't have a to-row"; if ($#_ == 0) { print " for $_[0]"; } else { print " or from-row"; } print ".\n"; return; }
  my $from = $_[0];
  my $to = $_[1];

  if ($moveBar == 1) { if ($showBlockedMoves) { barMove("$from-$to blocked, as previous move failed.\n"); } else { $blockedMoves++; } return; }

  if (($from > 6) || ($from < 1) || ($to > 6) || ($to < 1)) { barMove("$from-$to is not valid. Rows range from 1 to 6.\n"); return; }

  if ($from==$to) { barMove("Oops, tried to switch a row with itself.\n"); return; }

  if (!$stack[$from][0]) { barMove("Tried to move from empty row/column.\n"); return; } # note: this needs a better error message.

  #print("$_[0] to $_[1]\n");
  #my $trace = Devel::StackTrace->new; print $trace->as_string . "\n";

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
	  if ($undo) { print "WARNING: bad move tried during redo. Type UL for details.\n"; if ($stillNeedWin) { print "Bailing because the undo array appears corrupted.\n"; } $stillNeedWin = 0; }
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
  my $toCard = -1;
  if (!isEmpty($to)) { $toCard = $stack[$to][$toEl]; }
  my $fromCard = $stack[$from][$fromEl];

  while ($stack[$from][$fromEl])
  {
  push (@{$stack[$to]}, $stack[$from][$fromEl]);
  splice (@{$stack[$from]}, $fromEl, 1);
  }
  if (!isEmpty($from) && ($stack[$from][0] == -1)) #see about turning a card over
  {
    my $fromLook = 0;
	my $maxEnt = $#{$stack[$from]};
	while (($fromLook <= $maxEnt) && ($stack[$from][$fromLook] == -1)) { $fromLook++; }
	if ($fromLook > $maxEnt)
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
  if (($#_ == 0) || ($_[1] != -1)) { if ($toCard - $fromCard != 1) { $anyMovesYet = 1; } }
  if (!$undo)
  {
    push(@undoArray, "$from$to");
  } #-1 means that we are in the "ones" subroutine so it is not a player-move

  printdeck(0);
  checkwin();
}

sub altUntil
{
  my @cmds = split(//, $_[0]);
  my $from = $cmds[0];
  my $to = $cmds[1];
  my $totalMoves = 0;
  if (($from < 1) || ($from > 6) || ($to < 1) || ($to > 6)) { print "From/to must be between 1 and 6.\n"; }
  #print "$from$to trying\n";
  if (!canChain($from,$to) && !canChain($to, $from)) #do we need this
  {
    #if (canChain($to, $from)) { $temp = $from; $from = $to; $to = $temp; }
	$errorPrintedYet = 1;
	if (canMove($from,$to) || canMove($from,$to)) { print "You can move between $from and $to, but you can't alternate. Maybe use w or y to force things.\n"; return; }
	print "Rows $from and $to aren't switchable.\n"; return;
  }
  $quickMove = 1;
  #print "$to$from trying\n";
  while (canChain($from, $to, $totalMoves) || canChain($to, $from, $totalMoves))
  {
    if (canChain($from, $to))
	{
    tryMove("$from", "$to"); #print "$to$from trying\n";
	}
	else
	{
    tryMove("$to", "$from"); #print "$to$from trying\n";
	}
	if ($quickMove == 0) { return; } # this means you won
    if ($moveBar == 1) { print "Move was blocked. This should never happen.\n"; last; }
	#$temp = $from; $from = $to; $to = $temp;
	$totalMoves++;
  }
  $quickMove = 0;
  printdeck(0);
  print "Made $totalMoves moves.\n";
  checkwin();
}

sub canChain
{
  if ($moveBar) { return 0; }
  if ($_[0] == $_[1]) { return 0; }
  my $fromLoc = $#{$stack[$_[0]]};
  my $toLoc = $#{$stack[$_[1]]};
  my $toCard = $stack[$_[1]][$toLoc];
  if (!defined($toCard)) { $toCard = 0; }
  if (($toLoc > -1) && ($toCard % 13 == 1)) { return 0; } # if it is an ace, there's no way we can chain
  if ($fromLoc == -1) { return 0; } # can't move from empty row
  my $fromCard = $stack[$_[0]][$fromLoc];
  if (($toLoc != -1) && (suit($toCard) != suit($fromCard))) { return 0; } #can't move onto a different suit, period. But we can move onto an empty card.
  if (($toCard != 0) && ($toCard < $fromCard)) { return 0; } # and of course smaller must move onto bigger
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
  if ($toLoc == -1) { if (suit($stack[$_[0]][$fromLoc-1]) != suit($stack[$_[0]][$fromLoc])) { if (($_[2] > 0)) { if (emptyRows() < 2) { print "With only 1 empty row, revealing new suit must be done manually e.g. $_[0]$_[1].\n"; return 0; } else { print "u1 if the last flip to an empty column doesn't work.\n"; } } } } # 8H-7C-6C won't jump to unless 2 open
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

sub topCardInSuit
{
  my $temp = $#{$stack[$_[0]]};
  while (($temp > 0) && (suit($stack[$_[0]][$temp]) == suit($stack[$_[0]][$temp]-1)) && ($stack[$_[0]][$temp-1] > $stack[$_[0]][$temp])) { $temp--; }
  return $stack[$_[0]][$temp];
}

sub topPosInSuit
{
  my $temp = $#{$stack[$_[0]]};
  while (($temp > 0) && (suit($stack[$_[0]][$temp]) == suit($stack[$_[0]][$temp-1])) && ($stack[$_[0]][$temp-1] > $stack[$_[0]][$temp]))
  {
    $temp--;
  }
  return $temp;
}

sub suitsAligned
{
  for my $z (0..2)
  { printDebug("Comparing $z to 3: $_[$z] vs $_[3]\n");
    if (($_[$z] != $_[3]) && ($_[$z] != -1)) { return 0; }
  }
  return 1;
}

sub botSuit
{
  return suit(botCard($_[0]));
}

sub botCard
{
  if ($#{$stack[$_[0]]} == -1) { return -1; }
  return $stack[$_[0]][$#{$stack[$_[0]]}];
}

sub firstEmptyRow
{
  my $retVal = 0;
  for my $rv (1..6)
  {
    if ($#{$stack[$rv]} == -1) { return $rv; }
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
  if ($#{$stack[$_[0]]} == -1) { return 1; }
  return 0;
}

sub ascendingOld # sees if we have a fully ascending row
{
  for (0..$#{$stack[$_[0]]} - 1)
  {
    if ($stack[$_[0]][$_] < $stack[$_[0]][$_+1]) { return 0; }
    if (suit($stack[$_[0]][$_]) != suit($stack[$_[0]][$_+1])) { return 0; }
  }
  return 1;
}

sub straightUp # this doesn't say that a row is ascending but rather if it can be swapped
{
  my $max = $stack[$_[0]][0]; # in other words--we expect this row to be the same suit all the way down
  #print "Testing $_[0] to $_[1]\n";
  my $fromH = $#{$stack[$_[0]]};
  if ($fromH == -1) { return 0; }
  my $toH = $#{$stack[$_[1]]};

  my $fromBot = $stack[$_[0]][$fromH];
  my $sui = suit($stack[$_[0]][$fromH]);

  if ($toH == -1)
  {
    for (my $z = $fromH; $z >= 0; $z--)
	{
	  if ($sui != suit($stack[$_[0]][$z])) { return 1; }
	  if ($fromBot > $stack[$_[0]][$z]) { return 1; }
	  if ($z == 0) { return 0; }
	}
    return 1;
  }
  #print "$_[1] has more than 1 item\n";
  my $whatTo = $stack[$_[1]][$#{$stack[$_[1]]}];
  my $suiTo = suit($stack[$_[1]][$#{$stack[$_[1]]}]);

  if ($sui != $suiTo) { return 0; }

  my $temp;
  for (my $z = $fromH; $z >= 0; $z--)
  { # go up the "from" stack and see if the
    $temp = $stack[$_[0]][$z];
    #print "$temp($sui) vs $max vs $whatTo for $_[0] to $_[1]\n";
    if ($temp > $max) { return 0; }
	if (($temp > $whatTo) && ($sui == suit($temp)) && ($fromBot < $whatTo))
	{
	  #$quickMove = 0; printdeck(0); $quickMove = 1; print "Okay $_[0] to $_[1]: $temp > $whatTo and $sui is suit of $temp\n";
	  printDebug("a\n");
	  return 1;
	}
    if ($sui != suit($temp))
	{
	  #print "Bad suit.\n";
	  return 0;
	}
  }
  #print "Okay $_[0] to $_[1]\n";
  printDebug("b\n");
  return 1;
}

sub lowNonChain
{
  my $temp = $#{$stack[$_[0]]};
  if ($temp == -1) { return -1; }
  while ($stack[$_[0]][$temp-1] == $stack[$_[0]][$temp] + 1)
  { $temp--;  if ($temp == 0) { return -1; } }
  return $stack[$_[0]][$temp-1];
}

sub safeShuffle # this tries sane but robust safe shuffling
{
  if ($_[0] == $_[1]) { return -1; }
  if (isEmpty($_[0]) || isEmpty($_[1])) { return -2; }
  if (botSuit($_[0]) != botSuit($_[1])) { return -3; } #no point shuffling onto itself, empty is either risky or useless, and different suits can't work
  #printDebug("Trying $_[0] to $_[1] low-from " . botCard($_[0]) . " " . faceval(botCard($_[0])) . " botsuit " . botSuit($_[0]) . " " . faceval(botSuit($_[0])) . " to " . botCard($_[1]) . " with suit $_[2] @sui($_[2])\n");
  if (botSuit($_[0]) != $_[2]) { return -4; }
  if (botCard($_[0]) > botCard($_[1])) { return -5; }
  if (emptyRows() == 0)
  {
    my $lnc = lowNonChain($_[0]);
	if ((suit($lnc) == botSuit($_[0])) && (lowNonChain($_[0]) > botCard($_[1]))) { printDebug("Cosmetic move $_[0] to $_[1]\n"); return 1; } # qc-ac to 7c but not vice versa
    return -6;
  } # note we can tighten this up later if we have a bit more but for now it's a bit too tricky
  my $topFrom = topCardInSuit($_[0]);
  my $topFromPos = topPosInSuit($_[0]);
  my $lowTo = botCard($_[1]);
  if ($topFromPos == 0)
  {
    printDebug("Top from position = 0\n"); return 1;
  } # empty out a row
  my $breaks = 0;
  my $x = $#{$stack[$_[0]]};
  printDebug("Start at position $x row $_[0] to row $_[1], bottom card " . botCard($_[1]) . "\n");
  while (($x > 0) && (suit($stack[$_[0]][$x-1]) == suit($stack[$_[0]][$x])) && (($stack[$_[0]][$x-1]) > suit($stack[$_[0]][$x])) && (($stack[$_[0]][$x-1]) < botCard($_[1])))
  {
    #printDebug("$x: " . suit($stack[$_[0]][$x-1]) . " $stack[$_[0]][$x-1] vs " . suit($stack[$_[0]][$x]) . " $stack[$_[0]][$x]\n");
    if ($stack[$_[0]][$x-1] - $stack[$_[0]][$x] > 1) { $breaks++; }
	$x--;
  }
  printDebug("$_[0] to $_[1] is a strong candidate\n");
  if ($x == 0) { printDebug("No breaks, returning\n"); return 1; }
  printDebug("boop: $breaks vs " . emptyRows() . "\n");
  if ($breaks > emptyRows() && (!straightUp($_[0], $_[1]))) { return -7; }
  printDebug($stack[$_[0]][$x-1] . " vs " . botCard($_[1]) . " is the question.\n");
  printDebug("$breaks, " . emptyRows() . " empty row" . plur(emptyRows()) . ". $_[0] to $_[1] is OK.\n");
  #printAnyway();
  return 1;
}

sub autoShuffleExt #autoshuffle 0 to 1 via 2, but check if there's a 3rd open if stuff is left on 2
{
  my $i;
  my $j;
  my $didSafeShuffle = 0;
  my $suitToShuf = $_[3];
  if (!$suitToShuf)  { $suitToShuf = botSuit($_[0]); }
  if (!isEmpty($_[1]) && (botSuit($_[0]) != botSuit($_[1]))) { return; }
  printDebug("before autoshuffle: $_[0] to $_[1] via $_[2], cards " . faceval(botCard($_[0])) . " to " . faceval(botCard($_[1])) . " via " . faceval(botCard($_[2])) . "\n");
  autoShuffle($_[0], $_[1], $_[2]);
  printDebug("after autoshuffle\n");
  my $emptyShufRow = firstEmptyRow();
  do
  {
  $didSafeShuffle = 0;
  $emptyShufRow = firstEmptyRow();
  #if ($emptyShufRow == 0) { return; }
  for my $i (1..6)
  {
    for my $j (1..6)
	{
	  #printDebug("Suit to shuffle $i $j is $suitToShuf\n");
	  my $errNum = safeShuffle($i, $j, $suitToShuf);
	  if ($errNum ==1)
	  {
	    #if ($debug) { printAnyway(); }
		$moveBar = 0;
	    printDebug ("Safe shuffling $i and $j via $emptyShufRow, suit=$suitToShuf, move bar = $moveBar\n");
	    autoShuffle($i, $j, $emptyShufRow);
		$didSafeShuffle = 1;
        $emptyShufRow = firstEmptyRow();
	  }
	  else
	  {
	    #printDebug("$i to $j failed, error $errNum.\n");
	  }
	}
  }
  } while ($didSafeShuffle);
  return;
  if (isEmpty($_[2]))
  {
    return;
  }
  if (!emptyRows()) { return; }
  my $fer = firstEmptyRow();
  #print straightUp($_[2], $_[1]) . " = $_[2]-$_[1]!\n";
  #print straightUp($_[1], $_[2]) . " = $_[1]-$_[2]!\n";
  $moveBar = 0;
  my $numMoves;
  my $madeAMove;
  do
  {
  $madeAMove = 0;
  my $numMoves = $#undoArray;
  if ((emptyRows == 1) && (straightUp($_[1], $_[2])))
  {
    $madeAMove = 1;
	printDebug("$_[1] to $_[2], $numMoves\n");
    autoShuffle($_[1], $_[2], $fer);
  }
  elsif ((emptyRows == 1) && (straightUp($_[2], $_[1])))
  {
    $madeAMove = 1;
	printDebug("$_[2] to $_[1]\, $numMoves\n");
    autoShuffle($_[2], $_[1], $fer);
  }
  elsif ((emptyRows == 1) && (!straightUp($_[2], $_[1]) || !straightUp($_[1], $_[2])))
  {
    if (!$errorPrintedYet)
	{
	  if (straightUp($_[2], $_[1])) { print "$_[2]$fer$_[1]x is a possibility but I can't prove it's best, so I'll let you decide.\n"; }
	  if (straightUp($_[1], $_[2])) { print "$_[1]$fer$_[2]x is a possibility but I can't prove it's best, so I'll let you decide.\n"; }
	}
	return;
  }
	printdeckraw();
  } while (($madeAMove) && ($numMoves != $#undoArray))
  #printdeckforce();
  #print "First empty row $fer\n";
  #print "Trying $_[1] to $_[2] via $fer.\n";
  #print "Trying $_[2] to $_[1] via $fer.\n";
}

sub endSuit
{
  if ($#{$stack[$_[0]]} == -1) { return -1; }
  return suit($stack[$_[0]][$#{$stack[$_[0]]}]);
}

sub autoShuffle # autoshuffle 0 to 1 via 2
{
  if ($moveBar) { return; }
  #if ((endSuit[$_[0]] != endSuit[$_[1]]) && ($#{$stack[$_[1]]} != -1)) { barMove("To and from must be the same suit.\n"); return; }
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
    if (!$moveBar) { tryMove("$_[0]", "$_[1]"); } return;
  }

  #print "$_[0] to $_[1], then $_[0] to $_[2], then $_[1] to $_[2].\n";
  autoShuffle($_[0], $_[2], $_[1], $count - 1);
  if (!$moveBar)
  {
    tryMove("$_[0]", "$_[1]");
    autoShuffle($_[2], $_[1], $_[0], $count - 1);
  }
}

sub reinitBoard
{
  my @depth = (0, 3, 3, 2, 2, 3, 3);
  $cardsInPlay = 22;
  $drawsLeft = 5;
  $hidCards = 16;
  $anyMovesYet = 0;
  for (1..52) { if (!$holds{$_}) { $inStack{$_} = 1; } }
  for (1..6)
  {
    @{$stack[$_]} = ();
    for my $x (1..$depth[$_]) { push (@{$stack[$_]}, -1); }
	push (@{$stack[$_]}, $topCard[$_]);
	delete($inStack{$topCard[$_]});
  }
  %holds = ();
  @holdAry = ();
}

sub undoToStart
{
  if (!$anyMovesYet) { print "Reshuffling auto-moves if available.\n"; }
  @pointsArray = ();
  reinitBoard();
  @cardUnder = @backupCardUnder;
  @fixedDeck = @oneDeck;
  @undoArray = ();
  printdeck(0);
}

sub undo # 1 = undo # of moves (u1, u2, u3 etc.) specified in $_[1], 2 = undo to last cards-out (ud) 3 = undo last 6-card draw (ud1)
{
  my $tempUndoCmd = "";
  my $lastNMinus = 0;
  $undo = 1; $undidOrLoadThisTurn = 1;
  if ($showUndoBefore) { print "Undo array: @undoArray\n"; }
  if (($_[0] == 2) || ($_[0] ==3)) { if ($cardsInPlay == 22) { print "Note--there were no draws, so you should use us instead.\n"; $undo = 0; return; } }
  if ($_[0] == 2) { if (($undoArray[$#undoArray] eq "n-") && ($undoArray[$#undoArray-1] eq "df")) { print "Already just past a draw.\n"; $undo = 0; return; } }
  if ($undoDebug)
  {
    print "Writing to debug...\n";
    open(B, ">>undo-debug.txt");
	print B "========\n";
	if (keys %holds) { print B "H="; for my $el (sort {$a <=> $b} keys %holds) { print B ",$el"; } print B "\n"; }
	print B "TC=" . join(",", @topCard) . "\n";
	print B "M=" . join (",", @undoArray) . "\n";
	for (1..6) { print B join(",", @{$stack[$_]}); print B "\n"; }
	close(B);
	if (-s "undo-debug.txt" > 100000) { print "WARNING trim undodebug file.\n"; }
  }
  #if ($#undoArray == -1) { print "Nothing to undo.\n"; return;}
  if ($undoArray[$#undoArray] eq "n-") { $lastNMinus = 1; }
  @undoLast = @undoArray;
  my $oldCardsInPlay = $cardsInPlay;
  @force = ();
  @pointsArray = ();
  reinitBoard();
  #print "$cardsInPlay cards in play.\n";
  $x = $#undoArray;
  $tempUndoCmd = $undoArray[$x];
  #print "$x elts left\n";
  if ($x >= 0)
  {
	while (($x > 0) && ($tempUndoCmd eq "n+")) { pop(@undoArray); $x--; $tempUndoCmd = $undoArray[$x]; }
	if (($_[0] != 3) || ($tempUndoCmd ne "df")) # special case: Don't pop if we are near a DF anyway
	{
    $tempUndoCmd = pop(@undoArray);
	$x--;
	printDebug("Popped $tempUndoCmd\n");
	}
	if ($_[0] == 1)
	{
	my $undos = 0;
	while (($x >= 0) && ($undos < $_[1]))
	{
	while (($x >= 0) && ($undoArray[$x] =~ /^(f|n-|n\+)/))
	{
	  $x--; $tempUndoCmd = pop(@undoArray);
	}
	if (($x >= 0) && ($undoArray[$x] eq "df")) { for (1..6) { pop(@undoArray); } $x -= 6; }
	pop(@undoArray); $x--;
	$undos++;
	}
	$lastNMinus = 0;
	for (0..$#undoArray)
	{
	  if ($undoArray[$_] eq "n-") { $lastNMinus = 0; }
	  if ($undoArray[$_] eq "n+") { $lastNMinus = 1; }
	}
	}
	elsif (($_[0] ==3) && ($undoArray[$x] eq "df"))
	{
	  print "Already at a draw, so only going back one move.\n";
	  while (($undoArray[$x] =~ /^[fd]/) && ($x >= 0)) { $x--; pop(@undoArray);  }
	}
	elsif (($_[0] == 2) || ($_[0] == 3))
	{
	  #print "1=============\n@undoArray\n";
	while (($undoArray[$x] ne "df") && ($x >= 0)) { $x--; pop(@undoArray); }
	  #print "2=============\n@undoArray\n";
	if (($_[0] == 3) && ($x > 0))  # encountered df.
	{
	  $tempUndoCmd = 0;
	  pop(@undoArray); $x = $#undoArray;
	  while (($undoArray[$x] =~ /^f/) && ($x > 0))
	  {
	    $x--; pop(@undoArray); $tempUndoCmd++;
	  }
	  if ($tempUndoCmd != 6) { print "WARNING: popped wrong number of forces ($tempUndoCmd) in undo array. Push ul for full details.\n"; }
	}
	if ($_[0] == 2) { push(@undoArray, "n-"); }
	}
	elsif (($tempUndoCmd eq "n-"))
	{
	while (($undoArray[$x] ne "n+") && ($x >= 0)) { $x--; pop(@undoArray); }
	}
	else
	{
	while (($undoArray[$x] =~ /^(f|n\+)/) && ($x >= 0))
	{
	  $x--;
	  $tempUndoCmd = pop(@undoArray);
	  #print "extra-popped 1 $tempUndoCmd\n";
	}
	}
	while (($x >= 0) && ($undoArray[$x] =~ /^n\+/) ) # this is to get rid of stray N+
	{
	  $x--;
	  if ($#undoArray > -1)
	  {
	    $tempUndoCmd = pop(@undoArray);
	  }
	  else
	  {
	    $tempUndoCmd = "";
	  }
	  #print "extra-popped 2 $tempUndoCmd\n";
	}
  }
  #print "@undoArray\n";
  $undo = 1;
  for (0..$#undoArray)
  {
	#$undo = 0;
    #print "$undoArray[$_]\n";
    procCmd($undoArray[$_]);
  }
  $undo = 0;
  @outSinceLast = ();
  printdeck(-1);
  # allow for an undo on back regularly after a u1
  if (($lastNMinus) && ($undoArray[$#undoArray] ne "n-") && ($tempUndoCmd ne "n+") && ($#undoArray != -1)) { push(@undoArray, "n-"); }
}

sub checkWellForm
{
  printDebug("Checking wellform\n");
  my $plusses = 0;
  my $z;
  my $minusNext = 0;
  for my $z (0..$#undoArray)
  {
    if ($undoArray[$z] eq "n+") { if ($minusNext) { print "Undo malformed at $z, unexpected n+.\n"; } $plusses++;  $minusNext = 1; }
    if ($undoArray[$z] eq "n-") { if (!$minusNext) { print "Undo malformed at $z, unexpected n-.\n"; } $plusses--; $minusNext = 0; }
  }
  if ($plusses == 1) { print "Last n+ is not matched with n-.\n"; }
}

sub printLowCards
{
  my $retString = "Low cards: ";
  for my $a (1..6) { $retString .= "$a " . faceval(botCard($a)) . " "; }
  return "$retString\n";
}

sub showhidden
{
  my @out = (0, 0, 0, 0);
  my $outs = "";

  if ($hidCards == 0) { print "Nothing hidden left.\n"; }
  my $lastSuit = -1;
  print "Still off the board:";
  for my $cardnum (1..52)
  {
    if ($inStack{$cardnum} || $holds{$cardnum})
	{
    if ($lastSuit != suit($cardnum)) { if ($out[$lastSuit] > 0) { print " ($out[$lastSuit])"; } $lastSuit = suit($cardnum); print "\n"; }
    if ($inStack{$cardnum}) { print " " . faceval($cardnum); $out[suit($cardnum)]++; }
	elsif ($holds{$cardnum}) { print " -" . faceval($cardnum); $out[suit($cardnum)]++; }
	}
  }
  if ($out[$lastSuit]) { print " ($out[$lastSuit])"; }
  my $is = keys %inStack;
  my $ih = $#force + 1;
  print "\nTotal unrevealed: " . ($is + $ih);
  if ($ih)
  {
    print " ($ih held to end:";
	for (0..$#force)
	{
	  if ($_) { print ","; }
	  print " " . faceval($force[$_]);
	}
	print ")";
  }
  print "\n";
  for (1..4) { if (!$out[$_]) { $outs .= "$sui[$_] OUT. "; } }
  if ($outs) { print "$outs\n"; }
}

sub ones # 0 means that you don't print the error message, 1 means that you do
{ # note we could try to do another round of safe shuffling after but then we do shuffling, ones, etc. & that can lose player control
  if (($undo) || ($currentlyLoadingSaving)) { return 0; } # otherwise this is a big problem if we want to undo something automatic.
  my $onesMove = 0;
  my $totMove = 0;
  my $localAnyMove = $anyMovesYet;
  my $insertNMinus;
  my $movesAtOnesStart = $#undoArray;
  my @thisTopCard;
  my @thisBotCard;

  #eventually delete this if nothing goes boom
  if (($#undoArray > -1) && ($undoArray[$#undoArray] eq "n-") && ($movesAtStart != $#undoArray)) # in other words, only if we moved, we should see this error, and still we shouldn't.
  {
    pop(@undoArray); $insertNMinus = 1; print "********************Popped an n-. This should not happen. Save the undo array to find why.\n";
  }

  $moveBar = 0;

  my $quickStr = "";

  printDebug("Before outer: $#undoArray\n");
  my $anyYet;
  OUTER: do
  {
  $anyYet = 0;
  for (1..6)
  {
  my $temp = $#{$stack[$_]};
  if ($temp == -1) { $thisTopCard[$_] = -3; $thisBotCard[$_] = -3; next; }
  while ($temp > 0)
  {
  if (($stack[$_][$temp] == $stack[$_][$temp-1]-1) && (suit($stack[$_][$temp-1]) == suit($stack[$_][$temp])))
  { $temp--; }
  else
  { last; }
  }
  $thisTopCard[$_] = $stack[$_][$temp];
  $thisBotCard[$_] = $stack[$_][$#{$stack[$_]}];
  }
  for my $j (1..6)
  {
    for my $i (1..6)
	{
	  if (!defined($thisBotCard[$i])) { next; }
	  my $err = canFlipQuick($thisBotCard[$j], $thisTopCard[$j], $thisBotCard[$i]);
	  if ($err > 0)
	  {
	    if (!$anyYet)
		{
		  my $tempStr = "";
		  $quickMove = 1;
		  $tempStr .= "$j->$i=" . faceval($thisBotCard[$j]);
		  if ($thisTopCard[$j] != $thisBotCard[$j]) { $tempStr .= "/" . faceval($thisTopCard[$j]); }
		  $tempStr .= " -> " . faceval($thisBotCard[$i]);
		  #if (($thisBotCard[$j] == 27) && ($thisBotCard[$i] == 28)) { $undo = 0; $quickMove = 0; $autoOneSafe = 0; printdeck(0); die; }
          printDebug("$i -> $j\n" . printLowCards());
		  tryMove("$j", "$i", -1);
		  if (!$quickStr) { $quickStr .= "AUTO: $tempStr"; } else { if ($totMove % 5 == 0) { $quickStr .= "\n      "; } else { $quickStr .= ", "; } $quickStr .= "$tempStr"; }
		  $quickMove = 0; $anyYet = 1; $totMove++; #print "Move $totMove = $j to $i\n";
		}
	  } #else { printDebug("$i $j $thisBotCard[$j], $thisTopCard[$j], $thisBotCard[$i] = err $err\n"); }
	}
  }
  }
  while ($anyYet);
  if ($seventwenty) { return 0; }
  printDebug("After outer: $#undoArray\n");
  if (!$stillNeedWin)
  {
  if (($quickStr) && ($autoOneFull)) { print "$quickStr\n"; }
  if (!$totMove) { if ($_[0] == 1) { print "No moves found.\n"; } } else { print "$totMove auto-move" . plur($totMove) . " made.\n"; }
  }

  #checkwin(-1);
}

sub canFlipQuick #can card 1 be moved onto card 3? card 2 is the top one. Ah, 8h, 9h would be yes, for instance.
{
  #printDebug("Trying $_[0]:$_[1] to $_[2], any moves = $anyMovesYet\n");
  if (suit($_[0]) != suit($_[2])) { return -1; }
  if ($_[2] - $_[1] != 1) { return -2; }
  if (!$anyMovesYet) { return 1; }

  #note that having, say, a 2H on the bottom must be safe as only the 1H can be placed and it does not matter where the 1H might show up later
  if ($_[0] % 13 == 1) { return 1; } # we'd like to be able to say X % 13 == 2 but that doesn't always work as if an AH falls next in a draw of 6, as it may want a choice of 2 places to go
  if (($_[0] % 13 == 2) && ($drawsLeft == 0)) { return 1; } # however in this case with nothing to draw we can proceed pretty clearly. Either the ace will be visible or it won't.
  if ($autoOneSafe) #this is extended safe: 2h to 3h if ah is not on the board
  {
    my $temp = ($_[0] / 13) * 13 + 1;
	my $searchRow = 0;
	my $searchIndex = 0;

	if ($drawsLeft == 0) # a special case but a nice one to speed things up near the end.
	{
	if (!$inStack{$temp})
	{
	  my $searchRow = 0;
	  my $searchIndex = 0;
	  for my $searchRow (1..6) # this simply searches to see if there is a ( X-1 .. 1) chunk left. If it is, then playing ones over is safe.
	  {
	    for my $searchIndex (0..$#{$stack[$searchRow]})
		{
		  if ($stack[$searchRow][$searchIndex] == $temp)
		  {
		    my $si = $searchIndex;
			while ($si > 0)
			{
			  if ($stack[$searchRow][$si-1] - $stack[$searchRow][$si] != 1) { return 0; }
			  if ($stack[$searchRow][$si-1] == $temp - 1) { return 1; }
			  $si--;
			}
		  }
		}
	  }
	}
	}

	while ($temp < $_[0])
	{
	#printDebug("$temp vs $_[0]: $inStack{$temp}\n");
	if (!$inStack{$temp}) { return -3; }
	$temp++;
	}
	return 1;
  }
  if ($autoOnes) { return 1; }
  return -4;
}

sub checkwin
{
  my $suitsDone = 0;
  my $suitlist = "";

  OUTER:
  for my $stax (1..6)
  {
    my @x = @{$stack[$stax]};
	if (!defined($x[0])) { next; }
	for (0..$#x)
	{
	  my $inarow = 0;
	  if (($x[$_] > 0) && ($x[$_] % 13 == 0) && ($_ < $#x))
	  {
	    while (($_ < $#x) && ($x[$_] - $x[$_+1] == 1) && ($x[$_+1]) && (suit($x[$_]) == suit($x[$_+1]))) { $_++; $inarow++; }
	  }
	  if ($inarow == 12) { $suitsDone++;  if (!$suitlist) { $suitlist = @sui[$x[$_]/13+1]; } else { $suitlist .= " @sui[$x[$_]/13+1]"; } }
	}
  }
  if ($seventwenty)
  {
    if ($suitsDone == 4) { return 1; } return 0;
  }
  if ((!$undo) && (!$quickMove) && (!$inMassTest))
  {
  if ($suitsDone == 4)
  {
    if (($#_ > 0) && ($_[0] == -1)) { printdeck(-1); } printOutSinceLast();

	$stillNeedWin = 0;
	print "You win! ";
	$winsThisTime++;
	if ($timesAuto) { printf "(took $timesAuto times, expected $expected) "; use integer; $timesAuto = 0; }
	while (1)
	{
	print "Push ";
	if ($winsThisTime != $maxWins) { print "enter to restart, "; }
	print "q to exit, or s= to save an editable game, or u to undo."; $x = <STDIN>;
	if (($x eq "d;u") || ($x eq "u;d")) { print ("You already won. No need to button bash. Try cwx, actually.\n"); }
	if (($x =~ /^u/i) && ($x !~ /;/))
	{
	  $winsThisTime--;
	  splice(@undoArray, $beforeCmd + 1, 0, "n+");
	  push(@undoArray, "n-");
	  undo(0); $moveBar = 1; $shouldMove = 0;
	  return;
	}
	$youWon = 1;
    if ($x =~ /^q+/i) { processGame(); writeTime(); exit; }
	if ($x =~ /^s=/i) { if ($x =~ /^sf=/) { saveDeck($x, 1); next; } else { saveDeck($x, 0); next; } }
	if ($winsThisTime == $maxWins) { print "Take care! That was your last game.\n"; processGame(); writeTime(); exit; } elsif ($maxWins) { print "Played $winsThisTime of $maxWins games now.\n"; }
	@lastWonArray = @undoArray; @lastTopCard = @topCard; doAnotherGame(); return;
	}
  }
  my $er = emptyRows();
  if (($suitsDone || $er) && (!$stillNeedWin))
  {
  if ($suitsDone) { print "$suitsDone suit" . plur($suitsDone) . " completed ($suitlist)"; }
  if ($er) { if ($suitsDone) { print ", "; } print $er . " empty row" . plur($er); }
  print ".\n";
  }
  }
}

sub plur
{
  if ($#_ == -1) { return "s"; }
  elsif ($_[0] eq 1) { return ""; }
  elsif ($_[1]) { return "$_[1]"; }
  return "s";
}

sub peekAtCards
{
  print "On draw:";
  for (0..$#fixedDeck)
  {
    if (($_) && ($_ % 6 == 0)) { print " |"; }
    print " " . faceval($fixedDeck[$_]);
  }
  print "\n";
  for my $thisrow(1..6)
  {
    my $idx = 0;
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
	for my $thisrow(1..6)
	{
	  for (1..$blanks[$thisrow])
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
  my $winsuf = "win" . plur($wstreak);
  my $los = "loss" . plur($lstreak, "es");

 print "$wins $winsuf $losses $los\n";
 if ($wstreak) { print "Current win streak = $wstreak $winsuf\n"; }
 elsif ($lstreak) { print "Current loss streak = $lstreak $los\n"; }
 print "Longest streaks $lwstreak $winsuf $llstreak $los\n";
 print "Last ten games:";
 for (0..$#lastTen) { $sum += $lastTen[$_]; print " $wl[$lastTen[$_]]"; } print ", $sum $winsuf, " . (10-$sum) . " $los\n";
 printf("Win percentage = %d.%02d\n", ((100*$wins)/($wins+$losses)), ((10000*$wins)/($wins+$losses)) % 100);
}

sub saveDefault
{
  my $filename = "al-sav.txt";
  open(A, "$filename");
  <A>;
  open(B, ">$backupFile");
  print B "$startWith,$vertical,$collapse,$autoOnes,$beginOnes,$autoOneSafe,$sinceLast,$easyDefault,$autoOneFull,$showMaxRows,$saveAtEnd,$ignoreBoardOnSave\n";
  while ($a = <A>) { print B $a; }
  close(A);
  close(B);
  `copy $backupFile $filename`;
  `erase $backupFile`;
  print "Defaults saved.\n";
}

sub initGlobal
{
  $vertical = $collapse = 0;
  $youWon = 0;

  $sre{"c"} = 0;
  $sre{"d"} = 13;
  $sre{"h"} = 26;
  $sre{"s"} = 39;
  $rev{"a"} = 1;
  $rev{"j"} = 11;
  $rev{"q"} = 12;
  $rev{"k"} = 13;

  open(A, "al-sav.txt");
  my $a = <A>; chomp($a);
  my @opts = split(/,/, $a);
  if ($#opts < 11) { print "Note: not all options are present in al.pl.\n"; }
  if (!$startWith) { $startWith = $opts[0]; }
  $vertical = $opts[1];
  $collapse = $opts[2];
  $autoOnes = $opts[3];
  $beginOnes = $opts[4];
  $autoOneSafe = $opts[5];
  $sinceLast = $opts[6];
  if (!$easyDefault && ($#opts >= 7)) { $easyDefault = $opts[7]; }
  if ($#opts > 8) { $autoOneFull = $opts[8]; }
  if ($#opts >= 9) { $showMaxRows = $opts[9]; }
  if ($#opts >= 10) { $saveAtEnd = $opts[10]; }
  if ($#opts >= 11) { $ignoreBoardOnSave = $opts[11]; }
  close(A); # note showmaxrows and saveatend are global as of now

  if (!$startWith) { $startWith = 2; }

  #print "$a = first line\n";

  if ($startWith > 7) { print "First draw may take a bit...\n"; }

}

sub saveOpts
{
open(A, "al-sav.txt");
open(B, ">$backupFile");
#first line is global settings
<A>;

print B "$startWith,$vertical,$collapse,$autoOnes,$beginOnes,$autoOneSafe,$sinceLast,$easyDefault,$autoOneFull,$showMaxRows,$saveAtEnd,$ignoreBoardOnSave\n";

while ($a = <A>)
{
  print B $a;
}
close(A);
close(B);

`copy $backupFile al-sav.txt`;
`erase $backupFile`;
print "Options saved.\n";

}

sub showOpts
{
  print "========OPTIONS SETTING========\n";
  print "Vertical view (v) $toggles[$vertical].\n";
  print "Collapsing (c) $toggles[$collapse].\n";
  print "Fixed deck (ra) $toggles[$fixedDeckOpt].\n";
  print "Ignore Empty on Force (e) $toggles[$emptyIgnore].\n";
  print "Show Chain Breaks (cb) $toggles[$chainBreaks].\n";
  print "Auto-Ones on Draw (1a) $toggles[$autoOnes].\n";
  print "Begin with shuffling one-aparts (1b) $toggles[$beginOnes].\n";
  print "Auto-Ones Safe (1s) $toggles[$autoOneSafe].\n";
  print "Auto-Ones Full Desc (1f) $toggles[$autoOneFull].\n";
  print "Show blocked moves (sb) $toggles[$showBlockedMoves].\n";
  print "Show max rows (mr) $toggles[$showMaxRows].\n";
  print "Save undos at end (sae) $toggles[$saveAtEnd].\n";
  print "Show cards pulled since last (sl) $toggles[$sinceLast].\n";
  print "Easy default (ez) $toggles[$easyDefault].\n";
}

sub readScoreFile
{
open(A, "scores.txt");

$wins = $losses = $wstreak = $lstreak = $lwstreak = $llstreak = 0;

if (!fileno(A)) { print "No scores.txt\n"; }
else
{
print "Reading scores...\n";
my $stats = <A>; chomp($stats); @pcts = split(/,/, $stats);
if (defined($pcts[0])) { $wins = $pcts[0]; }
if (defined($pcts[1])) { $losses = $pcts[1]; }
if (defined($pcts[2])) { $wstreak = $pcts[2]; }
if (defined($pcts[3])) { $lstreak = $pcts[3]; }
if (defined($pcts[4])) { $lwstreak = $pcts[4]; }
if (defined($pcts[5])) { $llstreak = $pcts[5]; }
$stats = <A>; chomp($stats);
@lastTen = split(/,/, $stats);
close(A);
}
}

sub printLastWon
{
  if ($#lastWonArray == -1) { print "No previously won game this session.\n"; return; }
  print "#printout of last win: undo to get the right alignment";
  print "s=last won\n1,1\n";
  print "TC=" . join(",", @lastTopCard) . "\n";
  print "M=" . join(",", @lastWonArray) . "\n";
  print "\n\n\n\n\n\n";
}

sub writeTime
{
  my $randDenom = rand(9999) + 10001;
  my $time = time();
  my $remainder = $time % $randDenom;
  open (A, ">altime.txt");
  print A "$time\n$del\n$randDenom\n$remainder\n";
  close(A);
}

sub printNoTest
{
  if (!$inMassTest) { print $_[0]; }
}

sub printDebug
{
  if ($debug) { print "(DEBUG) $_[0]"; }
  #to track debugs we don't want
  #my $trace = Devel::StackTrace->new;
  #print $trace->as_string . "\n"; # like carp
}

sub printDeepDebug
{
  if ($debug > 1) { print "(DEBUG) $_[0]"; }
  #to track debugs we don't want
  #my $trace = Devel::StackTrace->new;
  #print $trace->as_string . "\n"; # like carp
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
[1-6][1-6][1-6]w moves a to c via b, then c to a via b. It is useful for, say, kh-jh-9h-7h and qh. Y repeats w.
[~!t][1-6][1-6][1-6] triages 3 columns with the same suit. It may cause a blockage.
v toggles vertical view (default is horizontal)
c toggles collapsed view (8h-7h-6h vs 8h=6h)
cb shows chain breaks e.g. KH-JH-9H-7H has 3
e toggles empty-ignore on eg if 2H can go to an empty cell or 6H, with it on, 1-move goes to 6H.
r restarts, ry forces if draws are left. You can specify =(#s or cards, comma separated) to force starting cards.
ez starts with 8C-KC across the top, and ezd sets it as default. er/erd sets randomized six-in-a-row.
(blank) or - reprints the deck.
d draws 6 cards (you get 5 of these), df forces if noncircular moves are left or you can move between AB, AC and BC.
q/x quits.
?? has more detailed usage, with u/undo, l/load and s/save
EOT
}

sub usageDet
{
print<<EOT;
s=saves current deck (rejected if name is used)
sf=save-forces if name exists (sfi/si saves "ignore", sfb/sb overrides "ignore")
h=shows hidden/left cards
b=push a card to the back (ho also, for hold)
f=force card
l=loads exact saved-deck name (e.g. s=me loaded be l=me)
lf=loads approximate saved-deck name (fuzzy, e.g. s=1 loads the first deck with a 1 in its name) (li/lfi ignores the saved position, lb/fb forces it)
t=loads test
tf=full test
os/so=option save
mr = show max rows
sd=save default
af=show force array
lw=show last won array
sl=show overturned since last move
sw=start with a minimum # of points (x-1 points for x-suits where x >=2, 1 point for adjacent cards, can start with 2-6)
sw0=shows odds of points to start with
sb=show blocked moves toggle
u=undo (to last block, or # for x moves back, x < 10)
um=undo 10+ moves
u1=undo one move
ud=undo to last 6-card draw
ub=undo to before last 6-card draw
ul=last undo array (best used for debugging if undo goes wrong. Sorry, it's not perfect yet.)
sl=save last undo array (to undo-debug.txt)
du=hidden undo debug (print undos to undo-debug.txt, probably better to use ul)
us=undo all the way to the start
ue=toggle undo each turn (only debug)
1a=auto ones (move cards 1 away from each other on each other: not strictly optimal)
1b=begin ones (this is safe, as no card stacks are out of order yet)
1s=auto ones safe (only bottom ones visible are matched up)
1f=ones full description (default is off) tells all the hidden moves the computer makes with 1s
1p=push ones once
%=prints stats
o=prints options' current settings
cw/cd=check for win-on-draw (1 draw left)
debug shows debug text
EOT
}

sub cmdUse
{
print<<EOT;
You typed an invalid command line parameter.

====others
-sw(0-9) or (0-9)=tells you to start with that many points.
-rf=(forced cards) or -rf (forced cards) can be used, if you want to be sneaky.
-ez=start easy game (8c-kc), -er = random 6-in-a-row, -e(zr)d sets defaults
-d is used for debug, but you don't want to see those details.
        And none should show up, I hope. Even with -dd, deep debug.
EOT
}