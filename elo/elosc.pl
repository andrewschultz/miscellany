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

my %wins;
my %losses;

#defaults, can be tweaked with options
my $dBug = 0;
my $iterations = 2000;
my $pointsPerWin = 32;
my $defaultRating = 2000;
my $debugEveryX = 0;
my $maxTotalShift = 0;
my $maxSingleShift = 0;
my $fudgefactor = 0.1;

#variables
my $closeEnough = 0;
my $count = 0;
my @allGames = ();
my @q;

my @teams;
my %nickname;
my $nickfile = "elonick.txt";
my $gamefile = "elosc.txt";

while ($count <= $#ARGV)
{
  $a = $ARGV[$count];
  $b = $ARGV[$count+1];
  for ($a)
  {
    /^-?d$/ && do { $dBug=1; $count++; next; };
    /^-?de$/ && do { $debugEveryX = $b; $count += 2; next; };
    /^-?f$/ && do
	{
	  $fudgefactor = $b;
	  if (($fudgefactor > .5) || ($fudgefactor < 0)) { die "Fudgefactor must be between 0 and .5.\n"; }
	  $count += 2;
	  next;
    };
    /^-?i$/ && do { $iterations = $b; $count += 2; next; };
	/^-?m$/ && do { $maxTotalShift = $b; $count += 2; next; };
	/^-?m1$/ && do { $maxSingleShift = $b; $count += 2; next; };
	/^-?n(i)?$/ && do { $nickfile = $b; $count += 2; next; };
    /^-?[pw]$/ && do { $pointsPerWin = $b; $count += 2; next; };
    /^-?r$/ && do { $defaultRating = $b; $count += 2; next; };
    /^-?(re|g)$/ && do { $gamefile = $b; $count += 2; next; };
    usage();
  }
}

readTeamNicknames();
readTeamGames();

for ($count = 1; $count <= $iterations && !$closeEnough; $count++)
{
eloIterate();
}

if ($closeEnough)
{
  print "Needed $count of $iterations iterations.\n";
}

my $x;

foreach $x (sort keys %rating)
  {
    $rating{$x} = int($rating{$x} + .5);
  }

 my $rank = 0;

 print "<table>\n";
foreach $x (sort {$rating{$b} <=> $rating{$a}} keys %rating)
{
  $rank++;
  print "<tr><td>$rank<td>$x<td>$rating{$x}\n";
}
print "</table>";

# now to print the table of probabilities
print "<table><tr><td>";

my $t1;
my $t2;
my $mult;

for $t1 (sort keys %rating)
  {
    print "<td>";
	print ifshort($t1);
  }
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

##########################subroutines

sub eloIterate # this takes the ELO rating and
{
  my $x;
  my @b;
  my $expPoints;
  my $expWins;
foreach $x (keys %rating) { $tempRating{$x} = $rating{$x}; }

for (@allGames)
{
  @b = split(/[,]/, $_);
  #printf("$b[0] %d vs $b[1] %d\n", $rating{$b[0]}, $rating{$b[1]});
  # this shouldn't be necessary but I want it in to do basic error checking
  unless (defined($rating{$b[0]}) && defined($rating{$b[1]})) { print "$_ is an irrelevant matchup\n"; next; }
  if (!$rating{$b[0]}) { $rating{$b[0]} = $tempRating{$b[0]} = $defaultRating; printDbug("resetting $b[0]\n"); }
  if (!$rating{$b[1]}) { $rating{$b[1]} = $tempRating{$b[1]} = $defaultRating; printDbug("resetting $b[1]\n"); }
  $mult = ($rating{$b[1]} - $rating{$b[0]})/400;
  $expWins = 1/(1+10**($mult));
  #printDbug("Expected wins for $b[0] vs $b[1] rating $rating{$b[0]} rating $rating{$b[1]} = $expWins\n");
  $expPoints = $pointsPerWin*(1 - $expWins * 1);
  #printDbug("$b[0] gains $expPoints\n$b[1] loses $expPoints\n");
  $tempRating{$b[0]} += $expPoints;
  $tempRating{$b[1]} -= $expPoints;
}

my $totalDelt = 0;
my $maxDelt = 0;
my $curDelt = 0;
foreach $x (keys %rating)
{
  if ($dBug || $maxTotalShift || $maxSingleShift)
  {
  $curDelt = abs($rating{$x} - $tempRating{$x});
  if ($curDelt > $maxDelt) { $maxDelt = $curDelt; }
  $totalDelt += $curDelt;
  }
  $rating{$x} = $tempRating{$x};
}
if ($dBug)
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
sub printDbug
{
  if (!$dBug) { return; }
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
  if ($a =~ /\t/) # the big ten website has tables, which cut-paste to tabs. Otherwise, we can make files with "WINNER, LOSER"
  {
  $a =~ s/.*201[67][ \t]*//;
  $a =~ s/^[ \t]*//;
  $a =~ s/\t.*//;
  $a =~ s/ *\(OT\)//;
  $a =~ s/ *[0-9]+, */,/;
  $a =~ s/ *[0-9]+ *$//;
  }
  @q = split(/,/, $a);
  if (defined($rating{$q[0]}) && defined($rating{$q[1]}))
  {
    if ($q[0] eq $q[1])
	{
	  print("$q[0] playing themselves at line $. ignored. A team can only figuratively beat itself.\n");
	  next;
    }
    push(@allGames, $a);
	$wins{$q[0]}++;
	$losses{$q[1]}++;
  }
}
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
    if ($dBug) { print "$team has no wins.\n"; }
	$allwin++; $losses{$team} = $fudgefactor; $wins{$team}  -= $fudgefactor;
  }
  elsif ($losses{$team} == 0)
  {
    if ($dBug) { print "$team has no losses.\n"; }
	$allloss++; $wins{$team} -= $fudgefactor; $losses{$team}  = $fudgefactor;
  }
  else { $wins{$team} -= $delta; $losses{$team} += $delta; }
}

if ($dBug)
{
print "Fudge factor = $fudgefactor, delta = $delta\n";
for my $t (@teams) { print "$t: $wins{$t}-$losses{$t}\n"; }
}
}

###################reads teams and their short names--short names are handy if we are exporting to an HTML table and want to keep it narrow
# e.g. names like "Northwestern" make a column really wide
sub readTeamNicknames
{
open(A, "elonick.txt") || die ("Can't open elonick.txt");
my @b;
while ($a = <A>)
{
  if ($a =~ /^;/)
  { last; }
  chomp($a);
  @b = split(/,/, $a);
  push(@teams, $b[0]);
  if ($#b > 0) { $nickname{$b[0]} = $b[1]; }
}
@teams = sort(@teams);
for (@teams) { $rating{$_} = $defaultRating; $wins{$_} = 0; $losses{$_} = 0; }

}

sub usage
{
print<<EOT;
-d is debug rating
-de means send debug information every X iterations
-f sets the fudge factor for winless/undefeated teams so their ratings aren't undefined (currently .1 of a game, max .5)
-i changes number of iterations
-m is the minimum total rating shift to try another iteration
-m1 is the minimum maximum rating shift by any one team to try another iteration
-ni changes the nickname file
-p/-w changes the points per win
-r changes the default rating, which is usually 2000 (expert)
-re/-g is the game result file
EOT
exit;
}

# future options:
# * table or no
# * check what total ratings sum to and bring everything back to the original average
# also, create a hash of win numbers for each side, as well as their schedule. @allGames contains nonconference games at the moment.