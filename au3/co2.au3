; co2.au3
;
; code academy script to run daily to keep streak going
;

#include <MsgBoxConstants.au3>
#include "c:\\scripts\\andrew.au3"

Opt("WinTitleMatchMode", -2)
Opt("SendKeyDelay", 50)

HotKeySet("{F7}", "Bail")
HotKeySet("{F10}", "Bail")
HotKeySet("{F11}", "Bail")

Local $lesson_delay = 2
Local $wait = 0
Local $launch = 0
Local $start = 0
Local $verticalInit = 710
Local $horizInit = 1400

Local $substring = "learn"

Local $count = 1

while $count <= $cmdLine[0]
  $arg = StringLower($CmdLine[$count])
  if $arg == 's' or $arg == '-s' Then
    $substring = "AndrewSchultzChicago"
  Elseif $arg == 'l' or $arg == '-l' Then
    $substring = "learn"
  Elseif $arg == 'x' Then
    $launch = 1
  Elseif StringLeft($arg, 1) == 'w' Then
    $wait = StringMid($CmdLine[$count], 2)
  Elseif StringLeft($arg, 1) == 'd' Then
    $lesson_delay = StringMid($CmdLine[$count], 2)
  ElseIf $CmdLine[$count] > 0 Then
    $start = $CmdLine[$count]
  ElseIf $CmdLine[$count] == -1 Then
    $verticalInit = 337
  Else
    MOK("need valid #", "number must be -1 for re-reset or 1-9 for which step to start with." & "Can also do -s or s for streak info / -l or l to learn (default)")
    Exit
  EndIf
  $count = $count + 1
  ; ContinueLoop
Wend

if $wait > 0 Then
  sleep($wait * 1000)
Endif

WinActivate("Codecademy - Mozilla Firefox")
WinWaitActive("Codecademy - Mozilla Firefox")

if $start <= 0 Then
  ResetAndResume()
EndIf

; first

if $start <= 1 Then
clickCmd()
send("ls{ENTER}{ENTER}")
hitNext()
EndIf

; second

if $start <= 2 Then
hitNext()
EndIf

; third

if $start <= 3 Then
clickCmd()
send("pwd{ENTER}{ENTER}")
sleep(500)
send("{ENTER}{ENTER}")
hitNext()
EndIf

; fourth

if $start <= 4 Then
clickCmd()
send("pwd{ENTER}")
sleep(500)
send("ls{ENTER}")
sleep(500)
send("cd 2015{ENTER}")
sleep(500)
send("{ENTER}{ENTER}cd .{ENTER}")
hitNext()
EndIf

; fifth

if $start <= 5 Then
clickCmd()
send("cd jan/memory{ENTER}cd ..{ENTER}")
sleep($lesson_delay * 1000)
send("{ENTER}{ENTER}cd .{ENTER}")
hitNext()
hitNext()
EndIf

; sixth

if $start <= 6 Then
clickCmd()
send("cd ../feb{ENTER}mkdir media{ENTER}")
sleep($lesson_delay * 1000)
send("{ENTER}{ENTER}cd .{ENTER}")
hitNext()
hitNext()
EndIf

; seventh

if $start <= 7 Then
clickCmd()
send("cd ../../2014/dec{ENTER}")
send("touch keyboard.txt{ENTER}")
sleep($lesson_delay * 1000)
send("{ENTER}{ENTER}cd .{ENTER}")
hitNext()
EndIf

; eighth

if $start <= 8 Then
send("{ENTER}{ENTER}cd .{ENTER}")
hitNext()
EndIf

; ninth

if $start <= 9 Then
hitNext()
EndIf

Opt("SendKeyDelay", 0)
Send("{ALTDOWN}d{ALTUP}")
send("https://www.codecademy.com/" & $substring & "{ENTER}")

; this was a workaround for a 32 bir btowser but with 64 bit AutoIt/Browser it's not necessary

; MouseClick("left", 500, 55, 1)
; Opt("SendKeyDelay", 0)
; send("https://www.codecademy.com/learn{ENTER}")

; MouseClick("left", 1654, 96, 1)
; MouseClick("left", 1654, 216, 1)

; functions below

Func clickCmd()
  MouseClick("left", 1032, 627, 1)
EndFunc

Func hitNext()
  sleep(1000)
  MouseClick("left", 1054, 983, 1)
  sleep(1000)
EndFunc

Func ResetAndResume()
  MouseClick("left", $horizInit, $verticalInit, 1)
  sleep(1500)
  MouseClick("left", 872, 632, 1)
  sleep(5000)
  MouseClick("left", 847, 289, 1)
  sleep(10000)
EndFunc

Func Bail()
  exit
EndFunc
