###############################################
#wlad.pl
#
#word ladder from argv[0] to argv[1] with argv[2+] (csv) ignored
#
#usage = wlad.pl him her hem
#should give solution with 4 alternates

use strict;
use warnings;

my $myword = $ARGV[0];
my $toword = $ARGV[1];
my $l = length($myword);

#####################
#ladder lengths and ladder details
my %ladder;
my %laddet;

######################
#variables
my $continue = 1;
my $count = 2;
my $temp;
my $i;
my $ltr;

if ($l =~ /\?/) { usage(); }

if (!defined($toword)) { die ("Need at least 2 arguments."); }

if ($l != length($toword)) { die ("To and from must have same length."); }

$laddet{$myword} = $myword;

$myword = lc($myword);

#disable anything that is listed after the first 2 entries
while (defined($ARGV[$count]))
{
  my @x = split(/,/, $ARGV[$count]);
  for (@x)
  {
	if (length($_) != length($myword)) { warn("$_ is not the same length as $myword.\n"); next; }
    $ladder{lc($_)} = -2;
  }
  $count++;
}

$count = 0;

open(A, "c:\\writing\\dict\\words-$l.txt");

while ($a = <A>)
{
  chomp($a); $a = lc($a);
  if ($a eq $myword) { $ladder{$a} = 0; }
  elsif (!defined($ladder{$a})) { $ladder{$a} = -1; }
}
close(A);

unless (defined($ladder{$myword})) { $ladder{$myword} = 0; print "Didn't find $myword in word list.\n"; }
unless (defined($ladder{$toword})) { $ladder{$toword} = -1; print "Didn't find $toword in word list.\n"; }

while (($ladder{$toword} < 0) && ($continue == 1))
{
  print "$count...\n";
  $continue = 0;
  for my $w (keys %ladder)
  {
    if ($ladder{$w} != $count) { next; }
    for ($i = 0; $i < length($myword); $i++)
    {
      for $ltr ('a'..'z')
      {
        $temp = $w;
        substr($temp, $i, 1) = $ltr;
        if (defined($ladder{$temp}) && ($ladder{$temp} == -1)) { $ladder{$temp} = $count + 1; $continue = 1; $laddet{$temp} = "$laddet{$w}-$temp"; }
      }
    }
  }
  $count++;
}

if (!$laddet{$toword}) { print "No word ladder found."; }
else
{
  my $alts = 0;
  print $laddet{$toword} . " in " . $ladder{$toword} . " moves.\n";
  print "Searching for alternates...\n";
  for ($i = 0; $i < length($myword); $i++)
  {
    for $ltr ('a'..'z')
    {
      $temp = $toword;
	  if (substr($temp, $i, 1) eq $ltr) { next; }
      substr($temp, $i, 1) = $ltr;
	  #print "$temp(?)\n";
      if (defined($ladder{$temp}) && ($ladder{$temp} == $count - 1)) { print "Alternate: $laddet{$temp}-$toword\n"; $alts++; }
    }
  }
  if (!$alts) { print "No alternates found.\n"; }
  else { print "Total found: " . ($alts+1) . "\n"; }
}

############################
#subroutine(s)

sub usage
{
print<<EOT;
First word = from
Second word = to
Third and future arguments (comma separated or not) = words to ignore
EOT
exit();
}