########################################
#unch.pl
#un-checked-in changes in GIT
#run nightly

use warnings;
use strict;

use POSIX;

my %exp;
my %projs;
my @projAry = ("threediopolis", "ectocomp", "fourdiopolis", "stale-tales-slate", "the-problems-compound", "slicker-city", "misc", "ugly-oafs", "dirk", "trizbort", "writing");

$exp{"3d"} = "threediopolis";
$exp{"4d"} = "fourdiopolis";
$exp{"ec"} = "ectocomp";
$exp{"sa"} = "stale-tales-slate";
$exp{"roi"} = "stale-tales-slate";
$exp{"pc"} = "the-problems-compound";
$exp{"sc"} = "slicker-city";
$exp{"uo"} = "ugly-oafs";
$exp{"tr"} = "trizbort";

my $count = 0;
my $bigString = "";

my $file = 0;
my $proj = 0;
my $test = 0;

while ($count <= $#ARGV)
{
  $a = $ARGV[$count];
  for ($a)
  {
    /^-?t$/ && do { $test = 1; $count++; next; };
	/^[a-z]/ && do { @projAry = split(/,/, $b); $count += 2; next; };
	usage();
  }
}

my $gitRoot = "c:\\users\\andrew\\documents\\github";

for my $dir (@projAry)
{
checkProject($dir);
}

my @errfiles = split(/\n/, $bigString);
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
  print "TEST RESULTS:unchecked in projects,4,$file,0,$bigString\n";
  my $projLeft = join("/", sort keys %projs);
  print "TEST RESULTS:unchecked in files,2,$proj,0,$projLeft\n";
}

###########################subroutines

sub checkProject
{
  my $subdir = $_[0];
  if ($exp{$subdir}) { $subdir = $exp{$subdir}; }
  if (-d "$gitRoot\\$subdir")
  {
  chdir("$gitRoot\\$subdir");
  }
  else
  {
  print "Couldn't find subdir $subdir.\n";
  }
  my $tempString = `git status -s`;
  if ($tempString) { $bigString .= "$subdir:\n$tempString"; $projs{$subdir} = 1; }
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