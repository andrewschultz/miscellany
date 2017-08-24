@echo off

set NOTES=0
set OPENSOURCE=0
set TABLE=0
set RANDTEXT=0
set NUDGE=0
set NOTES=c:\users\andrew\dropbox\notes
set EXT=.inform
set PROJ=buck-the-past
set SOREL=source

if "%1" EQU "h" (
start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" c:\writing\starter.htm
goto end
)

if "%1" EQU "?" (
goto usage
)

:parse

rem forcing options first

if "%1" EQU "0" (
echo overriding other arguments, going to Inform base dir
cd \games\inform
goto end
)

if "%1" EQU "n" (
echo overriding other args, going to nightly build
cd \writing\dict\nightly
goto end
)

if "%1" EQU "ni" (
echo overriding other args, going to nightly build
cd \writing\dict\nightly
goto end
)

if "%1" EQU "rn" (
cd \users\andrew\dropbox\notes
goto end
)

if "%1" EQU "tr" (
echo overriding other arguments, going to trizbort dir
echo tr.bat allows more options
cd \games\inform\triz
shift /1
goto end
)

if "%1" EQU "w" (
echo overriding other arguments, going to Inform walkthroughs dir
cd \games\inform\walkthroughs
goto end
)

if "%1" EQU "x" (
  echo X shortcircuits other options. Going to extensions directory.
  cd "c:\Program Files (x86)\Inform 7\Inform7\Extensions\Andrew Schultz"
  goto end
)

if "%1" EQU "z" (
echo overriding other arguments, going to Inform zip dir
cd \games\inform\zip
goto end
)

rem now forcing opening files

if "%1" EQU "g" (
start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" c:\writing\games.otl
goto end
)

if "%1" EQU "l" (
start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" c:\writing\limericks.otl
goto end
)

if "%1" EQU "rt" (
start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" "c:\writing\dict\sts.txt"
goto end
)

if "%1" EQU "st" (
start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" "c:\writing\dict\sts.txt"
goto end
)

if "%1" EQU "an" (
start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" "C:\games\inform\roiling.inform\Source\tosort.txt"
goto end
)

if "%1" EQU "se" (
start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" "C:\writing\stackex.htm"
goto end
)

rem start release file edits

if "%1" EQU "cr" (
%NOTES%\buck_the_past_release_1_notes.txt
goto end
)

::above is current hot project and can change

if "%1" EQU "4r" (
%NOTES%\fourdiopolis_release_3_notes.txt
goto end
)

if "%1" EQU "3r" (
%NOTES%\threediopolis_release_4_notes.txt
goto end
)

if "%1" EQU "scr" (
%NOTES%\slicker_city_release_2_notes.txt
goto end
)

if "%1" EQU "br" (
%NOTES%\buck_the_past_release_1_notes.txt
goto end
)

if "%1" EQU "bsr" (
%NOTES%\buck_the_past_spring_thing_release_1_notes.txt
goto end
)

if "%1" EQU "rr" (
%NOTES%\roiling_release_4_notes.txt
goto end
)

if "%1" EQU "sr" (
%NOTES%\shuffling_around_release_5_notes.txt
goto end
)

if "%1" EQU "pr" (
%NOTES%\problems_compound_release_3_notes.txt
goto end
)

rem end forcing options

rem start what-file-dir-to-open options

if "%1" EQU "b" (
set SOREL=build
shift /1
goto parse
)

if "%1" EQU "nu" (
set NUDGE=1
shift /1
goto parse
)

if "%1" EQU "no" (
set NOTES=1
shift /1
goto parse
)

if "%1" EQU "ra" (
set RANDTEXT=1
shift /1
goto parse
)

if "%1" EQU "ta" (
set TABLE=1
shift /1
goto parse
)

if "%1" EQU "m" (
set EXT= Materials
set SOREL=release
shift /1
goto parse
)

rem end what-file-dir-to-open options

rem start what-project-to-open options

if "%1" EQU "e11" (
set PROJ=dash
shift /1
goto parse
)

if "%1" EQU "us" (
set PROJ=crabtree
shift /1
goto parse
)

if "%1" EQU "e13" (
set PROJ=ghost
shift /1
goto parse
)

if "%1" EQU "e14" (
set PROJ=candy rush saga
shift /1
goto parse
)

if "%1" EQU "e15" (
set PROJ=heezy-park
shift /1
goto parse
)

if "%1" EQU "e16" (
set PROJ=checkered-haunting
shift /1
goto parse
)

if "%1" EQU "t" (
set OPENSOURCE=1
shift /1
goto parse
)

if "%1" EQU "t2" (
set PROJ=slicker-city
shift /1
goto story
)

if "%1" EQU "tp" (
set PROJ=Compound
shift /1
goto story
)

if "%1" EQU "tb" (
set PROJ=buck-the-past
shift /1
goto story
)

if "%1" EQU "t3" (
set PROJ=threediopolis
shift /1
goto story
)

if "%1" EQU "t4" (
set PROJ=fourdiopolis
shift /1
goto story
)

if "%1" EQU "gr" (
set PROJ=grubbyville
shift /1
goto parse
)

if "%1" EQU "gru" (
set PROJ=grubbyville
shift /1
goto parse
)

if "%1" EQU "3" (
set PROJ=threediopolis
shift /1
goto parse
)

if "%1" EQU "3d" (
set PROJ=threediopolis
shift /1
goto parse
)

if "%1" EQU "4" (
set PROJ=fourdiopolis
shift /1
goto parse
)

