#$procString="shu,roi,sts";

$ght = "c:/writing/scripts/gh.txt";

preProcessHashes();

$justPrint = 0;

$gh = "c:\\users\\andrew\\Documents\\github";

if (@ARGV[0] eq "-j") { shift(@ARGV); $justPrint = 1; }

if (@ARGV[0])
{
  if ($altHash{@ARGV[0]})
  { $procString = $altHash{@ARGV[0]}; }
  else
  { $procString = @ARGV[0]; }
}
else
{ print "Default string: $procString\n"; }

findTerms();

@procAry = split(/,/, $procString);

for (@procAry)
{
  if ($_ eq "-a")
  { $alph = 1; next; }
  if ($altHash{$_}) { $do{$altHash{$_}} = 1; print "$_ => $altHash{$_}\n"; }
  else
  {
  $do{$_} = 1;
  }
}

for $k (sort keys %poss) { if ($k =~ /,/) { print "$k is a valid key and maps to multiple others.\n"; } else { print "$k is a valid key.\n"; } }

processTerms();

sub processTerms
{
  open(A, $ght) || die ("No $ght");
  while ($a = <A>)
  {
    chomp($a);
    $b = $a;
    $b =~ s/=.*//g;
    if ($do{$b})
    {
	  $didOne = 1;
      $c = $a; $c =~ s/.*=//g; @d = split(/,/, $c);
      $cmd = "copy \"@d[0]\" $gh\\@d[1]";
	  if ($justPrint) { print "$cmd\n"; } else { `$cmd`; }
#      `$cmd`;
    }
  }
  if (!$didOne) { print "Didn't find anything for $procString."; }
}

##########################
# finds all valid terms

sub findTerms
{
open(A, $ght) || die ("Oops, couldn't open gh.txt.");

while ($a = <A>)
{
  chomp($a);
  if ($a =~ /~/) { next; } #congruency
  if ($a =~ /^d:/) { next; } #default
  if ($a =~ /^;/) { last; }
  if ($a =~ /^#/) { next; }
  if ($a !~ /[a-z]/i) { next; }
  $a =~ s/=.*//g;
  $poss{$a} = 1;
}

close(A);
}

sub preProcessHashes
{
  open(A, "$ght") || die ("Can't open $ght.");
}