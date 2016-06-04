package i7proj;
use strict;
use warnings;
use Exporter qw( import );
our @EXPORT = qw( findProj %proj %gotProj );
our %proj;
our %gotProj;

open(A, "c:\\writing\\scripts\\proj.txt") || die ("No such file proj.txt. Check proj.pm.");

sub findProj
{
while (my $line = <A>)
{
  if ($line =~ /^#/) { next; }
  if ($line =~ /=/)
  {
    chomp($line);
    my @equiv = split(/=/, $line);
    my @left = split(/,/, $equiv[0]);
    my @right = split(/,/, $equiv[1]);
    for my $l (@left)
    {
      for my $r (@right)
      {
        $proj{$l} = $r;
		$gotProj{$r} = 1;
      }
    }
  }
  if ($line =~ /^;/) { last; }
}
}

1;