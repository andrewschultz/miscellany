@echo off
cd \users\andrew\documents\github
echo THREEDIOPOLIS
cd threediopolis
git status -s
echo FOURDIOPOLIS
cd ..\fourdiopolis
git status -s
echo STALE TALES SLATE
cd ..\stale-tales-slate
git status -s
echo PROBLEMS COMPOUND
cd ..\the-problems-compound
git status -s
echo SLICKER CITY
cd ..\slicker-city
git status -s
echo MISC
cd ..\misc
git status -s
echo WEIRD
cd ..\ugly-oafs
git status -s
cd ..\ectocomp
git status -s
cd ..\dirk
git status -s
echo TRIZBORT
cd ..\trizbort
git status -s

if "%1" NEQ "" (
cd %1
)