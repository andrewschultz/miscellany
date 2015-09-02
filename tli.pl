################################
#TLI.PL
#Lists the tables in an inform file, along with the sections they're in
#
#Usage: no arguments now. You have to go to the relevant directory.
#

open(A, "story.ni") || die ("No story file.");

@s = ("volume", "book", "part", "chapter", "section");

while ($a = <A>)
{
  $line++;
  $a =~ s/[\n\r]//g;
  for (0..$#s)
  {
  if ($a =~ /^@s[$_] /i)
  {
    for $x ($_..$#s)
    {
      $ti{@s[$x]} = "";
      #print "Wiping @s[$x] ($x) at $a\n";
    }
    $ti{@s[$_]} = $a;
  }
  }

  if (($a =~ /^table of /) && ($a !~ /\t/))
  {
    $a =~ s/ *\[.*//g;
    $comma = 0;
    print "$a ($line):\n    ";
    for (0..$#s)
    {
      if ($ti{@s[$_]})
      { if ($comma) { print ","; } print " $ti{@s[$_]}"; $comma = 1;}
    }
    print "\n";
  }
}