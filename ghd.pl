#######################################
#ghd.pl: github documenter
#did I do something today?
#no arguments. Set to run at 11:30.

use POSIX qw(strftime);
use Win32;

use strict;
use warnings;

my %repo;
my %repoSum;
my %count;
my %siteArray;
my $popup = strftime "Results for %m/%d/%Y\n", localtime;

my $ghbase = "c:\\Users\\Andrew\\Documents\\GitHub";

my $sum;

my $siteFile = __FILE__;
$siteFile =~ s/pl$/txt/i;

open(A, "$siteFile") || die("No $siteFile");
while ($a = <A>)
{
  chomp($a);
  my @b = split(/:/, $a);
  my @c = split(/,/, $b[1]);
  $siteArray{$b[0]} = \@c;
  for (@c) { $repo{$_} = $b[0]; }
}

close(A);

my @repos = (@{$siteArray{"bitbucket"}}, @{$siteArray{"github"}});

my $r;
my $thislog;

for $r (@repos)
{
  chdir("$ghbase\\$r") or do { warn "fail $ghbase\\$r"; next; };
  $thislog = `git log --since="12am"`;
  $count{$r} = () = $thislog =~ /^commit/gi;
  $repoSum{$repo{$r}} += $count{$r};
}

for my $k (sort keys %count) { if ($count{$k}) { $popup .= "====$k($repo{$k}): $count{$k}\n"; } }
$popup .= "Repos above, sites below\n";
for my $k (sort keys %repoSum)
{
  $popup .= "====$k: $repoSum{$k}\n";
  if (!$repoSum{$k}) { `c:\\nightly\\see-$k.htm`; }
}

Win32::MsgBox($popup);