open(A, "c:\\writing\\games.otl");

my $gotOne = 0;

if ($#ARGV < 1) { die ("Need an argument and a number: 1 to delete 1 #, 0 to delete only if they're all there, 2 to delete them all."); }

$searchstring = @ARGV[0];

open(B, ">c:\\writing\\temp\\games.otl");
while ($a = <A>)
{
  print B $a;
  if ($a =~ /^\\$searchstring[\|=]/)
  { commentProcess(); $gotOne = 1; }
}

close(A);
close(B);

if ($gotOne == 0) { print "Didn't find anyone!\n"; die; }

if ($ARGV[2]) { print "Copying over.\n"; `copy /y \\writing\\games.otl \\writing\\temp\\games.otl`; }
else { print "Comparing.\n"; `wm \\writing\\games.otl \\writing\\temp\\games.otl`; }

sub commentProcess
{
  my @toComment = ();

  if ($ARGV[1] == 2)
  {
    while ($a = <A>) { $a =~ s/^#*//; print B $a; if ($a !~ /[a-z0-9]/i) { last; } }
  }
  elsif ($ARGV[1] == 1)
  {
    while ($a = <A>) { $a =~ s/^#//; print $a; print B $a; if ($a !~ /[a-z0-9]/i) { last; } }
  }
  elsif ($ARGV[1] == 0)
  {
    $allComment = 1;
    while ($a = <A>)
    {
      push (@toComment, $a);
      if ($a !~ /[a-z0-9]/i) { last; }
      if ($a !~ /^#/) { $allComment = 0; print "Uncommented: $a"; }
    }
    for $co (@toComment)
    {
      if ($allComment) { $co =~ s/^#//; }
      print B $co;
    }
  }
  
}