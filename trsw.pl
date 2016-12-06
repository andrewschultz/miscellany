#################################
#
# trsw = trizbort switch
#

if ($#ARGV < 0) { die ("Need CSVs of ids to flip."); }

my $copyBack = 0;

my $count = 0;
my %matchups;
my %long;

$long{"btp"} = "buck-the-past";
$long{"sc"} = "slicker-city";
$long{"pc"} = "compound-directors-cut";

my $trdr = "c:\\games\\inform\\triz\\mine";

my $file = "buck-the-past.trizbort";

while ($count <= $#ARGV)
{
  $a1 = $ARGV[$count];
  for ($a1)
  {
  /^-?d$/ && do { diagnose(); exit(); };
  /^-?ca?$/ && do { $copyBack = 1; if ($a1 =~ /a/) { $diagAfter = 1; } $count++; next; };
  /^-?n$/ && do { $copyBack = 0; $count++; next; };
  /^-?o$/ && do { $order = 1; $count++; next; };
  /^-?da$/ && do { $diagAfter = 1; $count++; next; };
  if ($long{$a1}) { $file = $long{$a1} . ".trizbort"; $count++; next; }
  /^[0-9,]+$/ && do {
  @j = split(/,/, $a1);
  for (0..$#j)
  {
    $q = ($_+1) % ($#j+1);
	if ($q == $j[$_]) { die("$q mapped to itself."); }
    if ($matchups{$j[$_]}) { die("$j[$_] is mapped twice, bailing.\n"); }
    $matchups{$j[$_]} = $j[$q];
    #print "$j[$_] -> $j[$q], from $_ to $q.\n";
  }
  $count++; next;
  };

  print "$a1 is an invalid parameter.\n\n";
  usage();
  }
}

if ($order) { orderTriz(); }

if (keys %matchups == 0) { print "No matchups found to flip.\n"; exit; }

my $outFile = $file; $outFile =~ s/\./id\./g;

open(A, "$trdr\\$file");
open(B, ">$trdr\\$outFile");

while ($a = <A>)
{
  $thisLine = 0;
  $a =~ s/id=\"([0-9]+)\"/newNum($1)/ge;
  print B $a;
  $lineDif += $thisLine;
}

close(A);
close(B);

#print "$lineDif different lines, $idDif total changes.\n";

if ($copyBack)
{
print "Copying back $file.\n";
`copy /Y $trdr\\$outFile $trdr\\$file`;
if ($diagAfter) { diagnose(); exit(); }
} else
{
  print "-c to copy back $file.\n";
  `wm $trdr\\$outFile $trdr\\$file`;
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
  my $thisID;
  my $lastID;
  open(A, "$trdr\\$file");
  while ($line=<A>)
  {
  if ($line =~ /room id=\"/)
  {
    @q = split(/\"/, $line);
	push(@printy, "@q[1] -> @q[3] (@q[15])");
	$lastID = @q[1];
  }
  if ($line =~ /line id=\"/)
  {
    @q = split(/\"/, $line);
	push(@mylines, @q[1]);
  }
  }
  @printy = sort {$a <=> $b} (@printy);
  $lastID = 0;
  for (@printy)
  {
    $thisID = $_; $thisID =~s/ .*//g;
	if ($thisID - $lastID != 1) { $_ =~ s/ ->/ \* ->/; }
	$lastID = $thisID;
  }
  print join("\n", sort {$a <=> $b} (@printy)) . "\n";
  print "Lines: " . join(", ", sort {$a <=> $b} (@mylines));
}

sub orderTriz
{
  my $outFile = $file; $outFile =~ s/\./id\./g;
  my $toFile = 1;
  my @ids;
  my $curStr = "";
  open(A, "$trdr\\$file");
  open(B, ">$trdr\\$outFile");
  while ($line = <A>)
  {
    if ($toFile)
	{
	  print B $line;
      if ($line =~ /<map>/) { $toFile = 0; }
	  next;
	}
    if ($line =~ /<\/map>/)
	{
	  $toFile = 1;
	  print B join("\n", sort { idnum($a) <=> idnum($b) } @ids);
	  print "" . ($#ids+1) . " total.\n";
	  print B "\n$line";
	  next;
    }
	if ($line =~ /<(room|line).*\/>/)
    {
      print "Self closing tag: $line";
	  chomp($line);
	  push (@ids, $line);
	  next;
	}
	if ($line =~ /<\/(room|line)>/) { chomp($line); }
	$curStr .= $line;
	if ($line =~ /<\/(room|line)>/) { push(@ids, $curStr); $curStr = ""; }
  }
  close(A);
  close(B);
  `copy /Y $trdr\\$outFile $trdr\\$file`;
}

sub idnum
{
  my $id = $_[0];
  $id =~ s/.*id=\"//g;
  $id =~ s/\".*//g;
  return $id;
}

sub usage
{
print<<EOT;
-c = copy
-d = diagnose (show all rooms)
btp pc sc = projects
EOT
exit()
}