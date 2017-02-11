################################
#
# elo.pl
#
# calculates the ELO of all the teams or whatever
#
# I am copying from http://www.bigten.org/library/stats/mbb-schedule.html
#
#so anything of the form date \tab Winners xxx, Losers xxx should work

use strict;
use warnings;

use POSIX qw (round);

use Win32::Clipboard;

my %rating;
my %tempRating;

my %schedule;
my %skedNext;
my %wins;
my %losses;
my %homeAway;
my %locs;
my %expWins;
my %expLoss;
my %roundWin;
my %roundDubWin;

#defaults, can be tweaked with options
my $debug = 0;
my $iterations = 2000;
my $pointsPerWin = 32;
my $defaultRating = 2000;
my $debugEveryX = 0;
my $maxTotalShift = 0;
my $maxSingleShift = 0;
my $fudgefactor = 0.1;
my $home = 70;
my $suppressWarnings = 0;
my $clipboard = 0;
my $zapAdj = 1; # zap adjacent games that are the same
my $predictFuture = 1;
my $toHtml = 0;
my $launch = 0;
my $printRound = 0;
my $expByWin = 0;
my $printRemainDist = 0;
my $sigFig = 2;

#variables
my $x;
my $closeEnough = 0;
my $count = 0;
my @q;
my @allGames;
my $addString;
my $flipString;
my $undoString;
my $expPrint = "";

my @teams;
my %nickname;
my %revnick;
my $nickFile = "elonick.txt";
my $gameFile = "elosc.txt";
my $locFile = "eloloc.txt";

