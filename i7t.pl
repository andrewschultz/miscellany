use POSIX;

my $newDir = ".";
my $project = "Project";
$tables = 0;
$count = 0;

if (getcwd() =~ /\.inform/) { $project = getcwd(); $project =~ s/\.inform.*//g; $project =~ s/.*[\\\/]//g; }

while ($count <= $#ARGV)
{
  $a = @ARGV[$count];
  for ($a)
  {
    /-t/ && do { $b = @ARGV[$count+1]; @important = split(/,/, $b); $count+= 2; next; };
    /-p/ && do { $b = @ARGV[$count+1]; $project = $b; $count+= 2; next; };
	/-s/ && do { if ($exp{$b}) { $project = $exp{$b}; } else { $project = $b; } next; };
    /[\\\/]/ && do { $newDir = $a; $count++; next; };
	usage();
  }
}

open(A, "$newDir/story.ni") || die ("$newDir/story.ni doesn't exist.");
open(B, ">tables.i7");

while ($a = <A>)
{
  if ($a =~ /^table /)
  {
    $table = 1; $tables++; $curTable = $a; chomp($curTable); $tableShort = $curTable;
	$curTable =~ s/ *\[.*//g; $tableCount = -3;
	$curTable =~ s/ - .*//g;
	if ($tableShort =~ /\[x/) { $tableShort =~ s/.*\[x/x/g; $tableShort =~ s/\]//g; } else { $tableShort = $curTable; }
	for $x (@important)
	{
	  if ($a =~ /\b$x\b/i) { $majorTable = 1; }
	}
  }
  if ($table) { print B $a; $count++; $tableCount++; }
  if ($a !~ /[a-z]/)
  {
    if ($table) { $tableList .= "$curTable: $tableCount rows\n"; } $table = 0; $rows{$tableShort} = $tableCount;
	if ($majorTable) { $majorList .= "$curTable: $tableCount rows<br />"; } $majorTable = 0;
  }
}

$sum = "$tables tables, $count lines.\n$tableList";

print $sum;

print B $sum;
close(A);
close(B);

open(A, "c:/writing/scripts/i7t.txt");

while ($a = <A>)
{
  chomp($a);
  @b = split(/\t/, $a);
  if (lc(@b[0]) ne lc($project)) { next; }
  open(F, @b[2]) || die ("Can't find @b[2].");
  
  my $size = "";
  
  if ($rows{@b[1]}) { $size = $rows{@b[1]}; } else { print "@b[1] has nothing.\n"; }
  
  @b[3] =~ s/\$\$/$size/g;
  print "Trying @b[3]\n";
  my $success = 0;
  while ($f = <F>)
  {
    #print "@b[3] =~ $f";
    if ($f =~ /@b[3]/) { $success = 1; last; }
  }
  close(F);
  if ($success) { print "@b[2] search for @b[3]PASSED:\n  $f\n"; } else { print "TEST RESULTS:$project-@b[3],0,1,0,Look <a href=\"file:///@b[2]\">here</a>\n"; }
}

if ($majorList) { $majorList =~ s/,//g; print "TEST RESULTS:$project table count,0,0,0,$majorList\n"; }

sub usage
{
print<<EOT;
directory
csv = tables to highlight
EOT
exit;
}