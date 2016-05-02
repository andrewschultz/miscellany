########################################
#unch.pl
#un-checked-in changes in GIT
#run nightly

use POSIX;

if (@ARGV[0] eq "-t") { $test = 1; }

@projAry = ("threediopolis", "ectocomp", "fourdiopolis", "stale-tales-slate", "the-problems-compound", "slicker-city", "misc", "ugly-oafs", "dirk", "trizbort");

$gitRoot = "c:\\users\\andrew\\documents\\github";

for $dir (@projAry)
{
checkProject($dir);
}

sub checkProject
{
  chdir("$gitRoot\\$_[0]");
  $tempString = `git status -s`;
  if ($tempString) { $bigString .= "$_[0]:\n$tempString"; }
}

@errfiles = split(/\n/, $bigString);
{
  for (@errfiles) { if ($_ =~ /:$/) { $proj++; } else { $file++; } }
}

if (!$test)
{
  print $bigString;
}
else
{
  $bigString =~ s/\n/<br \/>/g;
  print "TEST RESULTS:unchecked in files,4,$file,0,$bigString\n";
}
