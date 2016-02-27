################################################
#ru.pl
#
#finds where code text is in a rule, or a rule header

$inHead = 1;

while ($count <= $#ARGV)
{

$a = @ARGV[$count];
  print "Trying $count $a\n";

for ($a)
{
  /^-c/ && do { $inCode = 1; $count++; next; };
  /^-h/ && do { $inHead = 1; $count++; next; };
  if (@match[1]) { print "Only 2 search arguments allowed.\n"; exit; }
  elsif (@match[0]) { $match[1] = $a; }
  else { @match[0] = $a; }
  $count++;
}

}

open(A, "story.ni") || die ("No story.ni.");

while ($a = <A>)
{
  $line++;
  chomp($a);
  if ($a =~ /^[a-z]/) { chomp($a); $head = $a; if (($inHead) && itMatches($a)) { print "$line: $a\n"; } }
  elsif (itMatches($a))
  {
    print "$line: $a (found in $head)\n";
  }

  if ($a !~ /[a-z]/)
  {
    if ($thisValid) { print "$funcBlock\n"; }
    $funcBlock = "";
  }
  
}

sub itMatches
{
  if (($#match == 0) && ($a =~ /@match[0]/i)) { return 1; }
  if (($#match == 1) && ($a =~ /@match[0]/i) && ($a =~ /@match[1]/i)) { return 1; }
  return 0;
}