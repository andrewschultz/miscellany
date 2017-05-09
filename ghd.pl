#######################################
#ghd.pl: github documenter
#
#did I do something today?
#no arguments. Set to run at 11:30 PM.
#
#requires ghd.txt
#
#BASE=c:\users\me\documents\github
#github=threediopolis
#bitbucket=fourdiopolis

use POSIX qw(strftime);
use Win32;

use strict;
use warnings;

my %repo;
my %repoSum;
my %count;
my %siteArray;
my $popupText = strftime "Results for %m/%d/%Y\n", localtime;

my $ghBase = "";

my $sum;

my $siteFile = __FILE__;
$siteFile =~ s/pl$/txt/i;

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
my $thisLog;

for $r (@repos)
{
  chdir("$ghBase\\$r") or do { warn "fail $ghBase\\$r"; next; };
  $thisLog = `git log --since="12am"`;
  $count{$r} = () = $thisLog =~ /([\n]|^)commit/gi;
  $repoSum{$repo{$r}} += $count{$r};
}

for my $k (sort {$repo{$a} cmp $repo{$b} || $a cmp $b} keys %count) { if ($count{$k}) { $popupText .= "====$k($repo{$k}): $count{$k}\n"; } }
$popupText .= "Repos above, sites below\n";
for my $k (sort keys %repoSum)
{
  $popupText .= "====$k: $repoSum{$k}\n";
  if (!$repoSum{$k}) { `c:\\nightly\\see-$k.htm`; }
}

Win32::MsgBox($popupText);