@echo off

set NOTES=c:\users\andrew\dropbox\notes
set EXT=.inform
set PROJ=slicker-city
set SOREL=source

if "%1" EQU "?" (
:usage
echo r = roiling
echo sa = shuffling
echo ni r nu = roiling nudges
echo ni sa ra = shuffling random
echo pr sr rr = problems, shuffling or roiling releases
echo e1 1-5 = ectoComp n/ni = nightly
echo m as 1st argument = materials
echo tr = trizbort
echo gr = grubbyville, ua = ugly oafs
echo current project = SC, pc/t2 = problems compound
echo btp/bp/17 = Buck the Past
echo rt = daily stuff, an = anagram list
echo b = build
goto end
)

if "%1" EQU "h" (
start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" c:\writing\starter.htm
goto end
)


if "%1" EQU "e11" (
set PROJ=dash
goto nodef
)

if "%1" EQU "e13" (
set PROJ=ghost
goto nodef
)

if "%1" EQU "e14" (
set PROJ=candy rush saga
goto nodef
)

if "%1" EQU "e15" (
set PROJ=heezy-park
goto nodef
)

if "%1" EQU "ni" (
cd \writing\dict\nightly
goto end
)

if "%1" EQU "n" (
cd \writing\dict\nightly
goto end
)

if "%1" EQU "m" (
set EXT= Materials
set SOREL=release
shift /1
)

if "%1" EQU "b" (
set SOREL=Build
shift /1
)

c:

if "%1" EQU "z" (
cd \games\inform\zip
goto end
)

if "%1" EQU "w" (
cd \games\inform\walkthroughs
goto end
)

if "%1" EQU "0" (
cd \games\inform
goto end
)

if "%1" EQU "tr" (
cd \games\inform\triz
goto end
)

if "%1" EQU "t" (
goto story
)

if "%1" EQU "t2" (
set PROJ=Compound
goto story
)

if "%1" EQU "t3" (
set PROJ=threediopolis
goto story
)

if "%1" EQU "t4" (
set PROJ=fourdiopolis
goto story
)

if "%1" EQU "g" (
set PROJ=grubbyville
goto nodef
)

if "%1" EQU "gr" (
set PROJ=grubbyville
goto nodef
)

if "%1" EQU "gru" (
set PROJ=grubbyville
goto nodef
)

if "%1" EQU "3" (
set PROJ=threediopolis
goto nodef
)

if "%1" EQU "3d" (
set PROJ=threediopolis
goto nodef
)

if "%1" EQU "4" (
set PROJ=fourdiopolis
goto nodef
)

if "%1" EQU "4d" (
set PROJ=fourdiopolis
goto nodef
)

if "%1" EQU "11" (
set PROJ=fanint
goto nodef
)

if "%1" EQU "12" (
set PROJ=shuffling
goto nodef
)

if "%1" EQU "ek" (
set PROJ=ektor
goto nodef
)

if "%1" EQU "fi" (
set PROJ=fanint
goto nodef
)

if "%1" EQU "op" (
set PROJ=threediopolis
goto nodef
)

if "%1" EQU "r" (
set PROJ=roiling
goto nodef
)

if "%1" EQU "rt" (
start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" "c:\writing\dict\sts.txt"
goto end
)

if "%1" EQU "ro" (
set PROJ=roiling
goto nodef
)

if "%1" EQU "an" (
start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" "C:\games\inform\roiling.inform\Source\tosort.txt"
goto end
)

if "%1" EQU "roi" (
set PROJ=roiling
goto nodef
)

if "%1" EQU "15" (
set PROJ=compound
goto nodef
)

if "%1" EQU "p" (
set PROJ=compound
goto nodef
)

if "%1" EQU "c" (
set PROJ=compound
goto nodef
)

if "%1" EQU "pc" (
set PROJ=compound
goto nodef
)

if "%1" EQU "sb" (
set PROJ=see-why-burg
goto nodef
)