if "%1" EQU "4d" (
set PROJ=fourdiopolis
shift /1
goto parse
)

if "%1" EQU "11" (
set PROJ=fanint
shift /1
goto parse
)

if "%1" EQU "12" (
set PROJ=shuffling
shift /1
goto parse
)

if "%1" EQU "ek" (
set PROJ=ektor
shift /1
goto parse
)

if "%1" EQU "fi" (
set PROJ=fanint
shift /1
goto parse
)

if "%1" EQU "op" (
set PROJ=threediopolis
shift /1
goto parse
)

if "%1" EQU "r" (
set PROJ=roiling
shift /1
goto parse
)

if "%1" EQU "ro" (
set PROJ=roiling
shift /1
goto parse
)

if "%1" EQU "roi" (
set PROJ=roiling
shift /1
goto parse
)

if "%1" EQU "15" (
set PROJ=compound
shift /1
goto parse
)

if "%1" EQU "p" (
set PROJ=compound
shift /1
goto parse
)

if "%1" EQU "c" (
set PROJ=compound
shift /1
goto parse
)

if "%1" EQU "pc" (
set PROJ=compound
shift /1
goto parse
)

if "%1" EQU "sb" (
set PROJ=see-why-burg
shift /1
goto parse
)

if "%1" EQU "sc" (
set PROJ=slicker-city
shift /1
goto parse
)

if "%1" EQU "16" (
set PROJ=slicker-city
shift /1
goto parse
)

if "%1" EQU "17" (
set PROJ=curate
shift /1
goto parse
)

if "%1" EQU "cu" (
set PROJ=curate
shift /1
goto parse
)

if "%1" EQU "cur" (
set PROJ=curate
shift /1
goto parse
)

if "%1" EQU "bp" (
set PROJ=buck-the-past
shift /1
goto parse
)

if "%1" EQU "btp" (
set PROJ=buck-the-past
shift /1
goto parse
)

if "%1" EQU "bs" (
set PROJ=btp-st
shift /1
goto parse
)

if "%1" EQU "ss" (
set PROJ=seeker-status
shift /1
goto parse
)

if "%1" EQU "bt" (
set PROJ=buck-the-past
shift /1
goto parse
)

if "%1" EQU "i" (
set PROJ=invis
shift /1
goto parse
)

if "%1" EQU "uo" (
set PROJ=ugly-oafs
shift /1
goto parse
)

if "%1" EQU "o" (
set PROJ=ugly-oafs
shift /1
goto parse
)

if "%1" EQU "oafs" (
set PROJ=ugly-oafs
shift /1
goto parse
)

if "%1" EQU "14" (
set PROJ=ugly-oafs
shift /1
goto parse
)

if "%1" EQU "s" (
set PROJ=shuffling
shift /1
goto parse
)

if "%1" EQU "sa" (
set PROJ=shuffling
shift /1
goto parse
)

if "%1" EQU "ux" (
set PROJ=uxmulbrufyuz
shift /1
goto parse
)

if "%1" EQU "f" (
set PROJ=fetch-quest
shift /1
goto parse
)

if "%1" EQU "fetch" (
set PROJ=fetch-quest
shift /1
goto parse
)

if "%1" EQU "ge" (
set PROJ=gems
goto parse
)

if "%1" NEQ "" (
set PROJ=%1
)

:nodef

if "%2" EQU "t" (
:story
start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" "c:\games\inform\%PROJ%%EXT%\source\story.ni"
)

if "%TABLE%" EQU "1" (
if "%PROJ%" EQU "buck-the-past" (
  start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" "c:\Program Files (x86)\Inform 7\Inform7\Extensions\Andrew Schultz\Buck the Past tables.i7x"
  goto end
  )
if "%PROJ%" EQU "slicker-city" (
  start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" "c:\Program Files (x86)\Inform 7\Inform7\Extensions\Andrew Schultz\Slicker City tables.i7x"
  goto end
  )
start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" "c:\Program Files (x86)\Inform 7\Inform7\Extensions\Andrew Schultz\%PROJ% tables.i7x"
)

if "%OPENSOURCE%" EQU "1" (
start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" "c:\games\inform\%PROJ%.inform\source\story.ni"
goto end
)

if "%RANDTEXT%" EQU "1" (
start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" "c:\Program Files (x86)\Inform 7\Inform7\Extensions\Andrew Schultz\%PROJ% Random Text.i7x"
goto end
)

if "%NUDGE%" EQU "1" (
start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" "c:\Program Files (x86)\Inform 7\Inform7\Extensions\Andrew Schultz\%PROJ% Nudges.i7x"
goto end
)

if "%NOTES%" EQU "1" (
start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" "c:\games\inform\%PROJ%.inform\source\notes.txt"
goto end
)

if "%TESTCASE%" EQU "1" (
start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" \games\inform\%PROJ%%EXT%\source\testcase.txt
goto end
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

:usage
echo Global tweaks: nu = nudges, ra = random (for Stale Tales Slate), no = notes
echo m as 1st argument = materials, b as 1st argument = build
echo ========================
echo r = roiling, sa = shuffling
echo Releases have R at end. pr scr sr rr = problems, slicker, shuffling or roiling releases
echo e1 [1235] = ectoComp n/ni = nightly
echo gr = grubbyville, ua = ugly oafs
echo current project = sc, pc/t2 = problems compound, btp/bp/17/t3 = Buck the Past
echo ========================
echo Non-Inform source: tr = trizbort, rt/st = anagram sorter, an = anagram list
echo ta = tables
echo rn = release notes (1 argument)

:end