##############################
#fl.pl = last-or-first 
#
#this looks through my files of first or last names and prints out what's there

if (!$ARGV[0]) { die ("Need a string to search. It can be a regex."); }

##############################
#DOS is crusty about using ^'s
##############################
$search = $ARGV[0]; if ($search =~ /^!/) { $search =~ s/!/\^/; }

goThru("c:\\writing\\dict\\firsts.txt", $search);
goThru("c:\\writing\\dict\\lasts.txt", $search);

sub goThru
{
my $anyYet = 0;

open(A, "$_[0]") || die ("Can't open $_[0]");

while ($a = <A>)
{
  if ($a =~ /$_[1]/i) { if (!$anyYet) { print "$_[0]:\n"; $anyYet = 1; } print "$a"; }
}

if (!$anyYet) { print "Nothing in $_[0].\n"; }
}