########################################
#wpb.pl
#
#prints out all "when play begins" stuff to wpb.txt
#

open(A, "story.ni") || die ("No story.ni");
open(B, ">wpb.txt");

while ($a = <A>)
{
  $lines++;
  if ($a =~ /when play begins/) { $tr = 1; print B "Line: $lines\n$a"; next; }
  if ($tr) { print B $a; }
  if ($a !~ /[a-z]/) { $tr = 0; }
}

close(A);
close(B);

print "WPB.TXT now has When Play Begins.\n";

if (@ARGV[0]) { `wpb.txt`; }