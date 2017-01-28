################################
#
# elo.pl
#
# calculates the ELO of all the teams or whatever
#
# I am copying from http://www.bigten.org/library/stats/mbb-schedule.html
#
#so anything of the form date \tab Winners xxx, Losers xxx should work

#use strict;
#use warnings;

my %rating;
my %tempRating;

#defaults
my $count = 0;
my $dBug = 0;
my $iterations = 2000;
my $pointsPerWin = 32;
my $defaultRating = 2000;

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
  $a = @ARGV[$count];
  $b = @ARGV[$count+1];
  for ($a)
  {
    /-r/ && do { $defaultRating = $b; $count += 2; next; };
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
  push(@allGames, $a);
}

close(A);

my $count;
for ($count = 1; $count <= $iterations; $count++)
{
eloIterate();
}

foreach $x (sort keys %rating)
  {
    $rating{$x} = int($rating{$x} + .5);
  }

@sorted = sort { $rating{$b} cmp $rating{$a} } keys %rating;

$count=0; $tempCount = 0; $overallCount=0;

for (@sorted) {
  $overallCount++;
  $count += ($draftOrder{$_} ne "c");
  $tempCount = $count; if ($draftOrder{$_} eq "c") { $tempCount = ""; }
  #$tempCount = $overallCount;
  printf "%2s %10s $rating{$_} $draftOrder{$_}\n", $tempCount, $_;
  }

  print "<table><tr><td>";
  
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
foreach $x (keys %rating) { $tempRating{$x} = $rating{$x}; }

for (@allGames)
{
  @b = split(/[,]/, $_);
  #printf("@b[0] %d vs @b[1] %d\n", $rating{$b[0]}, $rating{$b[1]});
  unless (defined($rating{@b[0]}) && defined($rating{@b[1]})) { next; }
  if (!$rating{@b[0]}) { $rating{@b[0]} = $tempRating{@b[0]} = $defaultRating; printDbug("resetting @b[0]\n"); }
  if (!$rating{@b[1]}) { $rating{@b[1]} = $tempRating{@b[1]} = $defaultRating; printDbug("resetting @b[1]\n"); }
  $mult = ($rating{@b[1]} - $rating{@b[0]})/400;
  $expWins = 1/(1+10**($mult));
  #printDbug("Expected wins for @b[0] vs @b[1] rating $rating{@b[0]} rating $rating{@b[1]} = $expWins\n");
  $expPoints = $pointsPerWin*(1 - $expWins * 1);
  #printDbug("@b[0] gains $expPoints\n@b[1] loses $expPoints\n");
  $tempRating{@b[0]} += $expPoints;
  $tempRating{@b[1]} -= $expPoints;
}

my $totalDelt = 0;
foreach $x (keys %rating) { $totalDelt += abs($rating{$x} - $tempRating{$x}); $rating{$x} = $tempRating{$x}; }
printDbug("$totalDelt total rating shift for run $count.\n");

#foreach $x (sort keys %rating)
#  {
#    printDbug("$x $rating{$x}\n");
#  }
#printDbug("==============================\n");

}

sub winPct
{
  my $exp = ($rating{$_[1]} - $rating{$_[0]}) / 400;
  return 100/(1+10**$exp);
}

sub printDbug
{
  if (!$dBug) { return; }
  print $_[0];
}

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