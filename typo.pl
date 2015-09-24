open(A, "story.ni") || die ("Need to run from a directory with a story.ni.");
open(B, ">stotext.txt");

#define command line arguments later.
$ignorebracket = 1;
$openAfter = 1;
$bracketText = "/";

while ($a = <A>)
{
  if ($a =~ /\"/)
  {
    $b = $a;
    $b =~ s/^[^\"]*\"(.*)\".*/$1/g;
	if ($ignorebracket) { $b =~ s/\[[^\]]+\]/$bracketText/g; }
    print B "$b";
  }
}

close(A);
close(B);

print "Story text written out to stotext.txt.";
if ($openAfter) { `stotext.txt`; }