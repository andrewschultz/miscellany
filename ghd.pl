#######################################
#ghd.pl: github documenter
#
#did I do something today?
#no arguments. Set to run at 11:30 PM.
#
#requires ghd.txt to see where to sort which projects
#
#BASE=c:\users\me\documents\github
#github=threediopolis
#bitbucket=fourdiopolis

use POSIX qw(strftime);
use Win32;

use strict;
use warnings;

########################hashes
my %repo;
my %repoSum;
my %count;
my %siteArray;

################options
my $debug = 0;
my $popup = 0;

#######################variables
my $count = 0;
my $ghBase = "";
my $popupText;
my $overallSum;
my $sum;
my $daysAgo = 0;

my $siteFile = __FILE__;
$siteFile =~ s/pl$/txt/i;

while ($count <= $#ARGV)
{
  my $arg = $ARGV[0];
  for ($arg)
  {
  /^-?d/ && do { $debug = 1; $count++; next; };
  /^-?p/ && do { $popup = 1; $count++; next; };
  /^-?\d+$/ && do { $daysAgo = $ARGV[0]; $daysAgo = abs($daysAgo); $count++; next; };
  /^-?\?/ && do { usage(); };
  print "Unknown cmd line parameter $arg\n";
  usage();
  }
}

$popupText = strftime "Results for %m/%d/%Y\n", localtime(time()-86400);

open(A, "$siteFile") || die("No $siteFile");
while ($a = <A>)
{
  chomp($a);
  if ($a =~ /^base=/i) { $a =~ s/^base=//i; $ghBase = $a; next; }
  my @b = split(/:/, $a);
  my @c = split(/,/, $b[1]);
  $siteArray{$b[0]} = \@c;
  for (@c) { $repo{$_} = $b[0]; }
}

close(A);

unless ($ghBase) { die ("Need BASE= in $siteFile."); }
unless (-d "$ghBase") { die ("$ghBase in $siteFile is not a valid directory."); }

my @repos = (@{$siteArray{"bitbucket"}}, @{$siteArray{"github"}});

my $r;
my $thisLog = "";
my $cmd = $daysAgo ? sprintf("git log --since=\"%d days ago\" --until=\"%d days ago\"", $daysAgo, $daysAgo - 1) : "git log --since=\"12 am\""; #yes, git log accepts "1 days ago" which is nice

print "Running on all dirs: $cmd\n";

for $r (@repos)
{
  chdir("$ghBase\\$r") or do { warn "fail $ghBase\\$r"; next; };
  $thisLog = `$cmd`;
  if ($debug) { print getcwd() . ": $cmd\n$thisLog"; }
  $count{$r} = () = $thisLog =~ /([\n]|^)commit/gi;
  $repoSum{$repo{$r}} += $count{$r};
}

for my $k (sort {$repo{$a} cmp $repo{$b} || $a cmp $b} keys %count) { if ($count{$k}) { $popupText .= "====$k($repo{$k}): $count{$k}\n"; } }
$popupText .= "Repos above, sites below\n";
for my $k (sort keys %repoSum)
{
  $popupText .= "====$k: $repoSum{$k}\n";
  if ((!$repoSum{$k}) && (!$daysAgo)) { `c:\\nightly\\see-$k.htm`; }
  $overallSum += $repoSum{$k} ? $repoSum{$k} - 1 : 0;
}

if ($overallSum) { $popupText .= "====$overallSum total extra changes\nRun UNCH.PL to see if there are any more to commit/push."; }

if ($popup)
{
Win32::MsgBox("$popupText",0,"GHD.PL");
}
else
{
print "$popupText";
}

#######################################
#subroutines

sub usage
{
print<<EOT;
==========basic usage==========
-d debug
-p pop up results
-(#) how many days back (default = 0, today)
EOT
exit();
}