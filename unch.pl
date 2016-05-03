########################################
#unch.pl
#un-checked-in changes in GIT
#run nightly

use POSIX;

@projAry = ("threediopolis", "ectocomp", "fourdiopolis", "stale-tales-slate", "the-problems-compound", "slicker-city", "misc", "ugly-oafs", "dirk", "trizbort");

$exp{"3d"} = "threediopolis";
$exp{"4d"} = "fourdiopolis";
$exp{"ec"} = "ectocomp";
$exp{"sa"} = "stale-tales-slate";
$exp{"roi"} = "stale-tales-slate";
$exp{"pc"} = "the-problems-compound";
$exp{"sc"} = "slicker-city";
$exp{"uo"} = "ugly-oafs";
$exp{"tr"} = "trizbort";

while ($count <= $#ARGV)
{
  $a = @ARGV[$count];
  for ($a)
  {
    /^-t$/ && do { $test = 1; $count++; next; };
	/^[a-z]/ && do { @projAry = split(/,/, $b); $count += 2; next; };
	usage();
  }
}

$gitRoot = "c:\\users\\andrew\\documents\\github";

for $dir (@projAry)
{
checkProject($dir);
}

sub checkProject
{
  $subdir = $_[0];
  if ($exp{$subdir}) { $subdir = $exp{$subdir}; }
  if (-d "$gitRoot\\$subdir")
  {
  chdir("$gitRoot\\$subdir");
  }
  else
  {
  print "Couldn't find subdir $subdir.\n";
  }
  $tempString = `git status -s`;
  if ($tempString) { $bigString .= "$subdir:\n$tempString"; }
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

sub usage
{
print<<EOT;
-t says this outputs test results
CSV tells projects to run
-l lists the default that is run
EOT
exit;
}