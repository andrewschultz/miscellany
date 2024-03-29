########################################################
#
# zup.pl
#
# given a manifest of files, this zips the latest version into, uh, a zip file
#
# this is deprecated in favor of zup.py, though
#

use strict;
use warnings;
use File::stat;
use File::Path;

use lib "c:/writing/scripts";
use mytools;

use Win32::Clipboard;

use Cwd 'abs_path';
use Archive::Zip qw( :ERROR_CODES :CONSTANTS );

################constants first
my $zip  = Archive::Zip->new();
my $zupt = __FILE__;
my $zupl = $zupt;
$zupt =~ s/pl$/-old.txt/;    # zupt = file to read, zupl = perl
my $zupp = $zupl;
$zupp =~ s/\.pl$/p\.txt/;

my $zipdir = "c:\\games\\inform\\zip";
my $dbbin  = "c:\\users\\andrew\\dropbox\\bins";
my $dbweb  = "https://www.dropbox.com/home/bins";
##################options
my %here;
my $extractOnly       = 0;
my $zipUp             = 0;
my $triedSomething    = 0;
my $version           = 0;
my $openAfter         = 0;
my $viewFile          = 0;
my $outFile           = "";
my $executeBeforeZip  = 0;
my $printExecute      = 0;
my $dropBinOpen       = 0;
my $dropLinkClip      = 0;
my $noExecute         = 0;
my $dropCopy          = 0;
my $dropboxSimpleCopy = 0;
my $dropboxThisCopy   = 0;
my $extractAfter      = 0;
my $launchAfter       = 0;
my $launchFile        = "";
my $dropLinkClipOnly  = 0;
my $ignoreTimeFlips   = 0;
my $bailOnFileSize    = 1;
my $deleteBefore      = 1;
my $maxTimeDelay      = 1800;
my $verbose           = 0;
my $buildBefore = 0;
my $copyAfter = 0;

##################variables
my $count = 0;
my $temp;
my $dropboxLink = "";
my $needExclam  = 0;
my %fileMinSize;
my %fileMaxSize;
my $executedAny = 0;
my $lastFile    = "";

while ( $count <= $#ARGV ) {
  $a = lc( $ARGV[$count] );
  for ($a) {
    /^-?\?$/  && do { usage();          exit(); };
    /^-?\?f$/ && do { usage_cfg_file(); exit(); };
    /^-[ol]$/ && do {
      $openAfter = 1;
      $count++;
      print "Launching the output file after creation.\n";
      next;
    };
    /^-?x$/ && do {
      print "Executing optional commands, if there are any.\n";
      $executeBeforeZip = 1;
      $count++;
      next;
    };
    /^-?a$/ && do {
      print "Kitchen sink flags for ZUP.\n";
      $executeBeforeZip = $dropboxThisCopy = $dropLinkClip = 1;
      $count++;
      next;
    };
    /^-?ao$/ && do {
      print "Kitchen sink flags for ZUP, open too.\n";
      $executeBeforeZip = $dropboxThisCopy = $dropBinOpen = $dropLinkClip = 1;
      $count++;
      next;
    };
    /^-?mt$/ && do {
      ( $maxTimeDelay = $a ) =~ s/^-mt//;
      $maxTimeDelay = 0 if $maxTimeDelay == "";
      $count++;
      next;
    };
    /^-?dt$/ && do { $dropboxThisCopy = 1; $count++; next; };
    /^-?it$/ && do { $ignoreTimeFlips = 1; $count++; next; };
    /^-?li$/ && do { projOut($zupt); projOut($zupp); exit(); };
    /^-?(fi|if|sb)$/ && do { $bailOnFileSize = 0; $count++; };
    /^-?nx$/
      && do { print "Executing no commands.\n"; $noExecute = 1; $count++; next; };
    /^-?eo$/ && do { $extractOnly = 1; $extractAfter = 1; $count++; next; };
    /^-?p$/ && do {
      print "Printing result of executed commands, if there are any.\n";
      $printExecute = 1;
      $count++;
      next;
    };
    /^-?dc$/ && do {
      print "Copying to Dropbox afterwards.\n";
      $dropCopy = 1;
      $count++;
      next;
    };
    /^-?d[qs]$/ && do {
      print "Quick/simple copying to Dropbox afterwards. To overwrite, -do.\nNOTE: THIS DOES NOT RECREATE THE ZIP FILE. USE -do FOR THAT, OR BETTER, -a TO PERFORM THE MOST COMMON TASKS.\n";
      $dropboxSimpleCopy = 1;
      $noExecute         = 1;
      $deleteBefore      = 0;
      $count++;
      next;
    };
    /^-?do$/ && do {
      print "Quick/simple copying to Dropbox afterwards, with overwrite. To avoid this, -dq. To do more, try -a.\n";
      $copyAfter = 1;
      $noExecute         = 1;
      $deleteBefore      = 1;
      $count++;
      next;
    };
    /^-?nd$/ && do {
      $deleteBefore = 0;
      $count++;
      next;
    };
    /^-?db$/ && do {
      print "Opening dropbox bin directory afterwards.\n";
      $dropBinOpen = 1;
      $count++;
      next;
    };
    /^-?(dl|dlc|cb)?$/ && do {
      print "Dropbox link to clipboard.\n";
      $dropLinkClip     = 1;
      $dropLinkClipOnly = 1;
      $count++;
      next;
    };
	/^-?b$/ && do {
	  print "Running rebuild before zipping up.\n";
	  $buildBefore = 1;
	  $count++;
	  next;
	};
    /^-?ea$/ && do { $extractAfter = 1; $count++; next; };
    /^-?la$/ && do { $extractAfter = $launchAfter = 1; $count++; next; };
    /^-?e$/ && do { print "Opening commands file $zupt.\n"; `$zupt`; exit; };
    /^-?v$/ && do {
      print "Viewing the output file, if there.\n";
      $viewFile = 1;
      $count++;
      next;
    };
    /^-?ve$/ && do {
      print "Viewing the output file, if there.\n";
      $verbose = 1;
      $count++;
      next;
    };
    /^-?(c|ee)$/ && do {
      print "Opening script file.\n";
      system(
"start \"\" \"C:\\Program Files\\Notepad++\\notepad++.exe\"  $zupl"
      );
      exit;
    };
    /^-/ && do { print "Bad flag $a.\n"; usage(); };
    /,/ && do {
      my @commas = split( /,/, $count );
      for (@commas) { $here{$_} = 1; }
      $count++;
      next;
    };
    $here{ $ARGV[$count] } = 1;
    $count++;
  }
}

