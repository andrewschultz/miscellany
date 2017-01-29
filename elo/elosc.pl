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

my %rating;
my %tempRating;

my %schedule;
my %wins;
my %losses;
my %homeAway;

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

#variables
my $x;
my $closeEnough = 0;
my $count = 0;
my @q;
my @allGames;
my $addString;
my $flipString;
my $undoString;

my @teams;
my %nickname;
my %revnick;
my $nickfile = "elonick.txt";
my $gamefile = "elosc.txt";

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
	/^-?a$/ && do { $addString = $b; $count += 2; next; };
	/^-?f$/ && do { $flipString = $b; $count += 2; next; };
	/^-?u$/ && do { $undoString = $b; $count += 2; next; };
	/^-?h$/ && do { $home  = $b; $count += 2; next; };
    /^-?i$/ && do { $iterations = $b; $count += 2; next; };
	/^-?m$/ && do { $maxTotalShift = $b; $count += 2; next; };
	/^-?m1$/ && do { $maxSingleShift = $b; $count += 2; next; };
	/^-?n(i)?$/ && do { $nickfile = $b; $count += 2; next; };
    /^-?[pw]$/ && do { $pointsPerWin = $b; $count += 2; next; };
    /^-?r$/ && do { $defaultRating = $b; $count += 2; next; };
	/^-?s$/ && do { $suppressWarnings = 1; $count++; next; };
    /^-?(re|g)$/ && do { $gamefile = $b; $count += 2; next; };
    usage();
  }
}

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
  my $exp = ($rating{$_[1]} - $rating{$_[0]}) / 400;
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
open(A, $gamefile) || die ("No team game file");

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
  my $line = $_[0];
  if ($line =~ /\t/) # the big ten website has tables, which cut-paste to tabs. Otherwise, we can make files with "WINNER, LOSER"
  {
  $line =~ s/.*201[67][ \t]*//;
  $line =~ s/^[ \t]*//;
  $line =~ s/\t.*//;
  $line =~ s/ *\(OT\)//;
  $line =~ s/ *[0-9]+, */,/;
  $line =~ s/ *[0-9]+ *$//;
  }
  if ($line =~ /^-/) { $line =~ s/^-(.*),(.*)/$2,$1/; } # - at start means reverse
  my @q = split(/,/, $line);
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

###################reads teams and their short names--short names are handy if we are exporting to an HTML table and want to keep it narrow
# e.g. names like "Northwestern" make a column really wide
sub readTeamNicknames
{
open(A,  $nickfile) || die ("Can't open $nickfile");
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
	  if ($revnick{$temp}) { die ("$temp was mapped to $revnick{$temp} but $nickfile tries to redefine it as $b[0]."); }
	  $revnick{lc($b[$_])} = $b[0];
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
foreach $x (sort keys %rating)
{
  $rating{$x} = int($rating{$x} + .5);
}

 my $rank = 0;

 print "<table border=1>\n";
foreach $x (sort {$rating{$b} <=> $rating{$a}} keys %rating)
{
  $rank++;
  print "<tr><td>$rank<td>$x<td>$wins{$x}-$losses{$x}<td>$rating{$x}\n";
}
print "</table>\n";

# now to print the table of probabilities
print "<table border=1><tr><td>";

my $t1;
my $t2;
my $mult;

for $t1 (sort keys %rating)
  {
    print "<td>";
	print ifshort($t1);
  }
print "\n";
for $t1 (sort keys %rating)
  {
    print "<tr><td>";
	print ifshort($t1);
    for $t2 (sort keys %rating)
	{
	  print "<td>";
	  if ($t1 eq $t2) { next; }
	  printf("%.2f", winPct($t1, $t2));
	}
	print "\n";
  }
  print "</table>";
}

##################################standard usage file
sub usage
{
print<<EOT;
-a adds games
-f flips a game's result (winner first, changed to loser)
-u undoes a game (deletes it)
-d is debug rating
-de means send debug information every X iterations
-ff sets the fudge factor for winless/undefeated teams so their ratings aren't undefined (currently .1 of a game, max .5)
-i changes number of iterations
-m is the minimum total rating shift to try another iteration
-m1 is the minimum maximum rating shift by any one team to try another iteration
-ni changes the nickname file
-p/-w changes the points per win
-r changes the default rating, which is usually 2000 (expert)
-re/-g is the game result file
-s suppresses warnings
EOT
exit;
}

# future options:
# * table or no
# * check what total ratings sum to and bring everything back to the original average
# also, create a hash of win numbers for each side, as well as their schedule. @allGames contains nonconference games at the moment.