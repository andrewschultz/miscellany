#################################
#
# trsw.pl = trizbort switch
#
# sample usages
#       trsw.pl d ss
#       trsw.pl ca sc 2,3

use File::Compare;
use warnings;
use strict;

if ( $#ARGV < 0 ) { die("Need (at the very least) CSVs of ids to flip."); }

######################options
my $diagnose         = 0;
my $copyBack         = 0;
my $diagAfter        = 0;
my $order            = 0;
my $launch           = 0;
my $gotLong          = 0;
my $showLines        = 0;
my $showOrderDifs    = 0;
my $checkContRegions = 1;

####################variables
my $last    = 0;
my $lineDif = 0;
my $idDif   = 0;
my $count   = 0;
my %matchups;
my %long;
my $line;
my $upperLimit = 99999;
my $region     = "";
my @bump;

my $mapfile = __FILE__;
$mapfile =~ s/pl$/txt/;

my $triz = "c:\\games\\inform\\triz\\mine";

my $trdr = ".";
my $file = "";

open( A, $mapfile ) || die("Can't open $mapfile.");
while ( $line = <A> ) {
  if ( $line =~ /^#/ ) {
    next;
  }
  chomp($line);
  if ( $line =~ /=/ ) {
    my @eq = split( /=/, $line );
    $long{ $eq[0] } = $eq[1];
    $long{"-$eq[0]"} = $eq[1];
  }
  if ( $line =~ /^DEFAULT:/ ) {
    $file = $line;
    $file =~ s/^DEFAULT://;
  }
  if ( $line =~ /^MAPDIR:/ ) {
    $trdr = $line;
    $trdr =~ s/^MAPDIR://;
  }
}
close(A);

if ( !$file ) { print "Warning, no default file in $mapfile.\n"; }

while ( $count <= $#ARGV ) {
  my $a1 = $ARGV[$count];
  my @j;
  for ($a1) {
    /^-?\?$/ && do { usage(); };
    /^-?x$/  && do { $count = 9999; next; };
    /^-?d$/  && do { $diagnose = 1; $count++; next; };
    /^-?ca?$/ && do {
      $copyBack = 1;
      if ( $a1 =~ /a/ ) { $diagAfter = 1; }
      $count++;
      next;
    };
    /^-?n$/ && do { $copyBack = 0; $count++; next; };
    /^-?o(o)?$/
      && do { $order = 1; $showOrderDifs = ( $a1 =~ /oo/ ); $count++; next; };
    /^-?r$/ && do { $region = $ARGV[ $count + 1 ]; $count += 2; next; };
    /^-?(cr|rc)$/           && do { $checkContRegions = 1; $count++; next; };
    /^-?(ncr|nrc|crn|rcn)$/ && do { $checkContRegions = 0; $count++; next; };
    /^-?da$/                && do { $diagAfter        = 1; $count++; next; };
    /^-?sl$/                && do { $showLines        = 1; $count++; next; };
    /^-?l$/                 && do { $launch           = 1; $count++; next; };
    /^-?ul$/ && do { $upperLimit = $ARGV[ $count + 1 ]; $count += 2; next; };

    if ( $long{$a1} ) {
      $file    = "$long{$a1}.trizbort";
      $gotLong = 1;
      $count++;
      next;
    }
    if ( -f "$a1.trizbort" ) {
      $gotLong = 0;
      $file    = "$a1.trizbort";
      $count++;
      next;
    }
    if ( -f "$triz\\$a1.trizbort" ) {
      die();
      $gotLong = 0;
      $file    = "$triz\\$a1.trizbort";
      $count++;
      next;
    }
    /^[0-9,\\\/:]+$/ && do {
      if ( $a1 =~ /\// ) {
        my $incr = 1;
        if ( $a1 =~ /:/ ) {
          $b = $a1;
          $b =~ s/.*://;
          $incr = $b;
          if ( $incr < 0 ) {
            die("Increment must be positive. Switch / and \\ to change.");
          }
          $a1 =~ s/:.*//;
        }
        @j = split( /\//, $a1 );
        print "Moving up $incr from $j[0] to "
          . ( $j[1] - $incr )
          . ", then down by "
          . ( $j[1] - $j[0] - $incr + 1 )
          . ( $incr != 1 ? " from " . ( $j[1] - $incr + 1 ) . " to" : " at" )
          . " $j[1]\n";
        for ( $j[0] .. $j[1] ) {
          $matchups{$_} = $_ + $incr;
          if ( $matchups{$_} > $j[1] ) {
            $matchups{$_} += ( $j[0] - $j[1] - 1 );
          }
        }
        $count++;
        next;
      }
      if ( $a1 =~ /\\/ ) {
        my $incr = 1;
        if ( $a1 =~ /:/ ) {
          $b = $a1;
          $b =~ s/.*://;
          $incr = $b;
          if ( $incr < 0 ) {
            die("Increment must be positive. Switch / and \\ to change.");
          }
          $a1 =~ s/:.*//;
        }
        @j = split( /\\/, $a1 );
        print "Moving down $incr from $j[1] to "
          . ( $j[0] + $incr )
          . ", then up by "
          . ( $j[1] - $j[0] - $incr + 1 )
          . ( $incr != 1 ? " from " . ( $j[0] + $incr - 1 ) . " to" : " at" )
          . " $j[0]\n";
        for ( $j[0] .. $j[1] ) {
          $matchups{$_} = $_ - $incr;
          if ( $matchups{$_} < $j[0] ) {
            $matchups{$_} += ( $j[1] - $j[0] + 1 );
          }
        }
        $count++;
        next;
      }
      @j = split( /,/, $a1 );
      for ( 0 .. $#j ) {
        my $q = ( $_ + 1 ) % ( $#j + 1 );
        if ( ( $_ > 1 ) && ( $q == $j[$_] - 1 ) ) {
          die("$q mapped to itself.");
        }
        if ( $matchups{ $j[$_] } ) {
          die("$j[$_] is mapped twice, bailing.\n");
        }
        $matchups{ $j[$_] } = $j[$q];

        #print "$j[$_] -> $j[$q], from $_ to $q.\n";
      }
      $count++;
      next;
    };

    print "$a1 is an invalid parameter.\n\n";
    usage();
  }
}

if ( !$file ) {
  die(
"Without a default file to read, you need to specify one on the command line."
  );
}

if ($diagnose) { diagnose(); }

checkIDBounds();

if ($order) { orderTriz(); }

if ( ( scalar keys %matchups == 0 ) && ( !$order ) ) {
  print "No matchups found to flip.\n";
  exit;
}

#for $y (sort keys %matchups) { print "$y - $matchups{$y}\n"; }

my $outFile = $file;
$outFile =~ s/\./id\./g;

if ( ($gotLong) && ( !-f "$trdr\\$file" ) ) {
  die("Oops, no file $trdr\\$file, check trsw.pl.");
}
if ( ( !$gotLong ) && ( !-f "$trdr\\$file" ) ) {
  die("Oops, no file $trdr\\$file, check command line.");
}

open( A, "$trdr\\$file" );
open( B, ">$trdr\\$outFile" );

my $line2;
my $thisLine;

while ( $line = <A> ) {
  $thisLine = 0;
  $line2    = $line;
  $line2 =~ s/id=\"([0-9]+)\"/newNum($1)/ge;
  print B $line2;
  $lineDif += $thisLine;
}

close(A);
close(B);

if ( ($lineDif) || ($idDif) ) {
  print "$lineDif different lines, $idDif total changes.\n";
}

if ($copyBack) {
  conditionalCopy( "$trdr\\$outFile", "$trdr\\$file" );
}
else {
  print "-c to copy back $file.\n";
  `wm $trdr\\$outFile $trdr\\$file`;
}

####################################################################
#
# subroutines below here
#
####################################################################

sub conditionalCopy {
  if ( !compare( $_[0], $_[1] ) ) {
    print "No changes in generated file. I am not copying back.\n";
    print "Also not diagnosing.\n" if $diagAfter;
  }
  else {
    print "Copying back $file.\n";
    `copy /Y $trdr\\$outFile $trdr\\$file`;
    `erase $trdr\\$outFile`;

    if ($diagAfter) { diagnose(); exit(); }
  }
}

sub newNum {

  #print "ARG:$_[0], $matchups{$_[0]}\n";
  if ( $matchups{ $_[0] } ) {
    $idDif++;
    $thisLine = 1;
    return "id=\"$matchups{$_[0]}\"";
  }
  else { return "id=\"$_[0]\""; }
}

sub diagnose {
  my %printy;
  my $thisID;
  my $lastID;
  my @mylines;
  my @myrooms;
  my %regions;

  open( A, "$trdr\\$file" );
  while ( $line = <A> ) {
    if ( $line =~ /room id=\"/ ) {
      my @q = split( /\"/, $line );
      if ( ( !$region ) || ( $q[15] =~ /$region/i ) ) {
        $printy{ $q[1] }  = "$q[3] ($q[15])";
        $regions{ $q[1] } = $q[15];
      }
      $lastID = $q[1];
    }
    if ( $line =~ /line id=\"/ ) {
      my @q = split( /\"/, $line );
      push( @mylines, $q[1] );
    }
  }
  $lastID = 0;
  my $curCount = 0;
  for ( sort keys %printy ) {
    $thisID = $_;
    $thisID =~ s/ .*//g;
    if ( $thisID > $upperLimit ) {
      print "Printout truncated at $_ / $thisID > $upperLimit, $curCount.\n";
      for my $j ( sort keys %printy ) {
        if ( $j > $upperLimit ) { delete( $printy{$j} ); }
      }
      last;
    }
    if ( $thisID - $lastID != 1 ) { $_ =~ s/ ->/ \* ->/; }
    $lastID = $thisID;
    $curCount++;
  }
  print join( "\n",
    map { sprintf( "%3d: $printy{$_}%s", $_, isasc($_) ); }
    sort { $a <=> $b } keys %printy )
    . "\n";
  @mylines = sort { $a <=> $b } (@mylines);

  if ($checkContRegions) {
    my %lastRegLine;
    my @myrooms = sort { $a <=> $b } ( keys %regions );
    for (@myrooms) {
      if ( $lastRegLine{ $regions{$_} }
        && $_ - $lastRegLine{ $regions{$_} } > 1 )
      {
        print
"$regions{$_} out of order at $_, last seen at $lastRegLine{$regions{$_}}.\n";
      }
      $lastRegLine{ $regions{$_} } = $_;
    }
  }

  if ($showLines) {
    print "Lines: " . join( ", ", @mylines ) . "\n";
  }
  else {
    print "Lines min=$mylines[0], max=$mylines[$#mylines]\n";
  }
  if ( $#bump > -1 ) {
    print "Bump ups: " . join( ", ", sort { $a <=> $b } (@bump) ) . "\n";
  }
}

sub isasc {
  my $l2 = $last;
  $last = $_[0];
  if ( $_[0] - $l2 == 1 ) { return ""; }
  push( @bump, $_[0] );
  return " ********************";
}

sub orderTriz {
  my $outFile = $file;
  $outFile =~ s/\./id\./g;
  my $toFile = 1;
  my @ids;
  my $curStr = "";
  open( A, "$trdr\\$file" );
  open( B, ">$trdr\\$outFile" );
  while ( $line = <A> ) {

    if ($toFile) {
      print B $line;
      if ( $line =~ /<map>/ ) { $toFile = 0; }
      next;
    }
    if ( $line =~ /<\/map>/ ) {
      $toFile = 1;
      print B join( "\n", sort { idnum($a) <=> idnum($b) } @ids );
      print "" . ( $#ids + 1 ) . " total.\n";
      print B "\n$line";
      next;
    }
    if ( $line =~ /<(room|line).*\/>/ ) {

      #print "Self closing tag: $line";
      chomp($line);
      push( @ids, $line );
      next;
    }
    if ( $line =~ /<\/(room|line)>/ ) { chomp($line); }
    $curStr .= $line;
    if ( $line =~ /<\/(room|line)>/ ) { push( @ids, $curStr ); $curStr = ""; }
  }
  close(A);
  close(B);
  if ($showOrderDifs) {
    print "Use just -o and not -oo to copy back over.\n";
    `wm $trdr\\$outFile $trdr\\$file`;
    exit();
  }
  else {
    print
"Attempting to copy back over sorted file. There should be no corruptions.\n";
    conditionalCopy( "$trdr\\$outFile", "$trdr\\$file" );
    exit();
  }
}

sub idnum {
  my $id = $_[0];

  #$id =~ s/.*<(line|room) id=\"//sg;
  $id =~ s/.*?id=\"//s;
  $id =~ s/\".*//sg;
  return $id;
}

sub checkIDBounds {
  my $max = 0;
  my $die = 0;
  open( A, "$trdr\\$file" );
  while ( $line = <A> ) {
    if ( $line =~ /id=\"/ ) {
      my @x = split( /\"/, $line );
      my $y = $x[1];
      if ( $y > $max ) { $max = $y; }
    }
  }
  close(A);
  for my $j ( sort keys %matchups ) {
    if ( $j > $max ) {
      print("$j is more than the maximum ID, $max.");
      $die = 1;
    }
  }
  if ($die) { die(); }
  close(A);
}

sub usage {
  print <<EOT;
-c = copy
-d = diagnose (show all rooms)
-da = diagnose after copying
-n = don't copy back
-o = order
-r = specify region
-cr/-rc = check continuous regions, -n for reverse
-ul = upper limit for IDs to display
-l = launch after
-sl = show all lines, not just max
-? = this
-x breaks arg reading loop, useful for if you typed in a lot before and don't want to delete
btp pc sc ss = projects
1,4,7 cycles 1 to 4 to 7, 1/4=1,2,3,4, 1\\4=4,3,2,1
usage: cycle 21-22-...-186 then diagnose after copying (comma flips 21 and 186)
trsw.pl roi 21/186 c da
You may wish to run trsw.pl o after.
EOT
  exit();
}
