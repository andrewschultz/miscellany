@echo off

if "%1" equ "" (
echo Need an argument
goto end
)

if "%1" equ "h" (
start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" c:\writing\starter.htm
)

if "%1" equ "-b" (
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

if "%1" EQU "g" (
start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" "c:\writing\games.otl"
)

if "%1" EQU "sr" (
start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" "c:\games\inform\Standard Rules.i7x"
)

if EXIST "c:\writing\%1.otl" (
echo Found OTL file.

start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" "c:\writing\%1.otl"
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

if EXIST "c:\scripts\%1" (
echo file is in scripts
start "" "C:\Program Files (x86)\Notepad++\notepad++.exe" c:\scripts\%1
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
echo h opens starter home page
echo -b goes to backup directory

:end