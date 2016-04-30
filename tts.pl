$long{"roil"} = "roiling";
$long{"roi"} = "roiling";
$long{"ro"} = "roiling";
$long{"r"} = "roiling";
$long{"s"} = "sa";
$long{"sa"} = "sa";
$long{"12"} = "sa";
$long{"13"} = "threediopolis";
$long{"3"} = "threediopolis";
$long{"3d"} = "threediopolis";
$long{"14"} = "uglyoafs";
$long{"15"} = "compound";
$long{"pc"} = "compound";
$long{"4"} = "fourdiopolis";
$long{"4d"} = "fourdiopolis";
$long{"sc"} = "slicker-city";

$endspace = 0;

chooseFile("c:/games/inform/@ARGV[0].inform/Source/story.ni");
chooseFile("c:/games/inform/$long{@ARGV[0]}.inform/Source/story.ni");
chooseFile("story.ni");

if (!$myFile) { die("No story.ni, and no abbreviation leads to it."); }

open(A, "$myFile");

while ($a = <A>)
{
  if ($a =~ /[\t ]+$/) { $endspace++; }
}
close(A);

print "TEST RESULTS:$long{@ARGV[0]} whitespace,orange,$endspace,0,none\n";

if ($endspace == 0) { exit; }

if (@ARGV[1])
{
  my $tempwhite = "c:\\games\\inform\\tempwhite.txt";
  open(A, "$myFile");
  open(B, ">$tempwhite");
  while ($a = <A>) { $b = $a; $b =~ s/[ \t]+$//g; print B $b; }
  close(A);
  close(B);
  `xcopy /y $tempwhite \"$myFile\"`;
}
else
{
if ($endspace > 0) { print "Run with a 2nd argument to zap whitespace.\n"; }
}

sub chooseFile
{
  if ((!$myFile) && (-f "$_[0]")) { $myFile = $_[0]; print "New file: $_[0]\n"; }
}