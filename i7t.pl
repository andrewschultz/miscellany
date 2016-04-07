open(A, "story.ni");
open(B, ">tables.i7");

while ($a = <A>)
{
  if ($a =~ /^table/) { $table = 1; $tables++; }
  if ($table) { print B $a; $count++; }
  if ($a !~ /[a-z]/) { $table = 0; }
}

$sum = "$tables tables, $count lines.";

print $sum;

print B $sum;
close(A);
close(B);
