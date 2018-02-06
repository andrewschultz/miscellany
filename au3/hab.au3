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
    if $cmdLine[0] > 2 Then
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

	clickSkill($clicks, 920, 980)

  ElseIf $CmdLine[1] == 'm' Then
    if $cmdLine[0] > 1 and $cmdLine[2] > 0 Then
	  clickSkill($clicks, 730, 980)
    Endif
    if $cmdLine[0] > 2 and $cmdLine[3] > 0 Then
	  clickSkill($clicks, 920, 980)
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

    MouseMove ( 100, 100 )
  ElseIf $CmdLine[1] == 'p' Then

    ; perception
    ToHab()
    GoEquip()

    PickAttr(2)

    PickItem(0, 0)
    PickItem(0, 1)
    PickItem(0, 2)
    PickItem(0, 3)

    MouseMove ( 100, 100 )
  ElseIf $CmdLine[1] == 'o' Then
    ToHab()
    for $i = 1 to $clicks
      MouseClick("left")
      sleep($delay)
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
  MsgBox($MB_OK, "Bad/missing parameter(s)", "-m, -i or -p are the options." & @CRLF & "-m needs a number after for clicks, a second for delays.")
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

Func clickSkill($clicks, $x, $y)
  for $i = 1 to $clicks
    MouseClick ( "left", $x, $y, 1 )
    if $i < $clicks Then
      MouseMove ( $x, $y - 100 )
      sleep($delay)
    Endif
  Next
  MouseMove ( 100, 100 )
EndFunc
