@echo off

if "%1" EQU "" (
  echo You need to type in something to search for. Something for which to search.
  goto end
)

gt.pl %1

:end
