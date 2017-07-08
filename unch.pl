########################################
#unch.pl
#un-checked-in changes in GIT
#run nightly
#
#-h gives HTML
#-t gives test results
#-l lists default values
#
#-a may, in the future, list all my github subdirectories

use warnings;
use strict;

use POSIX;

my %exp = ( "3d" => "threediopolis",
  "4d" => "fourdiopolis",
  "ec" => "ectocomp",
  "sa" => "stale-tales-slate",
  "roi" => "stale-tales-slate",
  "pc" => "the-problems-compound",
  "sc" => "slicker-city",
  "uo" => "ugly-oafs",
  "tr" => "trizbort"
);

my %projs;
my @projAry = ("threediopolis", "ectocomp", "fourdiopolis", "stale-tales-slate", "the-problems-compound", "slicker-city", "misc", "ugly-oafs", "dirk", "trizbort", "writing", "seeker-status", "curate");

#####################variables
my $count = 0;
my $bigString = "";

#######################options
my $html = 0;
my $file = 0;
my $proj = 0;
my $test = 0;

while ($count <= $#ARGV)
{
  my $arg = $ARGV[$count];
  for ($arg)
  {
    /^-?l$/ && do { for (@projAry) { print "$_\n"; } exit(); };
    /^-?t$/ && do { $test = 1; $count++; next; };
    /^-?h$/ && do { $html = 1; $count++; next; };
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
  print "TEST RESULTS:unchecked in projects (unch.pl),4,$file,0,$bigString\n";
  my $projLeft = join(" &amp; ", sort keys %projs);
  print "TEST RESULTS:unchecked in files,2,$proj,0,$projLeft\n";
  print "gh.pl -all copies everything over, gh.pl -alb only public stuff.";
}

if ($html)
{
  my $htmlString = $bigString;
  my $hfile = 'c:\writing\scripts\unch.htm';
  $htmlString =~ s/\n/<br \/>\n/g;
  $htmlString .= "<br />gh.pl -all copies everything over, gh.pl -alb only public stuff.";
  open(H, ">$hfile");
  print H "<html>\n<title>Unchanged Files</title>\n<body>$htmlString</body></html> ";
  close(H);
  `$hfile`;
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
-h creates and runs an html file
EOT
exit;
}