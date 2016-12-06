if ($#ARGV < 0) { die ("Need CSVs of ids to flip."); }

my $copyBack = 0;

my $count = 0;
my %matchups;

while ($count <= $#ARGV)
{
  $a1 = $ARGV[$count];
  for ($a1)
  {
  /^-?d$/ && do { diagnose(); exit; };
  /^-?c$/ && do { $copyBack = 1; $count++; next; };
  /^-?n$/ && do { $copyBack = 0; $count++; next; };
  /^[0-9,]+$/ && do {
  @j = split(/,/, $a1);
  for (0..$#j)
  {
    $q = ($_+1) % ($#j+1);
    if ($matchups{$j[$_]}) { die("$j[$_] is mapped twice, bailing.\n"); }
    $matchups{$j[$_]} = $j[$q];
    print "$j[$_] -> $j[$q], from $_ to $q.\n";
  }
  $count++;
  };

  usage();
  }
}

open(A, "buck-the-past.trizbort");
open(B, ">buck-the-past-id.trizbort");

while ($a = <A>)
{
  $thisLine = 0;
  $a =~ s/id=\"([0-9]+)\"/newNum($1)/ge;
  print B $a;
  $lineDif += $thisLine;
}

close(A);
close(B);

print "$lineDif different lines, $idDif total changes.\n";

if ($copyBack)
{
print "Copying back.\n";
`copy /Y buck-the-past-id.trizbort buck-the-past.trizbort`;
} else
{
  print "-c to copy back.\n";
  `wm buck-the-past.trizbort buck-the-past-id.trizbort`;
}

sub newNum
{
  #print "ARG:$_[0], $matchups{$_[0]}\n";
  if ($matchups{$_[0]})
  {
    $idDif++;
    $thisLine = 1;
    return "id=\"$matchups{$_[0]}\"";
  } else { return "id=\"$_[0]\""; }
}

sub diagnose
{
  open(A, "buck-the-past.trizbort");
  while ($line=<A>)
  {
  if ($line =~ /room id=\"/)
  {
    @q = split(/\"/, $line);
	push(@printy, "@q[1] -> @q[3]");
  }
  if ($line =~ /line id=\"/)
  {
    @q = split(/\"/, $line);
	push(@mylines, @q[1]);
  }
  }
  print join("\n", sort {$a <=> $b} (@printy)) . "\n";
  print "Lines: " . join(", ", sort {$a <=> $b} (@mylines));
}

sub usage
{
}