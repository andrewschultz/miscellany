@echo off

if "%1" equ "" (
echo Need an argument
goto end
)

rem the stuff below needs to stay there because it's important shortcuts

if "%1" EQU "g" (
start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" "c:\writing\games.otl"
goto end
)

if "%1" EQU "sm" (
c:\games\inform\buck-the-past.inform\Source\gotl.pl
goto end
)

if "%1" EQU "l" (
start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" "c:\writing\limericks.otl"
goto end
)

if "%1" EQU "li" (
start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" "c:\writing\limericks.otl"
goto end
)

rem the stuff above needs to stay there because it's important shortcuts

if "%1" equ "q" (
echo USAGE============================
echo u = undefined
echo f = create empty file named 2nd arg
echo h = starter.htm
echo b = go to notepad backup directory
echo . = go to unix file, OLD
echo g = games.otl
echo l/li = limericks.otl
echo sr = standard rules
echo search for: x.pl, x.py, scripts\x.pl, scripts\x.py, writing\scripts\x.pl, writing\dict\x.pl, x.bat
goto end
)

if "%1" equ "-f" (
goto f
)

if "%1" equ "f" (
:f
echo creating empty file/appending nothing to existing, ignore error.
"abc" >> "%2"
start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" "%2"
goto end
)

if "%1" equ "h" (
start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" c:\writing\starter.htm
goto end
)

if "%1" equ "u" (
start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" c:\writing\undef.txt
goto end
)

if "%1" equ "b" (
goto b
)

if "%1" equ "-b" (
:b
cd %APPDATA\notepad++\backup
dir /od
goto end
)

if "%1" equ "." (
start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" u:\ahschult\.kshrc
start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" u:\ahschult\.profile
goto end
)

if EXIST "%1.pl" (
echo Found PL file.

start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" %1.pl
goto end
)

if EXIST "%1.py" (
echo Found PY file.

start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" %1.py
goto end
)

if EXIST "c:\scripts\%1.py" (
echo Found PY file in scripts.

start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" "c:\scripts\%1.py"
goto end
)

if EXIST "c:\writing\scripts\%1.py" (
echo Found PY file.

start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" "c:\writing\scripts\%1.py"
goto end
)

if EXIST "c:\writing\dict\%1.py" (
echo Found PY file.

start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" "c:\writing\dict\%1.py"
goto end
)

if EXIST "%1.otl" (
echo Found OTL file.

start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" "%1.otl"
goto end
)

if "%1" EQU "sr" (
start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" "c:\games\inform\Standard Rules.i7x"
)

if EXIST "c:\writing\%1.otl" (
echo Found OTL file.

start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" "c:\writing\%1.otl"
goto end
)

if EXIST "c:\scripts\%1" (
echo file is in scripts
start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" c:\scripts\%1
goto end
)

if EXIST "c:\scripts\%1.pl" (
echo file is in scripts
start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" c:\scripts\%1.pl
goto end
)

if EXIST "c:\writing\scripts\%1.pl" (
echo Found PL file.

start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" "c:\writing\scripts\%1.pl"
goto end
)

if EXIST "c:\writing\dict\%1.pl" (
echo Found PL file.

start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" "c:\writing\dict\%1.pl"
goto end
)

if EXIST "%1" (
start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" "%1"
goto end
)

if EXIST "c:\writing\scripts\%1" (
start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" c:\writing\scripts\%1
goto end
)

if EXIST "%1.bat" (
echo Found BAT file locally.

start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" "%1.bat"
goto end
)

if EXIST "c:\scripts\%1.bat" (
echo Found BAT file in scripts.

start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" "c:\scripts\%1.bat"
goto end
)

if EXIST "c:\writing\scripts\%1.bat" (
echo Found BAT file in scripts.

start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" "c:\writing\scripts\%1.bat"
goto end
)

if EXIST "%1.txt" (
start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" %1.txt
goto end
)

if EXIST "c:\writing\scripts\%1.txt" (
start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" c:\writing\scripts\%1.txt
goto end
)

if EXIST "c:\scripts\%1.txt" (
start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" c:\scripts\%1.txt
goto end
)

echo No %1, %1.pl, %1.bat or %1.txt.
goto usage

:end