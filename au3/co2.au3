Opt("WinTitleMatchMode", -2)

HotKeySet("{F7}", "Bail")

WinActivate("Codecademy - Mozilla Firefox")
WinWaitActive("Codecademy - Mozilla Firefox")

ResetAndResume()

; first

clickCmd()
send("ls{ENTER}")
hitNext()

; second

hitNext()

; third

clickCmd()
send("pwd{ENTER}")
hitNext()

; fourth

clickCmd()
send("pwd{ENTER}ls{ENTER}cd 2015{ENTER}")
hitNext()

; fifth

clickCmd()
send("cd jan/memory{ENTER}cd ..{ENTER}")
hitNext()

; sixth

clickCmd()
send("cd ../feb{ENTER}mkdir media{ENTER}")
hitNext()

; seventh

clickCmd()
send("cd ../../2014/dec{ENTER}touch keyboard.txt{ENTER}")
hitNext()

; eighth

hitNext()

; ninth

hitNext()

; send("{ALTDOWN}D{ALTUP}")
MouseClick("left", 500, 55, 1)
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
