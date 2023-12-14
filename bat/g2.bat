@echo off

REM gh.bat
REM longterm replacement for older longer gh.bat
REM It uses ni.py to potentially create a temporary batch file

call ni.py gh %*

if EXIST "c:\writing\temp\ni-temp.bat" (
  echo calling ni-temp.bat
  cat ni-temp.bat
  call c:\writing\temp\ni-temp.bat
)
