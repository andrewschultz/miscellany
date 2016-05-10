##################################
#salf.pl
#section alphabetizer
#
# currently only for games.otl but it can be expanded
#
# usage salf.pl 
#
# recommended: salf.pl pc, salf.pl sc

use Data::Dumper qw(Dumper);
use List::MoreUtils qw(uniq);

if (!@ARGV[0]) { print ("Need alphabetical to sort, or -pc for all of PC"); }

@sects = split(/,/, @ARGV[0]);

if (@ARGV[0] eq "-pc")
{
  @sects=split(/,/, "pc,sc,sc1,sc2,sc3,sc4,scfarm,sce,scd,scc,scb,sca");
}

$infile = "c:\\writing\\games.otl";
$outfile = "c:\\writing\\temp\\games.otl";

open(A, "$infile");
open(B, ">$outfile");

while ($a = <A>)
{
  print B $a;
  if ($a =~ /^\\/)
  {
    for $mysect (@sects)
	{
	  if ($a =~ /^\\$mysect[=\|]/) { alfThis(); }
	}
  }
}

close(A);
close(B);

if ((-s $infile) != (-s $outfile))
{
  print "Uh oh, $infile and $outfile didn't match sizes. Bailing.\n";
  print "" . (-s $infile) . " for $infile, " . (-s $outfile) . " for $outfile.\n";
  exit;
}

$cmd = "copy $outfile $infile";
print "$cmd\n";
`$cmd`;

sub alfThis
{
  my @lines = ();
  my @uniq_no_case = ();
  
  while ($a = <A>)
  {
    chomp($a);
    if ($a !~ /[a-z0-9]/i)
    {
      print "Last line $lines[-1]\n";
      last;
    }
    push(@lines, $a);
  }
  @x = sort { "\L$a" cmp "\L$b" } @lines;

  for $y (@x)
  {
    if ($got{lc($y)} == 1) { print "Duplicate $y\n"; next; }
	$got{lc($y)} = 1;
	push(@uniq_no_case, $y);
  }


  print B join("\n", @uniq_no_case) . "\n";
  print B "$a\n";
  print "$#lines ($#uniq_no_case unique) shuffled\n";
  return;
}