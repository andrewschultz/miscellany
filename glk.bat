@echo off

if "%1" equ "4" (
set GLKFILE=fourdiop
goto stage2
)

if "%1" equ "pc" (
set GLKFILE=pcverbs
np \games\inform\pcverbs.glkdata
goto stage2
)

if "%1" equ "uo" (
set GLKFILE=uoa
goto stage2
)

if EXIST "c:\games\inform\%1.glkdata" (
set GLKFILE=%1
goto stage2
)

echo Didn't find a corresponding glk data file. 4, pc and uo are the most likely ones.
echo D as the second argument deletes the file, while B backs it up. R recovers it.
goto end

:stage2

if "%2" EQU "d" (
erase \games\inform\%GLKFILE%.glkdata
goto end
)

if "%2" EQU "b" (
move \games\inform\%GLKFILE%.glkdata \games\inform\%GLKFILE%.glkdata2
goto end
)

if "%2" EQU "r" (
move \games\inform\%GLKFILE%.glkdata2 \games\inform\%GLKFILE%.glkdata
goto end
)

np \games\inform\%GLKFILE%.glkdata

:end