my $newDir = ".";
$tables = 0;
$count = 0;

while ($count <= $#ARGV)
{
  $a = @ARGV[$count];
  for ($a)
  {
    /,/ && do { @important = split(/,/, $a); $count++; next; };
    /[\\\/]/ && do { $newDir = $a; $count++; next; };
	usage();
  }
}

open(A, "$newDir/story.ni") || die ("$newDir/story.ni doesn't exist.");
open(B, ">tables.i7");

while ($a = <A>)
{
  if ($a =~ /^table/)
  {
    $table = 1; $tables++; $curTable = $a; chomp($curTable); $curTable =~ s/\[.*//g; $tableCount = -3;
	for $x (@important)
	{
	  if ($a =~ /\b$x\b/i) { $majorTable = 1; }
	}
  }
  if ($table) { print B $a; $count++; $tableCount++; }
  if ($a !~ /[a-z]/)
  {
    if ($table) { $tableList .= "$curTable: $tableCount rows\n"; } $table = 0;
	if ($majorTable) { $majorList .= "$curTable: $tableCount rows<br />"; } $majorTable = 0;
  }
}

$sum = "$tables tables, $count lines.\n$tableList";

print $sum;

print B $sum;
close(A);
close(B);

if ($majorList) { $majorList =~ s/,//g; print "TEST RESULTS:PC table count,0,0,0,$majorList"; }

sub usage
{
print<<EOT;
directory
csv = tables to highlight
EOT
exit;
}