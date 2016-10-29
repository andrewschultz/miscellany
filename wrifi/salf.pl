##################################
#salf.pl
#section alphabetizer
#
# currently only for games.otl but it can be expanded
#
# usage salf.pl 
#
# recommended: salf.pl pc, salf.pl sc, salf.pl btp

use Data::Dumper qw(Dumper);
use List::MoreUtils qw(uniq);

my $dupBytes = 0;

if (!@ARGV[0]) { print ("Need alphabetical to sort, or -btp for all of BTP. PC and SC are largely redundant."); exit; }

@sects = split(/,/, @ARGV[0]);

if (@ARGV[0] eq "-pc")
{
  @sects=split(/,/, "pc"
}
elsif (@ARGV[0] eq "sc-rej")
{
  @sects=split(/,/, "sc,sc1,sc2,sc3,sc4,scfarm,sce,scd,scc,scb,sca");
}
elsif (@ARGV[0] eq "btp")
{
  @sects=split(/,/, "btp-rej,btp,btp-dis,btp-book,btp1,btp2,btp3,btp4,btp-farm,btp-e,btp-d,btp-c,btp-b,btp-a");
}

if ($#sects == -1) { print "Need a CSV of sections, or use -pc for ProbComp.\n"; exit; }

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

if (!$didSomething) { print "Didn't sort anything!\n"; exit; }

if ((-s $infile) != ((-s $outfile) + $dupBytes))
{
  print "Uh oh, $infile and $outfile(+$dupBytes) didn't match sizes. Bailing.\n";
  print "" . (-s $infile) . " for $infile, " . (-s $outfile) . " for $outfile.\n";
  exit;
}

$cmd = "copy $outfile $infile";
print "$cmd\n";
`$cmd`;

sub alfThis
{
  $didSomething = 1;
  my @lines = ();
  my @uniq_no_case = ();
  %got = ();
  
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
  #@x = @lines;

  for $y (@x)
  {
    #if ($got{lc($y)} == 1) { print "Duplicate $y\n"; $dupBytes += length(lc($y))+1; $dupes++; print "$dupBytes/$dupes total.\n"; next; }
	$got{lc($y)} = 1;
	push(@uniq_no_case, $y);
  }


  print B join("\n", @uniq_no_case);
  if ($#uniq_no_case > -1) { print B "\n"; }
  print B "$a\n";
  print "$#lines ($#uniq_no_case unique) shuffled\n";
  return;
}