if "%1" EQU "sc" (
set PROJ=slicker-city
goto nodef
)

if "%1" EQU "16" (
set PROJ=slicker-city
goto nodef
)

if "%1" EQU "17" (
set PROJ=buck-the-past
goto nodef
)

if "%1" EQU "bp" (
set PROJ=buck-the-past
goto nodef
)

if "%1" EQU "btp" (
set PROJ=buck-the-past
goto nodef
)

if "%1" EQU "i" (
set PROJ=invis
goto nodef
)

if "%1" EQU "uo" (
set PROJ=uglyoafs
goto nodef
)

if "%1" EQU "o" (
set PROJ=uglyoafs
goto nodef
)

if "%1" EQU "oafs" (
set PROJ=uglyoafs
goto nodef
)

if "%1" EQU "14" (
set PROJ=uglyoafs
goto nodef
)

if "%1" EQU "s" (
set PROJ=shuffling
goto nodef
)

if "%1" EQU "sa" (
set PROJ=shuffling
goto nodef
)

if "%1" EQU "ux" (
set PROJ=uxmulbrufyuz
goto nodef
)

if "%1" EQU "f" (
set PROJ=fetch-quest
goto nodef
)

if "%1" EQU "no" (
cd \users\andrew\dropbox\notes
goto end
)

if "%1" EQU "fetch" (
set PROJ=fetch-quest
goto nodef
)

if "%1" EQU "ge" (
set PROJ=gems
goto nodef
)

if "%1" NEQ "" (
set PROJ=%1
)

if "%1" EQU "cr" (
%NOTES%\slicker_city_release_1_notes.txt
goto end
)

::above is current hot project

if "%1" EQU "4r" (
%NOTES%\fourdiopolis_release_2_notes.txt
goto end
)

if "%1" EQU "3r" (
%NOTES%\threediopolis_release_4_notes.txt
goto end
)

if "%1" EQU "scr" (
%NOTES%\slicker_city_release_1_notes.txt
goto end
)

if "%1" EQU "rr" (
%NOTES%\roiling_release_4_notes.txt
goto end
)

if "%1" EQU "sr" (
%NOTES%\shuffling_release_5_notes.txt
goto end
)

if "%1" EQU "pr" (
%NOTES%\problems_compound_release_3_notes.txt
goto end
)

:nodef

if "%2" EQU "x" (
"c:\Program Files (x86)\Inform 7\Inform7\Extensions\Andrew Schultz"
)

if "%2" EQU "t" (
:story
start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" "c:\games\inform\%PROJ%%EXT%\source\story.ni"
)

if "%2" EQU "ra" (
start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" "c:\Program Files (x86)\Inform 7\Inform7\Extensions\Andrew Schultz\%PROJ% Random Text.i7x"
)

if "%2" EQU "-" (
start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" "c:\Program Files (x86)\Inform 7\Inform7\Extensions\Andrew Schultz\%PROJ% Random Text.i7x"
)

if "%2" EQU "nu" (
start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" "c:\Program Files (x86)\Inform 7\Inform7\Extensions\Andrew Schultz\%PROJ% Nudges.i7x"
)

if "%2" EQU "tc" (
start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" \games\inform\%PROJ%%EXT%\source\testcase.txt
)

  if EXIST "\games\inform\tries\%PROJ%%EXT%\%SOREL%" ( 
    c:
    cd "\games\inform\tries\%PROJ%%EXT%\%SOREL%"
	goto end
    )
  if EXIST "\games\inform\tmbg\%PROJ%%EXT%\%SOREL%" ( 
    c:
    cd "\games\inform\tmbg\%PROJ%%EXT%\%SOREL%"
	goto end
    )
  if EXIST "\games\inform\%PROJ%%EXT%\%SOREL%" ( 
    c:
    cd "\games\inform\%PROJ%%EXT%\%SOREL%"
	goto end
	)

echo Did not find %PROJ% in tries, tmbg or the default.
goto usage

:end