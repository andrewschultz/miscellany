my $continue = 1;
my $count = 0;
my $myword = $ARGV[0];
my $toword = $ARGV[1];
my %ladder;
my %laddet;
my $l = length($myword);

if ($l != length($toword)) { die ("To and from must have same length."); }

$laddet{$myword} = $myword;

$myword = lc($myword);

if (defined($ARGV[2]))
{
  @x = split(/,/, @ARGV[2]);
  for (@x) { $ladder{lc($_)} = -2; }
}

open(A, "words-$l.txt");

while ($a = <A>)
{
  chomp($a); $a = lc($a);
  if ($a eq $myword) { $ladder{$a} = 0; }
  elsif (!defined($ladder{$a})) { $ladder{$a} = -1; }
}

while (($ladder{$toword} < 0) && ($continue == 1))
{
  $continue = 0;
  for my $w (keys %ladder)
  {
    if ($ladder{$w} != $count) { next; }
    for ($i = 0; $i < length($myword); $i++)
    {
      for $ltr ('a'..'z')
      {
        $temp = $w;
        substr($temp, $i, 1) = $ltr;
        if ($ladder{$temp} == -1) { $ladder{$temp} = $count + 1; $continue = 1; $laddet{$temp} = "$laddet{$w}-$temp"; }
      }
    }
  }
  $count++;
}

if (!$laddet{$toword}) { print "No word ladder found."; }
else
{
print $laddet{$toword} . " in " . $ladder{$toword} . " moves.";
}