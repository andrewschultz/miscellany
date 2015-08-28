$procString="shu,roi,sts";

$justPrint = 0;

$gh = "c:\\users\\andrew\\Documents\\github";

if (@ARGV[0] eq "-j") { shift(@ARGV); $justPrint = 1; }

if (@ARGV[0]) { $procString = @ARGV[0]; } else { print "Default string: $procString\n"; }

findTerms();

@procAry = split(/,/, $procString);

for (@procAry)
{
  if ($_ eq "-a")
  { $alph = 1; next; }
  $do{$_} = 1;
}

for $k (sort keys %poss) { print "$k is a valid key.\n"; }

processTerms();

sub processTerms
{
  open(A, "c:/writing/scripts/gh.txt") || die ("No c:/writing/scripts/gh.txt");
  while ($a = <A>)
  {
    chomp($a);
    $b = $a;
    $b =~ s/=.*//g;
    if ($do{$b})
    {
      $c = $a; $c =~ s/.*=//g; @d = split(/,/, $c);
      $cmd = "copy \"@d[0]\" $gh\\@d[1]";
	  if ($justPrint) { print "$cmd\n"; } else { `$cmd`; }
#      `$cmd`;
    }
  }
}

##########################
# finds all valid terms

sub findTerms
{
open(A, "gh.txt");

while ($a = <A>)
{
  chomp($a);
  if ($a =~ /^;/) { last; }
  if ($a =~ /^#/) { next; }
  if ($a !~ /[a-z]/i) { next; }
  $a =~ s/=.*//g;
  $poss{$a} = 1;
}

close(A);
}