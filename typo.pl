###########################
#typo.pl
#
#this searches for typos in an I7 file's story text
#
#It's a bit crude--it takes everything between quotes and then removes everything between brackets
#

open(A, "story.ni") || die ("Need to run from a directory with a story.ni.");
open(B, ">stotext.txt");

#define defaults here
$ignorebracket = 1;
$openAfter = 1;
$bracketText = "/";

while ($count < $#ARGV)
{
  $a = @ARGV[$count];
  $b = @ARGV[$count+1];
  for ($a)
  {
  /-di/ && do { $ignorebracket = 0; $count++; next; };
  /-i/ && do { $ignorebracket = 1; $count++; next; };
  /-no/ && do { $openAfter = 0; $count++; next; };
  /-o/ && do { $openAfter = 1; $count++; next; };
  /-sp/ && do { $bracketText = " "; $count++; next; };
  /-e/ && do { $bracketText = ""; $count++; next; };
  /-sl/ && do { $bracketText = "/"; $count++; next; };
  usage();
  }
  $count++;
}

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

sub usage
{
print<<EOT;
-di don't ignore brackets
-i ignore brackets (default)
-no don't open after (default)
-o open after
-sp space replaces brackets
-e empty replaces brackets
-sl slash replaces brackets (default)
EOT
exit;
}