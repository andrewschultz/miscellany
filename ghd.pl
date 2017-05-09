use POSIX qw(strftime);
use Win32;

my $popup = strftime "Results for %m/%d/%Y\n", localtime;

my $ghbase = "c:\\Users\\Andrew\\Documents\\GitHub";
my @bitbucket = ("buck-the-past", "slicker-city");
my @github = ("the-problems-compound", "misc", "threediopolis", "fourdiopolis");

my @repos = (@bitbucket, @github);

my $sum;

for (@bitbucket) { $repo{$_} = "bitbucket"; }
for (@github) { $repo{$_} = "github"; }

for $r (@repos)
{
  chdir("$ghbase\\$r") or die "fail $ghbase\\$r";
  $thislog = `git log --since="12am"`;
  $logs .= $thislog;
  $count{$r} = () = $thislog =~ /^commit/gi;
  $repoSum{$repo{$r}} += $count{$r};
}

for my $k (sort keys %count) { if ($count{$k}) { $popup .= "====$k: $count{$k}\n"; } }
$popup .= "Repos above, sites below\n";
for my $k (sort keys %repoSum)
{
  $popup .= "====$k: $repoSum{$k}\n";
  if (!$repoSum{$k}) { `c:\\nightly\\see-$k.htm`; }
}

Win32::MsgBox($popup);