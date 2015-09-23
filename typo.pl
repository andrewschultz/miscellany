open(A, "story.ni");

while ($a = <A>)
{
  if ($a =~ /\"/)
  {
    $b = $a;
    $b =~ s/^[^\"]*\"(.*)\".*/$1/g;
    print "$b";
  }
}