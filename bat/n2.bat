@echo off

REM ni.bat
REM replaces ni-old.bat (much longer)
REM It is a wrapper around ni.py, which creates a temporary batch file

if "%1" EQU "aa" (
  cd \games\inform\andac
  goto end
)

if "%1" EQU "gt" (
  c:\users\andrew\documents\github\git-tips.txt
  goto end
)

call ni.py %*

if EXIST "c:\writing\temp\ni-temp.bat" (
  call c:\writing\temp\ni-temp.bat
)

:end