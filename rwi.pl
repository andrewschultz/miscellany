###################################
#
#rwi.pl
#
#find rule with (string) in it
#

$openAfter = 1;

open(A, "story.ni") || die ("No story.ni.");
open(B, ">rwi.txt") || die ("Unwritable rwi.txt.");

while ($a = <A>)
{
  $line++;
  if (($a =~ /^[a-z]/) && ($a =~ /@ARGV[0].*:/))
  {
    print B "Line $line:\n";
    $gotRule = 1;
  }
  if ($gotRule) { print B $a; }
  if ($a !~ /[a-z]/) { $gotRule = 0; }
}

close(A);
close(B);

if ($openAfter) { `rwi.txt`; }