while ($count <= $#ARGV)
{
  $a = $ARGV[$count];
  $b = $ARGV[$count+1];
  for ($a)
  {
    /^-?d$/ && do { $debug=1; $count++; next; };
    /^-?de$/ && do { $debugEveryX = $b; $count += 2; next; };
    /^-?ff$/ && do
	{
	  $fudgefactor = $b;
	  if (($fudgefactor > .5) || ($fudgefactor < 0)) { die "Fudgefactor must be between 0 and .5.\n"; }
	  $count += 2;
	  next;
    };
	/^-?[0-9]$/ && do { $sigFig = $a; $sigFig =~ s/^-//; $count++; next; };
	/^-?a$/ && do { $addString = $b; $count += 2; next; };
	/^-?c(p)?$/ && do { $clipboard = 1; if ($a =~ /p/) { $clipboard = 2; } $count += 2; next; }; # this is not great coding but basically -c sends to clipboard, -p prints too
	/^-?e$/ && do { $expByWin = 1; $count ++; next; };
	/^-?f$/ && do { $flipString = $b; $count += 2; next; };
	/^-?u$/ && do { $undoString = $b; $count += 2; next; };
	/^-?h$/ && do { $home  = $b; $count += 2; next; };
    /^-?i$/ && do { $iterations = $b; $count += 2; next; };
	/^-?m$/ && do { $maxTotalShift = $b; $count += 2; next; };
	/^-?m1$/ && do { $maxSingleShift = $b; $count += 2; next; };
	/^-?o(l)?$/ && do { $toHtml = 1; if ($a =~/l/) { $launch = 1; } $count++; next; };
	/^-?n(i)?$/ && do { $nickFile = $b; $count += 2; next; };
    /^-?[pw]$/ && do { $pointsPerWin = $b; $count += 2; next; };
    /^-?r$/ && do { $defaultRating = $b; $count += 2; next; };
	/^-?rd$/ && do { $printRemainDist = 1; $count++; next; };
	/^-?rr$/ && do { $printRound = 1; $count++; next; };
	/^-?s$/ && do { $suppressWarnings = 1; $count++; next; };
    /^-?(re|g)$/ && do { $gameFile = $b; $count += 2; next; };
	/^-?!(c)?$/ && do
	{
	  $expByWin = 1; $printRemainDist = 1; $printRound = 1;
	  if ($a =~ /c/) { $clipboard = 1; } else { $toHtml = 1; $launch = 1; } $count++; next; }; # kitchen sink option
    usage();
  }
}

readTeamLocs();
readTeamNicknames();
readTeamGames();
doIterations();
stabilizeRatings();
printOutRatings();

##########################################################################subroutines

#####################################simply executes eloIterate until all iterations are either through or small enough not to worry
sub doIterations
{
for ($count = 0; $count < $iterations && !$closeEnough; $count++)
{
eloIterate();
}

if ($closeEnough)
{
  print "Needed $count of $iterations iterations.\n";
}
}

# this takes the ELO rating for each team, replays all the games, and tracks all ratings changes
sub eloIterate
{
  my $x;
  my @b;
  my @c;
  my $expWins;
  my $mult;
foreach $x (keys %rating)
{
  $expWins = 0;
  $tempRating{$x} = $rating{$x};
  @b = split(/,/, $schedule{$x});
  @c = split(/,/, $homeAway{$x});
  for (0..$#b)
  {
  #print "$x, $_, $c[$_], $home: " . ($rating{$b[$_]} + ($c[$_] * $home)) . "\n";
  $mult = ($rating{$b[$_]} + ($c[$_] * $home) - $rating{$x})/400;
  $expWins += 1/(1+10**($mult));
  }
  #printf("$x changes by %.2f.\n", ($wins{$x} - $expWins) * $pointsPerWin);
  $tempRating{$x} += ($wins{$x} - $expWins) * $pointsPerWin;
}

my $totalDelt = 0;
my $maxDelt = 0;
my $curDelt = 0;
foreach $x (keys %rating)
{
  if ($debug || $maxTotalShift || $maxSingleShift)
  {
  $curDelt = abs($rating{$x} - $tempRating{$x});
  if ($curDelt > $maxDelt) { $maxDelt = $curDelt; }
  $totalDelt += $curDelt;
  }
  $rating{$x} = $tempRating{$x};
}
if ($debug)
{
  print("$totalDelt total rating shift for run $count.\n");
  print("$maxDelt maximum rating shift for run $count.\n");
}
if ($totalDelt < $maxTotalShift) { $closeEnough = 1; }
if ($maxDelt < $maxSingleShift) { $closeEnough = 1; }

if (($debugEveryX) && ($count  % $debugEveryX == 0))
{
  print("Results after $count ==============================\n");
  foreach $x (sort { $rating{$b} <=> $rating{$a} } keys %rating)
  {
    printf("$x %.2f\n", $rating{$x});
  }
}

}

##################this is the ELO formula for expected wins
sub winPct
{
  my $exp = ($rating{$_[1]} - $rating{$_[0]} - $home * $_[2]) / 400;
  return 100/(1+10**$exp);
}

##################if debug flag is on, print what's there. Otherwise, do nothing.
sub printdebug
{
  if (!$debug) { return; }
  print $_[0];
}

################team's nickname, if they have one. If not, team's name
sub ifshort
{
  if (defined($nickname{$_[0]}))
  {
    return $nickname{$_[0]};
  }
  return $_[0];
}

################reads game scores and converts them to (Winner, Loser)
sub readTeamGames
{
open(A, $gameFile) || die ("No team game file");

while ($a = <A>)
{
  chomp($a);
  if ($a =~ /#/)
  {
    next;
  }
  if ($a =~ /;/) { last; }
  if ($a =~ /^#/) { next; }
  addToSched($a);
}

readUserAlterations();
processInitSchedule();

for (keys %schedule) { $schedule{$_} =~ s/^,//; }
for (keys %homeAway) { $homeAway{$_} =~ s/^,//; }
#for (keys %homeAway) { print "$_: $homeAway{$_}\n"; } die;

close(A);
my $team;
my $adj = 0;
my $allwin = 0;
my $allloss = 0;
for $team (@teams)
{
  if ($wins{$team} + $losses{$team} == 0) { die ("$team has not played any games. Bailing.\n"); }
  if ($losses{$team} == 0) { $allloss++; }
  if ($wins{$team} == 0) { $allwin++; }
}

if (scalar @teams - $allwin - $allloss == 0) { die ("No teams with a win and a loss. Bailing.\n"); }

#check for the most likely case when we have played a few rounds, where everyone has won and lost, no adjustments necessary
if ($allwin + $allloss == 0) { return; }

if ($allwin == $allloss) { return; }
my $delta = ($allwin - $allloss) * $fudgefactor * ($allwin + $allloss) / (@teams - $allwin - $allloss);
for $team (@teams)
{
  if ($wins{$team} == 0)
  {
    if ($debug) { print "$team has no wins.\n"; }
	$allwin++; $losses{$team} -= $fudgefactor; $wins{$team}  = $fudgefactor;
  }
  elsif ($losses{$team} == 0)
  {
    if ($debug) { print "$team has no losses.\n"; }
	$allloss++; $wins{$team} -= $fudgefactor; $losses{$team}  = $fudgefactor;
  }
  else { $wins{$team} -= $delta; $losses{$team} += $delta; }
}

if ($debug)
{
print "Fudge factor = $fudgefactor, delta = $delta\n";
for my $t (@teams) { print "$t: $wins{$t}-$losses{$t}\n"; }
}
}

sub processInitSchedule
{
  my @q;
  my $myGame;
  for $myGame (@allGames)
  {
  @q = split(/,/, $myGame);
  $homeAway{$q[0]} .= "," . $q[2];
  $homeAway{$q[1]} .= "," . (0 - $q[2]);
  $schedule{$q[0]} .= ",$q[1]";
  $schedule{$q[1]} .= ",$q[0]";
  $wins{$q[0]}++;
  $losses{$q[1]}++;
  }
}

############################adds a game to the schedule.
sub addToSched
{
  my $scoreYet;
  my $locationYet;
  my $score;
  my $tabentry;
  my $thisLoc;
  my $homeTeam = "";

  my $line = $_[0];
  if ($line =~ /\t/) # the big ten website has tables, which cut-paste to tabs. Otherwise, we can make files with "WINNER, LOSER" and @ where need be
  {
  $line =~ s/ *$//;
  $homeTeam = "";
  my @lineSplit = split(/ *\t */, $line);
  for $tabentry (@lineSplit)
  {
    if ($tabentry =~ /20[0-9][0-9]/) { next; } # this is a date
	if ($tabentry !~ /[a-z]/i) { next; } # blank cell, skip it
	if ($tabentry =~ / at /)
	{
	  my @teams = split(/ at /, $tabentry);
	  if ($#teams != 1) { print ("$tabentry has 'at' text but is not in the form team1\@team2, $#teams.\n"); return; }
	  if ($zapAdj && ($skedNext{$teams[0]} =~ /,\@$teams[1]$/i)) { return; }
	  if ($zapAdj && ($skedNext{$teams[1]} =~ /,$teams[0]$/i)) { return; }
	  $skedNext{$teams[0]} .= "," . "\@" . "$teams[1]";
	  $skedNext{$teams[1]} .= ",$teams[0]";
	  return;
	}
    if ($tabentry !~ /[0-9]/) # might be game location
	{
	  for my $loc (keys %locs)
	  {
	    if ($locs{$loc} eq $tabentry)
		{
		  $homeTeam = $loc;
		  last;
		}
	  }
	  $thisLoc = $tabentry;
	  next;
	}
	if ($tabentry =~ /[0-9],/)
	{
	  $score = $tabentry;
	  $score =~ s/ *\([0-9]* *OT\) *//;
	  $score =~ s/ *[0-9]+//g;
	  $score =~ s/, */,/g;
	}
  }
  if ($homeTeam)
  {
    if ($score =~ /^$homeTeam/) { $score = "$score,1"; }
	elsif ($score =~ /,$homeTeam/) { $score = "$score,-1"; }
	else { $score = "$score,0"; }
  } else { $score = "$score,0"; }
  #print "$score,$homeTeam!!\n";
  }
  else
  {
    $score = $line;
  }
  if ($score =~ /^-/) { $score =~ s/^-(.*),(.*)/$2,$1/; } # - at start means reverse
  my @q = split(/,/, $score);
  if ($q[0] =~ /^@/) { $q[2] = 1; $q[0] =~ s/^@//; }
  if ($q[1] =~ /^@/) { $q[2] = -1; $q[1] =~ s/^@//; }
  $q[0] = teamMod($q[0]);
  $q[1] = teamMod($q[1]);
  if (defined($rating{$q[0]}) && defined($rating{$q[1]}))
  {
    if ($q[0] eq $q[1])
	{
	  print("$q[0] playing themselves at line $. ignored. A team can only figuratively beat itself.\n");
	  next;
    }
	if (!defined($q[2])) { push(@q, 0); }
	push(@allGames, join(",", @q));
  }
}

##################this allows us to use shorthand
sub teamMod
{
  my $team;
  if ($rating{$_[0]}) { return $_[0]; }
  if ($revnick{lc($_[0])}) { return $revnick{lc($_[0])}; }
  for $team (keys %rating)
  {
    if (lc($team) eq lc($_[0])) { return $team; }
  }
  if (!$suppressWarnings) { print "WARNING $_[0] could not be modded into a team" . ($. ? " at line $." : "" ) . ".\n"; }
}

sub readTeamLocs
{
  my @l;
  open(A, $locFile) || die ("No location file $locFile");
  while ($a=<A>)
  {
  if ($a =~ /^#/)
  { next; }
  if ($a =~ /^;/)
  { last; }
  chomp($a);
  @l = split (/\t/, $a);
  if ($#l != 1) { print "WARNING bad line $.: $a\n"; }
  else { $locs{$l[0]} = $l[1]; }
  }
  #for my $loc(sort keys %locs) { print "$loc, $locs{$loc}\n"; }
}

###################reads teams and their short names--short names are handy if we are exporting to an HTML table and want to keep it narrow
# e.g. names like "Northwestern" make a column really wide
sub readTeamNicknames
{
open(A,  $nickFile) || die ("Can't open $nickFile");
my @b;
my $temp;
while ($a = <A>)
{
  if ($a =~ /^;/)
  { last; }
  chomp($a);
  @b = split(/,/, $a);
  push(@teams, $b[0]);
  if ($#b > 0)
  {
    $nickname{$b[0]} = $b[1];
	for (1..$#b)
	{
	  $temp = lc($b[$_]);
	  if ($revnick{$temp}) { die ("$temp was mapped to $revnick{$temp} but $nickFile tries to redefine it as $b[0]."); }
	  $revnick{lc($b[$_])} = $b[0];
	  $skedNext{$b[0]} = "";
    }
  }
}
@teams = sort(@teams);
for (@teams) { $rating{$_} = $defaultRating; $wins{$_} = 0; $losses{$_} = 0; }

}

sub readUserAlterations
{
my @gameMod = ();
my $thisGame;
my $gotOne;

  if ($addString)
  {
    @gameMod = split(/\//, $addString);
	for $thisGame (@gameMod) { addToSched($thisGame); }
  }
  if ($flipString)
  {
    @gameMod = split(/\//, $flipString);
	for $thisGame (@gameMod)
	{
     $gotOne = 0;
	  for (0..$#allGames)
	  {
	    if (lc($thisGame) eq lc($allGames[$_]))
		{
          my $thatGameR = $allGames[$_];
          $thatGameR =~ s/(.*),(.*)/$2,$1/;
		  splice(@allGames, $_, 1);
		  push(@allGames, $thatGameR);
		  $gotOne = 1;
		}
	  }
      if (!$gotOne) { print "$thisGame didn't happen so it can't be flipped.\n";}
	}
  }
  if ($undoString)
  {
    @gameMod = split(/\//, $undoString);
	for $thisGame (@gameMod)
	{
      $gotOne = 0;
	  for (0..$#allGames)
	  {
	    if (lc($thisGame) eq lc($allGames[$_]))
		{
		  $gotOne = 1;
		  splice(@allGames, $_, 1);
		}
	  }
      if (!$gotOne) { print "$thisGame didn't happen so it can't be flipped.\n";}
	}
  }

}

#########################this stabilizes any significant rounding errors while we are approximating ELO ratings. Everyone gets a +/- til the average is the default rating again.
sub stabilizeRatings
{
my $totalRating;

foreach $x (sort keys %rating)
{
  $totalRating += $rating{$x};
}
my $endFudge = $defaultRating - $totalRating / (scalar keys %rating);
if ($endFudge < .01) { print "No significant rounding errors\n"; return; }
printf("Adjusting all ratings by %.4f.\n", $endFudge);

foreach $x (sort keys %rating)
{
  $rating{$x} +=  $endFudge;
}

}

#######################here we print out all the ratings
sub printOutRatings
{
my $bigPrint = "";

foreach $x (sort keys %rating)
{
  $rating{$x} = int($rating{$x} + .5);
}

 my $rank = 0;

 if ($predictFuture) { predictFutureWins(); }

 $bigPrint .= "<center><font size=+3><b>ELO/Predicted finish table</b></font></center><br />Text here<br /><table border=1><th>Rank<th>Team<th>W-L<th>Rating";
  if ($predictFuture) { $bigPrint .= "<th>ExpTotal<th>Rounded<th>ExpLeft"; }
  $bigPrint .= "\n";
  foreach $x (sort {$rating{$b} <=> $rating{$a}} keys %rating)
  {
    $rank++;
    $bigPrint .= "<tr><td>$rank<td>$x<td>$wins{$x}-$losses{$x}<td>$rating{$x}";
    if ($predictFuture) { $bigPrint .= sprintf("<td>%.*f-%.*f <td><center>%d-%d</center><td>%.*f-%.*f", $sigFig, $wins{$x} + $expWins{$x}, $sigFig, $losses{$x} + $expLoss{$x},
	  round($wins{$x} + $expWins{$x}), round($losses{$x} + $expLoss{$x}), $sigFig, $expWins{$x}, $sigFig, $expLoss{$x});
    }
    $bigPrint .= "\n";
  }
  $bigPrint .= "</table>\n";

# now to print the table of probabilities
$bigPrint .= "<center><font size=+3><b>Head to Head</b></font></center><br />Text here<br /><table border=1><tr><td>H/A";

my $t1;
my $t2;
my $mult;
my $cellTitle;
my $bg;
my $neutWin;
my $bothWayWin;
my $temp;

for $t1 (sort keys %rating)
  {
    $bigPrint .= "<td>";
	$bigPrint .= ifshort($t1);
  }
$bigPrint .= "\n";
for $t1 (sort keys %rating)
  {
    $bigPrint .= "<tr><td>";
	$bigPrint .= ifshort($t1);
    for $t2 (sort keys %rating)
	{
	  $neutWin = winPct($t1, $t2, 0) / 100;
	  $bothWayWin = (winPct($t1, $t2, 1) + winPct($t1, $t2, -1))/100;

      $cellTitle  = sprintf("\"%.*f win exp Home+away, %.*f neutral\"", $sigFig, $bothWayWin, $sigFig, $neutWin * 100);
	  $roundWin{$t1} += $neutWin;
	  $roundDubWin{$t1} += $bothWayWin;
	  $bg = sprintf("%02x%02x00", 255 - winPct($t1, $t2, 1) * 2.55, winPct($t1, $t2, 1) * 2.55);
	  $bigPrint .= "<td title=$cellTitle bgcolor=\"$bg\">";
	  if ($t1 eq $t2) { next; }
	  $bigPrint .= sprintf("%.*f", $sigFig, winPct($t1, $t2, 1));
	}
	$bigPrint .= "\n";
  }
  $bigPrint .= "</table>";
  if ($printRound)
  {
    $bigPrint .= "<center><font size=+3><b>Round Robin</b></font></center><br />Text here<br /><table border=1><th>Team<th>RR neutral Wins<th>RR h/a wins\n";
	my $elts = scalar (keys %rating )- 1;
	for $t1 (sort { $rating{$b} <=> $rating{$a} } keys %rating)
	{
	  $bigPrint .= sprintf("<tr><td>$t1<td>%.*f-%.*f<td>%.*f-%.*f\n", $sigFig, $roundWin{$t1}, $sigFig, $elts - $roundWin{$t1}, $sigFig, $roundDubWin{$t1}, $sigFig, 2 * $elts - $roundDubWin{$t1});
    }
	$bigPrint .= "</table>\n";
  }
  if ($printRemainDist) { $bigPrint .= $expPrint; }
  if($expByWin)
  {
	  $bigPrint .= "<center><font size=+3><b>Round Robin Neutral Expected Wins</b></font></center><br />Text here<br /><table border=1>\n<tr><td>Team/WinDist";
	for (0..(scalar keys %rating)-1)
	{
	  $bigPrint .= "<td>$_";
	}
	$bigPrint .= "\n";
    for $t1 (sort keys %rating)
	{
	  my @wins = (1);
	  my @newWins = ();
	  for $t2 (sort keys %rating)
	  {
	    if ($t1 eq $t2) { next; }
		for (0..$#wins+1)
		{
		  $temp = winPct($t1, $t2, 0)/100;
		  if ($_ < $#wins+1) { $newWins[$_] = (1-$temp) * $wins[$_]; }
		  if ($_) { $newWins[$_] += $temp * $wins[$_-1]; }
		}
		@wins = @newWins;
	  }
	  my $max = 0;
	  my $maxVal = 0;
	  for (0..$#newWins) { if ($newWins[$_] > $max) { $maxVal = $_; $max = $newWins[$_]; } }
        $bigPrint .= "<tr><td>$t1<td>";
		$bigPrint .= join("<td>", map { sprintf("%s%.*f%s", ($_ == $max) ? "<b>" : "", $sigFig, $_*100, ($_ == $max) ? "</b>" : "") } @wins) . "\n";
	}
    $bigPrint .= "</table>\n";
  }
  if ($toHtml)
  {
    open(B, ">elo.htm"); print B $bigPrint; close(B);
	if ($launch) { `elo.htm`; }
	return;
  }
  if ($clipboard)
  {
  my $clip = Win32::Clipboard::new();
  $clip->Set($bigPrint);
  print "Main data printed to clipboard.";
  }
  if ($clipboard != 1) { print $bigPrint; }
}

sub predictFutureWins
{

  my $t1;
  my @games;
  my @sk;
  my $game;
  my $temp;
  my $onRoad;
  my $tw;
  my @winDist;
  my @winDistTemp;
  my $maxLeft = 0;

  for $t1 (sort keys %rating)
  {
    @winDist =(1);
	@winDistTemp = (0);
    $skedNext{$t1} =~ s/^,//;
     @sk = split(/,/, $skedNext{$t1});
	 for $game (@sk)
	 {
	   $temp  = $game;
	   if ($game =~ /^\@/)
	   {
	     $temp =~ s/^\@//;
	     $onRoad = 1;
	    } else { $onRoad = -1; }
		$tw = winPct($t1, $temp, -$onRoad) / 100;
        $expWins{$t1} += $tw;
		$expLoss{$t1} += 1 - $tw;
		@winDistTemp = (0) x ($#winDist+1);
		for(0..$#winDist)
		{
		  $winDistTemp[$_] += $winDist [$_] * (1-$tw);
		  $winDistTemp[$_+1] = $winDist [$_] * $tw;
		}
		@winDist = @winDistTemp;
		#print "$tw changes stuff to @winDist\n";
	 }
	if ($maxLeft < $#winDist) { $maxLeft = $#winDist; }
	$expPrint .= "<tr><td>$t1";
	for (0..$#winDist)
	{
	  $expPrint .= sprintf("<td title=%d-%d>%.*f%%", $wins{$t1} + $_, $losses{$t1} + $#winDist - $_, $sigFig, $winDist[$_]*100);
	}
  }
  $expPrint = "<center><font size=+3><b>Remaining Win Distribution</b></font></center><br />Text here<br /><table border=1><th>Team<th>" . join("<th>", (0..$maxLeft)) . "\n" . $expPrint . "</table>\n";
}

##################################standard usage file
sub usage
{
print<<EOT;
-[2-9] changes signifigant digits, default is 2
-a adds games
-c puts stuff to clipboard
-d is debug rating
-e shows expected win share in a round robin
-f flips a game's result (winner first, changed to loser)
-de means send debug information every X iterations
-ff sets the fudge factor for winless/undefeated teams so their ratings aren't undefined (currently .1 of a game, max .5)
-h specifies home advantage
-i changes number of iterations
-m is the minimum total rating shift to try another iteration
-m1 is the minimum maximum rating shift by any one team to try another iteration
-ni changes the nickname file
-o puts stuff out to HTML file (elo.htm) and  -ol launches
-p/-w changes the points per win
-r changes the default rating, which is usually 2000 (expert)
-rd shows remaining win distribution
-re/-g changes the game result file(s) (CSV)
-rr shows round robin results on a neutral floor and double round robin results with home and away
-s suppresses warnings
-t specifies a certain team
-u undoes a game (deletes it)
-! is the kitchen sink option to print out everything (-rr -d -e -ol, -!c exports to clipboard instead of HTML file)
EOT
exit;
}

# future options:
# * table or no
# * check what total ratings sum to and bring everything back to the original average
# also, create a hash of win numbers for each side, as well as their schedule. @allGames contains nonconference games at the moment.