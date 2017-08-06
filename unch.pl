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

use lib "c:\\writing\\scripts";

use i7;
use warnings;
use strict;

use POSIX;

my $alphabetical = 0;

my %exp = ( "3d" => "threediopolis",
  "4d" => "fourdiopolis",
  "ec" => "short-games",
  "short" => "short-games",
  "sa" => "stale-tales-slate",
  "roi" => "stale-tales-slate",
  "pc" => "the-problems-compound",
  "sc" => "slicker-city",
  "ss" => "seeker-status",
  "cu" => "curate",
  "uo" => "ugly-oafs",
  "tr" => "trizbort"
);

my %projs;
# note that the bottom projects are the most important as they are least likely to go off the page
my @projAry = (@i7gh, "seeker-status", "curate");

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
    /^-?a$/i && do { $alphabetical = 1; $count++; next; };
    /^-?l$/i && do { for (@projAry) { print "$_\n"; } exit(); };
    /^-?t$/i && do { $test = 1; $count++; next; };
    /^-?h$/i && do { $html = 1; $count++; next; };
	/^[a-z]{2}/i && do { @projAry = split(/,/, $b); $count += 2; next; };
	usage();
  }
}

@projAry = sort(@projAry) if $alphabetical;
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
CSV tells projects to run or look at
-a alphabetizes instead of listing by priority
-l lists the default that is run
-h creates and runs an html file
-t has unch output test results
EOT
exit;
}