; hab.au3
;
; clicks the mouse for Habitica for Tools of the Trade
; or switches outfits
;
; i = intelligence, p = perception, m 12 = 12 Tools clicks
;
; o = only click
;

#include <MsgBoxConstants.au3>

Local $clicks = 0
Local $delay = 10000

if $CmdLine[0] > 0 Then
  if $CmdLine[1] == 't' Then ; cast Tools of the Trade X times

    ; number of times to cast Tools
    if $cmdLine[0] > 1 Then
      $clicks = $CmdLine[2]
    Endif

    ; adjust delay
    if $cmdLine[0] > 2 and Not $CmdLine[1] == 't' Then
      $delay = $CmdLine[3] * 1000
    Endif

    ; MsgBox($MB_OK, "debug popup", " " & $clicks & " clicks and delay = " & $delay)

    ToHab()
    MouseClick ( "left", 195, 93, 1 )
    ; need to wait to make sure the page loads after clicking "tasks"
    sleep(2000)

    if $clicks < 1 Then
      MsgBox($MB_OK, "Oops!", "Must specify positive number of clicks after -m.")
    Endif

    clickSkill($clicks, 2)

  ElseIf $CmdLine[1] == 'm' Then
    if $cmdLine[0] > 1 and $cmdLine[2] > 0 Then
      clickSkill($clicks, 1)
    Endif
    if $cmdLine[0] > 2 and $cmdLine[3] > 0 Then
      clickSkill($clicks, 2)
    Endif
  ElseIf $CmdLine[1] == 'i' Then

    ; intelligence
    ToHab()
    GoEquip()

    PickAttr(4)

    PickItem(6, 0) ; the first one-handed wand, so we can get more benefits from the off-hand
    PickItem(0, 1)
    PickItem(0, 2)
    PickItem(0, 3)

    ToTasks()
  ElseIf $CmdLine[1] == 'p' Then

    ; perception
    ToHab()
    GoEquip()

    PickAttr(2)

    PickItem(0, 0)
    PickItem(0, 1)
    PickItem(0, 2)
    PickItem(0, 3)

  ElseIf $CmdLine[1] == 'r' Then
    ToHab()
    CheckIfOnTask()
    for $i = 1 to $clicks
      MouseClick("left")
      sleep($delay)
    Next

  ElseIf $CmdLine[1] == 'b' Then
    ToHab()
    $MousePos = MouseGetPos()
    CheckIfOnTask()
    for $i = 1 to $clicks
      clickSkill(1, 540, 980)
      sleep($delay/2)
      MouseMove($MousePos[0], $MousePos[1])
      MouseClick("left")
      sleep($delay/2)
    Next
  Else
    Usage()
  Endif
Else
  Usage()
Endif

; end main
; function(s) below

Func Usage()
  MsgBox($MB_OK, "Bad/missing parameter(s)", "-b, -r, -t, -i or -p are the options." & @CRLF & "-i = intelligence gear, -p = perception gear" & @CRLF & "-t (tools of the trade) needs a number after for clicks, a second for delays." & @CRLF & "-b does fiery blast if cursor is positioned, and -r is a repeated activity.")
EndFunc

Func PickItem($x, $y)
  ; this varies based on screen size
  $x2 = $x * 95 + 250
  $y2 = $y * 160 + 430
  MouseClick ( "left", $x2, $y2, 1)
  sleep(2000)
  ; verify you want to equip the item
  MouseClick ( "left", 814, 480, 1)
  sleep(2000)
EndFunc

Func GoEquip()
  MouseMove ( 271, 89 )
  sleep(1000)
  MouseClick ( "left", 271, 165, 1 )
  sleep(2000)
EndFunc

Func ToHab()
  WinActivate("Habitica - Gamify Your Life - Mozilla Firefox")
  WinWaitActive("Habitica - Gamify Your Life - Mozilla Firefox")
EndFunc

Func PickAttr($y)
    MouseClick ( "left", 1430, 330, 1)
    sleep(1000)
    MouseClick ( "left", 1430, 360 + $y * 30, 1)
    sleep(2000)
EndFunc

Func clickSkill($clicks, $x)
   $xi = 540
   $yi = 980
   $xd = 190
  for $i = 1 to $clicks
    MouseClick ( "left", $xi + $xd * $x, $yi, 1 )
    if $i < $clicks Then
      MouseMove ( $xi + $xd * $x, $yi - 60 )
      sleep($delay)
    Endif
  Next
  ToTasks()
EndFunc

Func ToTasks()
  MouseMove ( 200, 100 )
EndFunc

Func CheckIfOnTask()
  $MousePos = MouseGetPos()
  If $MousePos[0] > 60 Then
    MsgBox($MB_OK, "Bad mouse position", "You need to position the mouse over a (+) for repeat- or breath-of-fire-cast to work.")
    exit
  EndIf
EndFunc