my $timestamp = "$zipdir\\timestamp.txt";

open( A, ">$timestamp" );

my (
  $second,     $minute,    $hour,
  $dayOfMonth, $month,     $yearOffset,
  $dayOfWeek,  $dayOfYear, $daylightSavings
) = localtime( time() );
print A sprintf(
  "%d-%02d-%02d %d:%02d:%02d\n",
  $yearOffset + 1900,
  $month + 1, $dayOfMonth, $hour, $minute, $second
);
close(A);

readZupFile($zupt);
readZupFile($zupp);

if ( !$triedSomething ) {
  if ( $#ARGV == -1 ) {
    print "Empty project array. -? for help.\n";
  }
  else {
    print "Didn't find any projects in (@ARGV). -? for help.\n";
  }
}

if ($dropCopy) {
  print "Starting Big Long Dropbox copy...\n";
  `dropbox.pl -x`;
  print "Dropbox copy done.\n";
}

if ($dropBinOpen) {
  print "Opening $dbweb\n";
  `start $dbweb`;
}

#################################
#subroutines
#

sub readZupFile {

  $count = 0;
  $zipUp = 0;

  open( A, $_[0] ) || die("$_[0] not available, bailing.");

  while ( $a = <A> ) {
    chomp($a);

    $a =~ s/\%/$version/g;

    #print "$a: ";

	if ($a =~ /^mistakes=/) {
	  $a =~ s/^mistakes=//gi;
	  my @b = split(/,/, $a);
	  my $bail = 0;
	  for my $c (@b) {
	    if ( defined( $here{$c} ) && ( $here{$c} == 1 ) ) {
		  $bail++;
		  print("WARNING project $c in mistakes. Maybe you meant to add a t to run the test build?\n");
		}
	  }
	  die("Fix mistakes and try again.") if $bail;
	}

    if (( $a =~ /^name=/i ) || ($a =~ /^proj=/i)) {
      if ($needExclam) {
        die("$_[0] line $. needs exclamation mark before $a");
      }
      $a =~ s/^name=//gi;
      my @b = split( /,/, $a );

      for my $idx (@b) {

        #print "$idx\n";
        if ( defined( $here{$idx} ) && ( $here{$idx} == 1 ) ) {
          $needExclam     = 1;
          $triedSomething = 1;
          $zipUp          = 1;
        }
      }
    }
    next if !$zipUp;
    next if $a =~ /^#/;

    # print "$a\n";

    for ($a) {
      /^v=/i && do { $a =~ s/^v=//gi; $version = $a; next; };
      /^!/ && do {
      FIPRO:
        if ($dropboxSimpleCopy) {
          die("OUTFILE wasn't defined during simple copy!") if !$outFile;
          print("Copying $outFile from $zipdir to $dbbin.\n");
          my $cmd = "copy \"$zipdir\\$outFile\" \"$dbbin\\$outFile\"";
          print `$cmd`;
          exit();
        }
        $needExclam = 0;
        if ( $dropLinkClip && !$dropboxLink ) {
          print "There is no dropbox link clip for this project.\n";
          exit;
        }
        if ( !$outFile ) {
          die("OutFile not defined. You need a line with out=X.ZIP in $_[0].");
        }
        my $outLong = "c:/games/inform/zip/$outFile";
        if ( $deleteBefore && ( -f "$outLong" ) ) {
          print "Deleting $outLong, suppress with -nd\n";
          unlink <"$outLong">;
        }
        unless ($extractOnly) {
          print "Writing to $outLong...\n";
          die 'write error'
            unless $zip->writeToFileNamed("c:/games/inform/zip/$outFile") ==
            AZ_OK;
          print "Writing successful.\n";
		  if ($copyAfter) {
		     print("Copying to dropbox after.\n");
             my $cmd = "xcopy /y \"$zipdir\\$outFile\" \"$dbbin\\$outFile\"";
			 `$cmd`;
		  }
          if ($openAfter) {
            print "Opening...\n";
            `$zipdir\\$outFile`;
          }
        }
        if ($extractAfter) {
          my $assem = "c:\\games\\inform\\assem\\";
          rmtree( $assem, 1, 1 );
          mkpath($assem);
          chdir($assem);
          print "Moved to $assem...\n";
          system("7z x -r -y ..\\zip\\$outFile");
          if ($launchFile) {
            my $launchCmd = "$assem$launchFile";
            print "Running ($assem)\\$launchCmd...\n";
            `$launchCmd`;
          }
        }
        print "-x specified but nothing to run.\n"
          if ( $executeBeforeZip && !$executedAny );
        print "Try -x to run executable commands"
          if ( !$executeBeforeZip && $executedAny );
        unless ($extractOnly) {
          for my $q ( sort keys %fileMinSize ) {
            print
"Necessary min size dimension info: $q needs $fileMinSize{$q} < actual size "
              . ( -s "$q" ) . "\n"
              if $verbose;
              if (( defined( $fileMinSize{$q} ) )
              && ( $fileMinSize{$q} )
              && ( -s "$q" < $fileMinSize{$q} )) {
              print "" . ($bailOnFileSize ? "" : "WARNING: ") . "$q in $outLong smaller than minimum bound $fileMinSize{$q} bytes: " . (-s "$q") . ".\n";
			  die "Deleting $outLong ... skip file size bail with -fi/if/sb\n" if $bailOnFileSize;
          }
		  }
          for my $q ( sort keys %fileMaxSize ) {
            print
"Necessary max size dimension info: $q needs $fileMaxSize{$q} > actual size "
              . ( -s "$q" ) . "\n"
              if $verbose;
              if (( defined( $fileMaxSize{$q} ) )
              && ( $fileMaxSize{$q} )
              && ( -s "$q" > $fileMaxSize{$q} ))
			  {
              print "" . ($bailOnFileSize ? "" : "WARNING: ") . "$q in $outLong larger than maximum bound $fileMaxSize{$q} bytes: " . (-s "$q") . ".\n";
			  die "Deleting $outLong ... skip file size bail with -fi/if/sb\n" if $bailOnFileSize;
			  }
          }
        }
        if ($dropboxThisCopy) {
          print("Copying $outFile from $zipdir to $dbbin.\n");
          my $cmd = "copy \"$zipdir\\$outFile\" \"$dbbin\\$outFile\"";
          print `$cmd`;
        }
        return;
      };
	  /^build=/ && do {
	  if ($buildBefore) {

	    (my $temp = $a) =~ s/.*=//;
	    my @buildInfo = split(/,/, $temp);
	    my $cmd = sprintf("icl.pl -j%s %s", $buildInfo[0], $buildInfo[1]);
		print("Running build command $cmd\n");
		my $stuff = `$cmd`;
		print($stuff);
		}
		next;
	  };
      /^out=/i && do {
        $a =~ s/^out=//gi;
        if ( $a !~ /\.zip$/i ) {
          print "Tacking on .zip to the end of $a.\n";
          $a .= ".zip";
        }
        $outFile = $a;
        my $outLong = "c:/games/inform/zip/$outFile";
        $lastFile = $outLong;
        if ($viewFile) {
          if   ( -f "$outFile" ) { `$outFile`; }
          else                   { print "No file $outFile.\n"; }
          exit();
        }
        elsif ($deleteBefore) {
          if ( -f $outLong ) {
            print("Deleting c:/games/inform/zip/$outLong, suppress with -nd\n");
            unlink <"$outLong">;
          }
        }
        else {
          print("Not deleting $outFile\n");
        }
        $zip = Archive::Zip->new();
        next;
      };
      /^tree:/i && do {
        $a =~ s/^tree://gi;
        my @b = split( /,/, $a );
        $zip->addTree( "$b[0]", "$b[1]" )
          ;    #print "Added tree: $b[0] to $b[1].\n";
        next;
      };
      /^min:/ && do {
        $fileMinSize{$lastFile} = $a;
        $fileMinSize{$lastFile} =~ s/.*://;
        die(
"$lastFile File max size $fileMaxSize{$lastFile} < file min size $fileMinSize{$lastFile}"
          )
          if ( defined( $fileMaxSize{$lastFile} ) )
          && ( $fileMaxSize{$lastFile} > 0 )
          && ( $fileMaxSize{$lastFile} < $fileMinSize{$lastFile} );
        next;
      };
      /^max:/ && do {
        $fileMaxSize{$lastFile} = $a;
        $fileMaxSize{$lastFile} =~ s/.*://;
        die(
"File max size $fileMaxSize{$lastFile} < file min size $fileMinSize{$lastFile}"
          )
          if ( $fileMaxSize{$lastFile} > 0 )
          && ( $fileMaxSize{$lastFile} < $fileMinSize{$lastFile} );
        next;
      };
      /^(x:|>>)/i && do {
        $executedAny = 1;
        next if $noExecute;
        if ( $executeBeforeZip || ( $a =~ /^x\+/i ) ) {
          my $cmd = $a;
          $cmd =~ s/^(x:|>>)//gi;
          print( $executeBeforeZip ? "Running" : "Forcing" );
          print " $cmd\n";
          $temp = `$cmd`;
          if ($printExecute) { print $temp; }
        }
        next;
      };
      /^dl=/i && do {
        $dropboxLink = $a;
        $dropboxLink =~ s/^dl=//i;
        if ($dropLinkClip) {
          my $clip = Win32::Clipboard::new();
          $clip->Set("$dropboxLink");
          print "$dropboxLink\n";
          exit() if $dropLinkClipOnly;
        }
        next;
      };
      /^D=/i && do {
        $b = $a;
        $b =~ s/^d=//i;
        $b =~ s/\\/\//g;
        $zip->addDirectory("$b");
        next;
      };
      /^\?:/i && do {
        $a =~ s/^..//;
        if ( $a =~ /[><]/ ) {
          my $compare;
          my $suggCmd = "";

          if ( ( $a =~ />/ ) && ( $a =~ /</ ) ) { die("<> found in $a\n"); }
          if ( $a =~ /\t/ ) {
            my @q = split( "\t", $a );
            $suggCmd = $q[1];
            $a       = $q[0];
          }
          $suggCmd = "(NONE, SORRY)" if ( !$suggCmd );
          my $gtlt = ( $a =~ />/ );
          $compare = $a;
          $a =~ s/[<>].*//;
          $compare =~ s/.*[<>]//;
          my @comp2 = split( /,/, $compare );
          if ( !-f "$a" ) { die "No file $a."; }

          for (@comp2) {
            if ( !-f "$_" ) { die "No file $_."; }
            if ( ( stat($a)->mtime < stat($_)->mtime ) && ($gtlt) ) {
              conditional_die( !$ignoreTimeFlips,
"$a dated before $_, should be other way around, command suggestion: $suggCmd."
              );
            }
            if ( ( stat($a)->mtime > stat($_)->mtime ) && ( !$gtlt ) ) {
              conditional_die( !$ignoreTimeFlips,
"$a dated after $_, should be other way around, command suggestion: $suggCmd."
              );
            }
          }
        }
        next;
      };
      /^LF=i/ && do {
        $launchFile = $a;
        $launchFile =~ s/^lf=//i;
        $count++;
        next;
      };
      /^F=/i && do {
        if ( $a =~ /\\/ ) {
          warn("WARNING Line $. ($a) has wrong slash direction.\n");
        }
        $a =~ s/^F=//gi;
        $a =~ s/\\/\//g;

        #$fileName =~ s/\./_release_$a\./g;
        $b = $a;
        if ( $b =~ /\t/ ) {
          $b =~ s/.*\t//;
          $a =~ s/\t.*//;
        }
        else {
          $b =~ s/.*[\\\/]//g;
        }
        if ( ( !-f "$a" ) && ( !-d "$a" ) && ( $a !~ /\*/ ) ) {
          print "No file/directory $a.\n";
        }
        if ( ( $a =~ /\.(z8|z5|glulx|ulx)$/ ) && ($maxTimeDelay) ) {
          my $timestamp = ctime( stat($a)->mtime );
          my $xxx       = time() - $timestamp;
          if ( $xxx > $maxTimeDelay ) {
            die(
"$a has taken too long--$xxx vs $maxTimeDelay. Set maxTimeDelay to 0 with the -mt flag to fix this."
            );
          }
        }
        $a = follow_symlink($a);
        $zip->addFile( "$a", "$b" );

        if ( -f $a ) { $lastFile = $a; }

        # print "Writing $a to $b.\n";
        next;
      };
      /^c:/i && do {
        my $cmd .= " \"$a\"";
        if ( ( !-f "$a" ) && ( !-d "$a" ) ) {
          if ( $a =~ /[<>]/ ) {
            print "WARNING: May need ? before $a\n";
          }
          else {
            print "WARNING: $a doesn't exist.\n";
          }
        }
        $zip->addFile("$a");
        next;
      };
      /^;/ && do {
        if ($outFile) {
          print(
"Warning: outfile defined but no ! at the end. Forcing end-of-zip-build.\n"
          );
          goto FIPRO;
        }
        last;
      };
    }
    last if $a =~ /^;/;

    #print "Cur cmd $cmd\n";
  }

  close(A);

}

sub processCmd {
  print "$_[0]\n";
  `$_[0]`;
}

sub projOut {
  my $str;
  my $str2;
  my $vers;

  open( A, $_[0] ) || die("$_[0] not available, bailing.");
  print "=" x 30 . "Reading $_[0]...\n";
  while ( $a = <A> ) {
    if ( $a =~ /name=/i ) { $str  = $a; $str =~ s/^name=//i; chomp($str); }
    if ( $a =~ /v=/i )    { $vers = $a; $vers =~ s/^v=//i;   chomp($vers); }
    if ( $a =~ /out=/i ) {
      $str2 = $a;
      $str2 =~ s/^out=//i;
      chomp($str2);
      $str .= " = $str2";
    }
    if ( $a =~ /^!/ ) { $str =~ s/\%/$vers/g; print "$str\n"; }
  }
}

sub conditional_die {
  die( $_[1] ) if ( $_[0] );
  print "WARNING: $_[1]\n";
}

sub usage {
  print <<EOT;
USAGE: zupt.pl (project)
-e open commands file zup.txt
-ea extracts the zip file contents afterwards to c:\\games\\inform\\assem, -la launches LF= file
-c/ee open script file zup.pl
-db open Dropbox bin after
-dc copies EVERYTHING over to Dropbox after
-dl get dropbox link if available (overrides creating a zip)
-dq/ds does a quick dropbox copy
-do overwrites and does a quick dropbox copy
-[ol] open after
-eo extract only
-fi/if = ignore bail on bad file size
-li lists all the project/outfile matches
-nd = don't delete before (default is to delete output file)
-mt = change max time delay (default = 1800, 1/2 hour)
-p print command execution results
-v view output zip file if already there
-x execute optional commands (x+ forces things in the file)
-b builds before zipping
-nx execute nothing (overrides -x)
-a = -x -db -dc -dl(without bailing). -[ol] open after used to be part of this but no longer is. -ao has that.
-?f = show example of formats
EXAMPLE: zup.pl -dq -x -b 17
EXAMPLE: zup.pl -eo 17
EXAMPLE: zup.pl a ut
EOT
  exit;
}

sub usage_cfg_file {
  print <<EOT;
# = commenting
; = end
name=(comma separated values)
v=(version)
dl=(dropbox link)
x: or >>(executable command)
out=out file name (% = release number)
build=kind of build (b/beta or r/release)
min:=minimum acceptable size
max:=maximum acceptable size (to make sure debug builds don't get through)
?:file1<file2 = make sure files are in order
F=file to add
! ends the list
EOT
  exit;

}
