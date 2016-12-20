@echo off

:x

if "%1" NEQ "" (
ide.au3 %1
shift
goto x
)
