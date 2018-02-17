Opt("WinTitleMatchMode", -2)
Opt("SendKeyDelay", 125)


HotKeySet("{F7}", "Bail")

Local $start = 0

WinActivate("Codecademy - Mozilla Firefox")
WinWaitActive("Codecademy - Mozilla Firefox")

if $cmdLine[0] > 0 Then
  if $CmdLine[1] > 0 Then
    $start = $CmdLine[1]
  EndIf
EndIf

if $start <= 0 Then
  ResetAndResume()
EndIf

; first

if $start <= 1 Then
clickCmd()
send("ls{ENTER}")
hitNext()
EndIf

; second

if $start <= 2 Then
hitNext()
EndIf

; third

if $start <= 3 Then
clickCmd()
send("pwd{ENTER}")
hitNext()
EndIf

; fourth

if $start <= 4 Then
clickCmd()
send("pwd{ENTER}ls{ENTER}cd 2015{ENTER}")
hitNext()
EndIf

; fifth

if $start <= 5 Then
clickCmd()
send("cd jan/memory{ENTER}cd ..{ENTER}")
hitNext()
EndIf

; sixth

if $start <= 6 Then
clickCmd()
send("cd ../feb{ENTER}mkdir media{ENTER}")
hitNext()
EndIf

; seventh

if $start <= 7 Then
clickCmd()
send("cd ../../2014/dec{ENTER}touch keyboard.txt{ENTER}")
hitNext()
EndIf

; eighth

if $start <= 8 Then
hitNext()
EndIf

; ninth

if $start <= 9 Then
hitNext()
EndIf

; send("{ALTDOWN}D{ALTUP}")
MouseClick("left", 500, 55, 1)
Opt("SendKeyDelay", 0)
send("https://www.codecademy.com/learn{ENTER}")

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
  MouseClick("left", 1292, 367, 1)
  sleep(1500)
  MouseClick("left", 872, 632, 1)
  sleep(5000)
  MouseClick("left", 847, 289, 1)
  sleep(10000)
EndFunc

Func Bail()
  exit
EndFunc
