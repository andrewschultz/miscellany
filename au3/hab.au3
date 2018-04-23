; hab.au3
;
; clicks the mouse for Habitica for Tools of the Trade
; or switches outfits
;
; a = opens armoire (needs #)
; b = fiery blast (needs position and number)
; d = adjust delay
; i = intelligence outfit (default for adventuring)
; m/w = magic/wizard skills
; o = only click to tasks
; p = perception outfit
; r = repeatedly access habit (needs #)
; t = Tools of the Trade clicks (needs #, optional delay)
; te = test
; x = express (e = equip only, r = reequip only, q = no nag)
;

#include <MsgBoxConstants.au3>
#include <Array.au3>

; constants for main attributes (pull down menu/outfits)
Const $CON = 1, $PER = 2, $STR = 3, $INT = 4

; constants for mage skill names
Const $BURST_OF_FLAME = 0, $ETHEREAL_SURGE = 1, $EARTHQUAKE = 2, $CHILLING_FROST = 3

; constants for where to click on a skill
Local $xi = 540, $yi = 980, $xd = 190

; constants for click frequency
Local $clicks = 0, $clicks2 = 0, $delay = 6000
Local $cmdCount = 1
Local $nextCmd = 2
Local $lastCmd = 0

Local $preDelay = 0

Local $testDontClick = False, $didAnything = False

Init()

; put this along with 'a' into its own function.
If $cmdLine[0] == 1 and StringIsDigit($cmdLine[1]) Then
    ToHab()
	    if $cmdLine[1] < 1 Then
		  needPositive()
	    EndIf
        for $i = 1 to $cmdLine[1]
          MouseClick ( "left", 1325, 450, 1 )
          MouseMove(1275, 400)
          if $i < $cmdLine[1] Then
            sleep(2000)
          Endif
        Next
  exit
EndIf

While $cmdCount <= $CmdLine[0]
  if $cmdCount == $lastCmd Then
    MsgBox($MB_OK, "oops possible infinite loop", $cmdCount & " vs " & $nextCmd & " in full array " & _ArrayToString($CmdLine, "/", "1:"))
	exit
  EndIf
  $lastCmd = $cmdCount
  $myCmd = StringLower($CmdLine[$cmdCount])
  if StringLeft($myCmd, 1) = '-' Then ; allow for -x = x
    $myCmd = StringMid($myCmd, 2)
  EndIf
  $nextCmd = $cmdCount + 1
  $nextNum = -1
  if StringIsDigit(StringMid($myCmd, 2)) Then
    $nextNum = StringMid($myCmd, 2)
	$myCmd = StringLeft($myCmd, 1)
  ElseIf StringIsDigit(StringMid($myCmd, 3)) Then ; this is not great code. Ideally we'd define a regex
    $nextNum = StringMid($myCmd, 3)
	$myCmd = StringLeft($myCmd, 2)
  ElseIf $cmdCount < $CmdLine[0] and StringIsDigit($CmdLine[$cmdCount+1]) Then
    $nextNum = $CmdLine[$cmdCount+1]
	$nextCmd = $cmdCount + 2
  EndIf
  If $myCmd == 'te' Then
    $testDontClick = True
    ContinueLoop
  EndIf
  $didAnything = True
  If $myCmd == 'a' Then

    ToHab()
	    if $nextNum < 1 Then
		  needPositive()
	    EndIf
        for $i = 1 to $nextNum
          MouseClick ( "left", 1325, 450, 1 )
          MouseMove(1275, 400)
          if $i < $nextNum Then
            sleep(2000)
          Endif
        Next

  ElseIf $myCmd == 'b' Then
    ToHab()
    $MousePos = MouseGetPos()
    CheckIfOnTask()
    for $i = 1 to $clicks
      clickSkill($BREATH_OF_FIRE, 1)
      sleep($delay/2)
      MouseMove($MousePos[0], $MousePos[1])
      MouseClick("left")
      sleep($delay/2)
    Next
  ElseIf $myCmd == 'd' Then
    $delay = 1000 * GetNumArgOrBail($cmdCount+1)
	$nextCmd = $cmdCount + 2
  ElseIf $myCmd == 'i' Then
    DoInt()
  ElseIf StringLeft($myCmd, 2) == 'iw' Then
    if $myCmd == 'iw' Then
	  $preDelay = $nextNum
	  $nextCmd = $cmdCount + 2
    Else
	  $preDelay = StringMid($myCmd, 3)
	  $nextCmd = $cmdCount + 1
    EndIf
	sleep($preDelay * 1000)
    DoInt()
  ElseIf $myCmd == 'm' Then ; todo: error checking for if anything case
    if $cmdLine[0] >= $cmdCount+1 and $cmdLine[$cmdCount+1] > 0 Then
      $clicks = $nextNum
    Endif
    if $cmdLine[0] >= $cmdCount+2 and $cmdLine[$cmdCount+2] > 0 Then
      $clicks2 = $cmdLine[3]
    Endif
    CheckClicks()
    clickSkill($clicks, $ETHEREAL_SURGE)
    clickSkill($clicks2, $EARTHQUAKE)
  ElseIf $myCmd == 'o' Then
    ToHab()
    MouseClick ( "left", 200, 100, 1 )
  ElseIf $myCmd == 'p' Then
    DoPer()
  ElseIf $myCmd == 'r' Then
    ToHab()
    CheckIfOnTask()
    for $i = 1 to $nextNum
      MouseClick("left")
      sleep($delay)
    Next
  Elseif $myCmd == 't' Then ; cast Tools of the Trade X times
    $clicks = $nextNum
    ToolsTrade($clicks, False, False)
  ElseIf StringLeft($myCmd, 1) == 'x' Then
    $additional = StringMid($myCmd, 2)
    $clicks = $nextNum
    if not StringInStr($additional, 'q') Then
      $res = MsgBox($MB_OKCANCEL, "Warning", "Check to make sure the browser is running relatively quickly, or problems may occur. If it is slow, cancel." & @CRLF & "-xq avoids this nag.")
      if $res == $IDCANCEL Then
        exit
      EndIf
    EndIf
    if StringInStr($additional, 'r') Then
      ToolsTrade($clicks, False, True)
      if StringInStr($additional, 'e') Then
        MsgBox($MB_OK, "Oops canceling suboptions", "You can use the r (reequip) or e (equip) options with x, but not both.")
        exit
      EndIf
    ElseIf StringInStr($additional, 'e') Then
      ToolsTrade($clicks, True, False)
    Else
      ToolsTrade($clicks, True, True)
    EndIf
  ElseIf $myCmd == '?' Then
    Usage(1)
  Else
    Usage(0, $cmdLine[$cmdCount])
  Endif
  $cmdCount = $nextCmd
WEnd

if $cmdLine[0] == 0 Then
  Usage(0, "(empty command line)")
Elseif $didAnything == False Then
  Usage(0, "(no useful commands)")
EndIf

; end main
; function(s) below

Func Usage($questionmark, $badCmd = "")
  Local $usgAry[12] = [ "-a, -b, -i, -iw, -m/-w, -o, -p, -r, -t or -x are the options.", _
  "-a (or only a number in the arguments) opens the armoire # times", _
  "-b does fiery blast, needs # and positioning", _
  "-d adjusts delay, though it needs to come before other commands", _
  "-i = intelligence gear,", _
  "-iw = initial wait,", _
  "-m / -w = mage skills, 1st # = ethereal surge, 2nd # = earthquake", _
  "-o = only click tasks: test option", _
  "-p = perception gear", _
  "-r = repeated habit on the left column, needs # and positioning", _
  "-t (tools of the trade) needs a number after for clicks, with an optional second for delays.", _
  "-x (eXpress) equips perception outfit, runs Tools (#) times and re-equips the intelligence outfit. q ignores the nag. e only equips. r only reequips." _
  ]
  Local $header = "Bad/missing parameter(s)"

  if $questionmark Then
    $header = "HAB.AU3 command line argument usage popup box"
  EndIf

  if $badCmd Then
    $header = $header & " " & $badCmd
  EndIf

  MsgBox($MB_OK, $header,  _ArrayToString($usgAry, @CRLF, 0, UBound($usgAry)-1))
  Exit
EndFunc

Func PickItem($x, $y)
  ; this varies based on screen size
  $x2 = $x * 95 + 250
  $y2 = $y * 160 + 430
  MouseClick ( "left", $x2, $y2, 1)
  sleep(2000)
  ; verify you want to equip the item
  MouseClick ( "left", 814, 510, 1)
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
  ToHome()
EndFunc

Func PickAttr($y)
    MouseClick ( "left", 1450, 330, 1)
    sleep(1000)
    MouseClick ( "left", 1450, 360 + $y * 30, 1)
    sleep(2000)
EndFunc

Func clickSkill($clicks, $x)
  if $testDontClick == True Then
    MsgBox($MB_OK, "Verifying clicking works", "In non-test mode you would have clicked " & $clicks & " times.")
    exit
  EndIf
  for $i = 1 to $clicks
    MouseClick ( "left", $xi + $xd * $x, $yi, 1 )
    if $i < $clicks Then
      MouseMove ( $xi + $xd * $x, $yi - 60 )
      sleep($delay)
    Endif
  Next
  ToTasks()
EndFunc

Func DoInt()
  ; intelligence
  ToHab()
  GoEquip()

  PickAttr(4)

  PickItem(6, 0) ; the first one-handed wand, so we can get more benefits from the off-hand
  PickItem(0, 1)
  PickItem(0, 2)
  PickItem(0, 3)

  ToTasks()
EndFunc

Func DoPer()
  ; perception
  ToHab()
  GoEquip()

  PickAttr(2)

  PickItem(0, 0)
  PickItem(0, 1)
  PickItem(0, 2)
  PickItem(0, 3)
EndFunc

Func ToolsTrade($times, $equipPer, $unequipPer)
  ; number of times to cast Tools

  CheckClicks()

  ; adjust delay: need to rewrite code elsewhere
  ; if $cmdLine[0] > 2 and $CmdLine[3] > 0 Then
  ;   $delay = $CmdLine[3] * 1000
  ; Endif

  ; MsgBox($MB_OK, "debug popup", " " & $clicks & " clicks and delay = " & $delay)

  if $equipPer == True Then
    DoPer()
  EndIf

  ToHab()
  ToTasks()
  MouseClick ( "left", 200, 100, 1 )
    ; need to wait to make sure the page loads after clicking "tasks"
  sleep(2000)

  clickSkill($times, 2)

  if $unequipPer == True Then
    DoInt()
  EndIf

EndFunc

Func CheckClicks() ; this is not perfect but it does the job for now
  if $clicks < 1 and $clicks2 < 1 Then
    MsgBox($MB_OK, "Oops!", "Must specify positive number of clicks after " & $cmdLine[0] & ".")
    exit
  Endif
EndFunc

Func ToTasks()
  sleep(1000)
  MouseMove ( 200, 100 )
  sleep(1000)
EndFunc

Func CheckIfOnTask()
  $MousePos = MouseGetPos()
  If $MousePos[0] > 60 Then
    MsgBox($MB_OK, "Bad mouse position", "You need to position the mouse over a (+) for repeat- or breath-of-fire-cast to work.")
    exit
  EndIf
EndFunc

Func GetNumArgOrBail($cmdIdx)
    if $cmdLine[0] < $cmdIdx Then
      MsgBox($MB_OK, "Need # after arg " & ($cmdIdx - 1) & " " & $cmdLine[$cmdIdx-1], "You need to specify a number of clicks for skill casting/armoire raiding.")
      exit
    EndIf
    if $cmdLine[$cmdIdx] <= 0 Then
      MsgBox($MB_OK, "Need # after arg " & ($cmdIdx - 1) & " " & $cmdLine[$cmdIdx-1], "You need to specify a number of clicks for skill casting/armoire raiding.")
      exit
    EndIf
    return $cmdLine[$cmdIdx]
EndFunc

Func Bail()
  exit
EndFunc

Func NeedPositive()
  MsgBox($MB_OK, "Need positive #", "Need positive # after arg ")
  exit
EndFunc

Func ToHome()
  Send("{CTRLDOWN}{HOME}{CTRLUP}")
EndFunc

Func Init()
  HotKeySet("{F6}", "Bail")
  HotKeySet("{F7}", "Bail")
  HotKeySet("{F9}", "Bail")
  HotKeySet("{F10}", "Bail")
  HotKeySet("{F11}", "Bail")
EndFunc