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

#defaults, can be tweaked with options
my $dBug = 0;
my $iterations = 2000;
my $pointsPerWin = 32;
my $defaultRating = 2000;
my $debugEveryX = 0;

#variables
my $count = 0;
my @allGames = ();
my @q;

#this could be put in a text file, but for now, it's not. Teams/Nicknames could be a hash.
my @teams = ("Illinois", "Indiana", "Iowa", "Maryland", "Michigan", "Michigan State", "Minnesota", "Nebraska", "Northwestern", "Ohio State", "Penn State", "Purdue", "Rutgers", "Wisconsin");

my %nickname;
$nickname{"Indiana"} = "iu";
$nickname{"Illinois"} = "UI";
$nickname{"Iowa"} = "OMHR";
$nickname{"Maryland"} = "MD";
$nickname{"Michigan"} = "UM";
$nickname{"Michigan State"} = "MSU";
$nickname{"Minnesota"} = "MN";
$nickname{"Nebraska"} = "NEB";
$nickname{"Northwestern"} = "NW";
$nickname{"Ohio State"} = "O\$U";
$nickname{"Penn State"} = "PSU";
$nickname{"Purdue"} = "PUR";
$nickname{"Rutgers"} = "RUT";
$nickname{"Wisconsin"} = "UW";

for (@teams) { $rating{$_} = $defaultRating; }

while ($count <= $#ARGV)
{
  $a = $ARGV[$count];
  $b = $ARGV[$count+1];
  for ($a)
  {
    /-r/ && do { $defaultRating = $b; $count += 2; next; };
    /-de/ && do { $debugEveryX = $b; $count += 2; next; };
    /-d/ && do { $dBug=1; $count++; next; };
    /-i/ && do { $iterations = $b; $count += 2; next; };
    /-p/ && do { $pointsPerWin = $b; $count += 2; next; };
    usage();
  }
}
open(A, "elosc.txt");

while ($a = <A>)
{
  chomp($a);
  if ($a =~ /#/)
  {
    next;
  }
  if ($a =~ /;/) { last; }
  $a =~ s/.*201[67][ \t]*//;
  $a =~ s/^[ \t]*//;
  $a =~ s/\t.*//;
  $a =~ s/ *\(OT\)//;
  $a =~ s/ *[0-9]+, */,/;
  $a =~ s/ *[0-9]+ *$//;
  @q = split(/,/, $a);
  if (defined($rating{$q[0]}) && defined($rating{$q[1]}))
  {
    push(@allGames, $a);
  }
}

close(A);

for ($count = 1; $count <= $iterations; $count++)
{
eloIterate();
}

my $x;

foreach $x (sort keys %rating)
  {
    $rating{$x} = int($rating{$x} + .5);
  }

 my $rank = 0;

 print "<table>\n";
foreach $x (sort {$rating{$a} <=> $rating{$b}} keys %rating)
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
  if ($dBug)
  {
  $curDelt = abs($rating{$x} - $tempRating{$x});
  if ($curDelt > $maxDelt) { $maxDelt = $curDelt; }
  $totalDelt += $curDelt;
  print("$totalDelt total rating shift for run $count.\n");
  print("$maxDelt maximum rating shift for run $count.\n");
  }
  $rating{$x} = $tempRating{$x};
}

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

sub usage
{
print<<EOT;
-r changes the default rating, which is usually 2000 (expert)
-d is debug rating
-i changes number of iterations
-p changes the points per win
EOT
exit;
}

# future options: 1 table or no 2 show debug every X turns
# also, create a hash of win numbers for each side, as well as their schedule. @allGames contains nonconference games at the moment.