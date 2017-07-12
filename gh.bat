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

if "%1" EQU "h" (
%TEMPDIR%\git-tips.txt
goto end
)

if "%1" EQU "r" (
%TEMPDIR%\regex.txt
goto end
)

if "%1" EQU "re" (
%TEMPDIR%\regex.txt
goto end
)

if "%1" EQU "hw" (
cd %TEMPDIR%\habitica\website\common\locales\en
goto end
)

if "%1" EQU "ll" (
cd %TEMPDIR%\lawless-legends
goto end
)

if "%1" EQU "rpg" (
cd  %TEMPDIR%\rpg-mapping-tools
goto end
)

if "%1" EQU "pc" (
cd  %TEMPDIR%\the-problems-compound
goto end
)

if "%1" EQU "sc" (
cd  %TEMPDIR%\slicker-city
goto end
)

if "%1" EQU "btp" (
cd  %TEMPDIR%\buck-the-past
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

if "%1" EQU "pe" (
cd  %TEMPDIR%\perlmaven\sites\en\pages
goto end
)

if "%1" EQU "pm" (
cd  %TEMPDIR%\perlmaven\sites\en\pages
goto end
)

if "%1" EQU "perl" (
cd  %TEMPDIR%\perlmaven\sites\en\pages
goto end
)

if "%1" EQU "e11" (
cd  %TEMPDIR%\ectocomp\2011
goto end
)

if "%1" EQU "e13" (
cd  %TEMPDIR%\ectocomp\2013
goto end
)

if "%1" EQU "e14" (
cd  %TEMPDIR%\ectocomp\2014
goto end
)

if "%1" EQU "e15" (
cd  %TEMPDIR%\ectocomp\2015
goto end
)

if "%1" EQU "e16" (
cd  %TEMPDIR%\ectocomp\2016
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
echo h or t = git-tips.txt
echo c/e/p = GH.PL code and external list and private files
echo tr = trizbort

:end
