########################################
# lnct.pl = LiNe CounT.pl
# simply counts the remaining lines to process in games.otl
#

open(A, "c:/writing/games.otl");

$totalLines = 0;

if (!$ARGV[0]) { die("Need an ARG string to look for in otl file."); }

$lookFor = @ARGV[0];

while ($a = <A>)
{
  $lines++;
  if ($a !~ /[a-z]/i)
  {
    #if ($counting) { print "Last line $a"; }
    $counting = 0; next;
  }
  if ($a =~ /^\\$lookFor[=\|]/i) { print "Start with $a"; $everFound = 1; $counting = 1; next; }
  if ($counting) { $totalLines++; }
}

if (!$everFound) { die "Oops! Never tripped \\$lookFor.\n"; }
print "TEST RESULTS:games.otl lines for $lookFor,3,$totalLines,0,<a href=\"file:///c:/writing/games.otl\">OTL file</a>\n";

close(A);