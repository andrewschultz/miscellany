@echo off

REM g2.bat
REM longterm replacement for gh.bat
REM It uses ni.py to potentially create a temporary batch file

call ni.py %*

if EXIST "c:\writing\temp\ni-temp.bat" (
  call c:\writing\temp\ni-temp.bat
)
