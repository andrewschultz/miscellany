open(A, "story.ni");
open(B, ">tables.i7");

while ($a = <A>)
{
  if ($a =~ /^table/) { $table = 1; $tables++; $curTable = $a; chomp($curTable); $tableCount = -3; }
  if ($table) { print B $a; $count++; $tableCount++; }
  if ($a !~ /[a-z]/) { if ($table) { $tableList .= "$curTable: $tableCount rows\n"; } $table = 0; }
}

$sum = "$tables tables, $count lines.\n$tableList";

print $sum;

print B $sum;
close(A);
close(B);
