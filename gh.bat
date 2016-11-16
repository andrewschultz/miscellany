@echo off

set TEMPDIR=c:\users\andrew\documents\github

if EXIST "%TEMPDIR%\%1" (
cd %TEMPDIR%\%1
goto end
)

if "%1" EQU "t" (
%TEMPDIR%\git-tips.txt
goto end
)

if "%1" EQU "pc" (
cd  %TEMPDIR%\the-problems-compound
goto end
)

if "%1" EQU "4" (
cd  %TEMPDIR%\fourdiopolis
goto end
)

if "%1" EQU "3" (
cd  %TEMPDIR%\threediopolis
goto end
)

if "%1" EQU "sts" (
cd  %TEMPDIR%\stale-tales-slate
goto end
)

if "%1" EQU "uo" (
cd  %TEMPDIR%\ugly-oafs
goto end
)

if "%1" EQU "oafs" (
cd  %TEMPDIR%\ugly-oafs
goto end
)

if "%1" EQU "gr" (
cd  %TEMPDIR%\grubbyville
goto end
)

if "%1" EQU "tr" (
cd  %TEMPDIR%\trizbort
goto end
)

if "%1" EQU "c" (
gh.pl c
goto end
)

if "%1" EQU "e" (
gh.pl e
goto end
)

if "%1" EQU "p" (
gh.pl e
goto end
)

if "%1" EQU "ce" (
gh.pl ec
goto end
)

if "%1" EQU "ec" (
gh.pl ec
goto end
)

if "%1" EQU "?" (
goto usage
)

echo didn't find anything valid
echo

:usage
echo USAGE
echo ===========================
echo t = git-tips.txt
echo c/e/p = GH.PL code and external list and private files
echo tr = trizbort

:end

echo 1