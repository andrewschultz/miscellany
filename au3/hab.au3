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

; in case I ever want to change default constants
#include <hab-h.au3>
#include "c:\\scripts\\andrew.au3"

#include <MsgBoxConstants.au3>
#include <Math.au3>
#include <Array.au3>

; constants for click frequency
Local $clicks = 0, $clicks2 = 0
Local $cmdCount = 1
Local $nextCmd = 2
Local $lastCmd = 0
Local $startMP = 0
Local $finalMP = 0
Local $MPloss = 0
Local $onlyTrackMP = 0
Local $closeAfter = 0
Local $focused = 0

Local $horiz_delta = 95
Local $vert_delta = 160

Local $preDelay = 0

Local $testDontClick = False, $didAnything = False

Init()

; put this along with 'a' into its own function.
If $cmdLine[0] == 1 and StringIsInt($cmdLine[1]) Then
    ToHab()
	justClick($cmdLine[1])
	Exit
EndIf

; process meta commands first

while $cmdCount <= $CmdLine[0]
  $myCmd = StringLower($CmdLine[$cmdCount])
  $nextCmd = $cmdCount + 1

  if StringLeft($myCmd, 1) = '-' Then ; allow for -x = x
    $myCmd = StringMid($myCmd, 2)
  EndIf

  $nextNum = digit_part($myCmd)
  $myCmd = string_part($myCmd, True)

  if not meta_cmd($myCmd) Then
    $cmdCount = $nextCmd
    ContinueLoop
  EndIf

  If $myCmd == 'te' Then
    $testDontClick = True
  ElseIf $myCmd == 'f' Then
	OpenHabiticaURL(False)
  ElseIf $myCmd == 'fc' Then
    OpenHabiticaURL(True)
	$focused = 1
  ElseIf $myCmd == 'om' Then
    $onlyTrackMp = 1
  ElseIf $myCmd == 'ca' Then
    $closeAfter = 1
  ElseIf $myCmd == '=' or $myCmd == 's' Then
    $startMP = $nextNum
	; MOK("Starting MP", "Starting MP = " & $startMP)
  Else
    MOK("unrecognized", $myCmd & " is not a recognized metacommand, even though it passed the meta_cmd test. Bailing.")
	Exit
  EndIf
  $cmdCount = $nextCmd

WEnd

;uncomment-able code below
;MOK("Debug checkpoint", "Meta command reading done")
;Exit

; this is the main loop

$cmdCount = 1

While $cmdCount <= $CmdLine[0]
  if $cmdCount == $lastCmd Then
    MOK("oops possible infinite loop", $cmdCount & " argument #" & @CRLF & $nextCmd & " argument value" & @CRLF & _ArrayToString($CmdLine, "/"))
	exit
  EndIf
  $lastCmd = $cmdCount
  $negative = 0
  $skipNextArg = 0
  $myCmd = StringLower($CmdLine[$cmdCount])
  if StringLeft($myCmd, 1) = '-' Then ; allow for -x = x
    $negative = 1
    $myCmd = StringMid($myCmd, 2)
  EndIf
  if meta_cmd($myCmd) Then
    ; MOK("ignored meta command", $myCmd)
    $cmdCount += 1
	ContinueLoop
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
	$skipNextArg = 1
  EndIf

  $didAnything = True
  If StringIsDigit($myCmd) Then
    ToHab()
	ToTasks()
    if $negative == 0 Then
	  justClick($myCmd)
    Else
	  justClick(0 - $myCmd)
	EndIf
  ElseIf $myCmd == 'a' Then
    ToHab()
	justClick(StringMid($myCmd, 2))
  ElseIf $myCmd == 'b' Then
    ToHab()
    $MousePos = MouseGetPos()
    CheckIfOnTask()
    for $i = 1 to $clicks
      clickSkill($BREATH_OF_FIRE, 1, 10)
      sleep($delay/2)
      MouseMove($MousePos[0], $MousePos[1])
      MouseClick("left")
      sleep($delay/2)
    Next
  ElseIf $myCmd == 'd' Then
    $delay = 1000 * $nextNum
  ElseIf $myCmd == 'i' Then
    DoInt()
  ElseIf StringLeft($myCmd, 2) == 'iw' Then
    if $myCmd == 'iw' Then
	  $preDelay = $nextNum
	  $skipNextArg = 1
    Else
	  $preDelay = StringMid($myCmd, 3)
    EndIf
	sleep($preDelay * 1000)
    DoInt()
  ElseIf StringInStr($CmdLine[$cmdCount], ",") Then
    Local $spells[3] = StringSplit($CmdLine[$cmdCount], ",")
	Local $spellOrd = [ Number($spells[1]), Number($spells[2]) ]
	_ArraySort($spellOrd)
	ToHab()
	ToTasks()
	clickSkill($spellOrd[0], $EARTHQUAKE, 35)
	if not $onlyTrackMp Then
	  sleep(12000)
    EndIf
	clickSkill($spellOrd[1], $ETHEREAL_SURGE, 30)
	MOK("Mage/Wizard spells", $spellOrd[0] & " earthquake" & @CRLF & $spellOrd[1] & " surge")
	ExitLoop
  ElseIf $myCmd == 'e' Then ; todo: error checking for if anything case
    ToHab()
	ToTasks()
	$old_delay = $delay
	$delay = 15000 ; adjust_delay($delay)
    $clicks = $nextNum
    CheckClicks()
	for $i = 1 to $nextNum
      clickSkill(2, $ETHEREAL_SURGE, 30, True)
      clickSkill(1, $EARTHQUAKE, 35)
	  if $i < $nextNum Then
        sleep($delay)
      EndIf
	Next
	$delay = $old_delay
  ElseIf $myCmd == 'm' Then ; todo: error checking for if anything case
    if $cmdLine[0] >= $cmdCount+1 and $cmdLine[$cmdCount+1] > 0 Then
      $clicks = $nextNum
    Endif
    if $cmdLine[0] >= $cmdCount+2 and $cmdLine[$cmdCount+2] > 0 Then
      $clicks2 = $cmdLine[3]
    Endif
    CheckClicks()
    clickSkill($clicks, $ETHEREAL_SURGE, 30)
    clickSkill($clicks2, $EARTHQUAKE, 35)
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
	  local $rightWarning = "Check to make sure the browser is running relatively quickly, or problems may occur. If it is slow, cancel."
	  if $focused == 1 Then
	    $rightWarning = "Okay, this is the daily script in case I forgot. It runs " & $clicks & " times."
	  EndIf
      $res = MsgBox($MB_OKCANCEL, "Warning",  $rightWarning & @CRLF & "-xq avoids this nag.")
      if $res == $IDCANCEL Then
        exit
      EndIf
    EndIf
    if StringInStr($additional, 'r') Then
      ToolsTrade($clicks, False, True)
      if StringInStr($additional, 'e') Then
        MOK("Oops canceling suboptions", "You can use the r (reequip) or e (equip) options with x, but not both.")
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
  $cmdCount = $nextCmd + $skipNextArg
WEnd

if $cmdLine[0] == 0 Then
  Usage(0, "(empty command line)")
Elseif $didAnything == False Then
  Usage(0, "(no useful commands)")
EndIf

If $startMP > 0 Then
  $finalMP = $startMP - $MPloss
  MOK("Projected MP change", "start=" & $startMP & @CRLF & "MP loss=" & $MPloss & @CRLF & "end=" & $finalMP)
EndIf

If $closeAfter > 0 Then
  Sleep(3000)
  Send("{CTRLDOWN}w{CTRLUP}")
EndIf

; end main
; function(s) below

Func Usage($questionmark, $badCmd = "")
  Local $usgAry[15] = [ "-a, -b, -ca, -d, -e, -i, -iw, -m/-w, -o, -p, -r, -s/-=, -t or -x are the options.", _
  "-a (or only a number in the arguments) opens the armoire # times. Negative number clicks where the mouse is # times", _
  "-b does fiery blast, needs # and positioning", _
  "-ca closes the tab after", _
  "-d adjusts delay, though it needs to come before other commands", _
  "-i = intelligence gear,", _
  "-iw = initial wait,", _
  "-m / -w = mage skills, 1st # = ethereal surge, 2nd # = earthquake, -e does 2 surge 1 earthquake per #", _
  "-o = only click tasks: test option", _
  "-p = perception gear", _
  "-r = repeated habit on the left column, needs # and positioning", _
  "-s or -= = gives starting MP so you can see final MP as well", _
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

  MOK($header,  _ArrayToString($usgAry, @CRLF, 0, UBound($usgAry)-1))
  Exit
EndFunc

Func PickItem($x, $y)
  ; this varies based on screen size
  $x2 = $x * $horiz_delta + 250
  $y2 = $y * $vert_delta + 430
  MouseClick ( "left", $x2, $y2, 1)
  sleep(2000)
  ; verify you want to equip the item
  MouseClick ( "left", 814, 510, 1)
  sleep(2000)
EndFunc

Func GoEquip()
  MouseMove ( 250, 89 )
  sleep(1000)
  MouseClick ( "left", 250, 165, 1 )
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

Func clickSkill($clicks, $x, $cost, $delayLast = False)
  $MPloss = $MPloss + $cost * $clicks
  if $onlyTrackMp Then
    Return
  EndIf
  if $testDontClick == True Then
    MOK("Verifying clicking works", "In non-test mode you would have clicked " & $clicks & " times.")
    exit
  EndIf
  for $i = 1 to $clicks
    MouseClick ( "left", $xi + $xd * $x, $yi, 1 )
    if $i < $clicks or $delayLast Then
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

  ; here we don't go with the best weapon, because it is two-handed.
  ; We pick the first one-handed item, which gives slightly more benefits from the off-hand (Nomad's scimitar, formerly wand of hearts before CRON rewards)
  ; 16 + 16 > 27 (18 + class bonus of 9). We miss out on 15 perception, but 5 intelligence is more important.
  PickItem(1, 0)
  PickItem(0, 1)
  PickItem(0, 2)
  PickItem(0, 3)
  ClickEyewearAndAccessory(True)

  Send("{PGUP}")
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
  ClickEyewearAndAccessory(False)

EndFunc

Func ClickEquipItem($vert_delt)
  sleep(1000)
  MouseClick("left", 814, 510 + $vert_delt, 1)
  sleep(1000)
EndFunc

Func SendWait($x)
  Send($x)
  sleep(600)
EndFunc

Func ClickEyewearAndAccessory($to_int)
  ; this bit is fiddly and also on the second page
  SendWait("{HOME}")
  SendWait("{PGDN}")
  ; eyewear: goofy glasses (0 slots over) for PER, aether mask (0 slots over) for INT
  MouseClick("left", 248, 496, 1)
  ClickEquipItem(0)
  ; though eyewear is between head/body accessory, I put head/body together because there are no INT items, and Habitica sorts them randomly for INT.
  ; however, a strength bonus is a Good Thing, since it increases critical hits.
  if $to_int Then
    SendWait("{PGUP}")
    PickAttr(3)
    SendWait("{PGDN}")
  EndIf
  ; head accessory: goggles of bookbinding (0 slots over) for PER, comical arrow (3 slots over, no INT but STR) afor INT
  MouseClick("left", 248, 344, 1) ; this is simply not good enough. We should sort by strength, then re-sort by intelligence.
  ClickEquipItem(0)
  ; body accessory: cozy scarf (0 slots over) for PER, aether amulet (5 slots over) for INT
  ; Aether amulet has no extra line
  ; Cozy scarf has extra line
  ; since I bought the royal gryphon cloak it appears on the left when sorting by intelligence
  MouseClick("left", 248, 648, 1)
  ClickEquipItem(30 - 30 * $to_int)
  ; aether cloak is the only good back accessory, so we don't need to change it (yet)
  SendWait("{PGUP}")
EndFunc

Func ToolsTrade($times, $equipPer, $unequipPer)
  ; number of times to cast Tools

  CheckClicks()

  ; adjust delay: need to rewrite code elsewhere
  ; if $cmdLine[0] > 2 and $CmdLine[3] > 0 Then
  ;   $delay = $CmdLine[3] * 1000
  ; Endif

  ; MOK("debug popup", " " & $clicks & " clicks and delay = " & $delay)

  if $equipPer == True Then
    DoPer()
	Sleep(500)
  EndIf

  ToHab()
  ToTasks()

  clickSkill($times, 2, 25)

  if $unequipPer == True Then
    DoInt()
  EndIf

EndFunc

Func CheckClicks() ; this is not perfect but it does the job for now
  if $clicks < 1 and $clicks2 < 1 Then
    MOK("Oops!", "Must specify positive number of clicks after " & $cmdLine[0] & ".")
    exit
  Endif
EndFunc

Func ToTasks()
  sleep(1000)
  MouseClick ( "left", 160, 90)
  sleep(1000)
EndFunc

Func CheckIfOnTask()
  $MousePos = MouseGetPos()
  If $MousePos[0] > 60 Then
    MOK("Bad mouse position", "You need to position the mouse over a (+) for repeat- or breath-of-fire-cast to work.")
    exit
  EndIf
EndFunc

Func GetNumArgOrBail($cmdIdx)
    if $cmdLine[0] < $cmdIdx Then
      MOK("Need # after arg " & ($cmdIdx - 1) & " " & $cmdLine[$cmdIdx-1], "You need to specify a number of clicks for skill casting/armoire raiding.")
      exit
    EndIf
    if $cmdLine[$cmdIdx] <= 0 Then
      MOK("Need # after arg " & ($cmdIdx - 1) & " " & $cmdLine[$cmdIdx-1], "You need to specify a number of clicks for skill casting/armoire raiding.")
      exit
    EndIf
    return $cmdLine[$cmdIdx]
EndFunc

Func NeedPositive()
  MOK("Need positive #", "Need positive # after arg ")
  exit
EndFunc

Func adjust_delay($x)
  if $x > 10000 Then
    return $x
  EndIf
  $y = $x * 2
  if $y > 10000 Then
    return 10000
  EndIf
  return $y
EndFunc

Func ToHome()
  Send("{CTRLDOWN}{HOME}{CTRLUP}")
EndFunc

Func meta_cmd($param)
  Local $metas[7] = [ 'om', 'te', '=', 's', 'ca', 'f', 'fc' ]
  Local $um = UBound($metas) - 1

  For $x = 0 to $um
    if StringLeft($param, StringLen($metas[$x])) == $metas[$x] Then
	  Return True
    EndIf
  Next

  Return False
EndFunc

Func string_part($param, $greedy = False)

  Local $digitIndex = StringLen($param)
  For $x = StringLen($param) to 1 step -1
    if StringIsDigit(StringMid($param, $x)) Then
	  $digitIndex = $x - 1
    Elseif $greedy and StringIsDigit(StringMid($param, $x, 1)) Then
	  $digitIndex = $x - 1
	EndIf
  Next
  ; MOK("string digit part", $digitIndex & @CRLF & StringLeft($param, $digitIndex))
  return StringLeft($param, $digitIndex)

EndFunc

Func digit_part($param)

  Local $digitIndex = -1
  For $x = StringLen($param) to 1 step -1
	; MOK("debug", $x & " " & StringMid($param, $x))
    if StringIsDigit(StringMid($param, $x)) Then
	  $digitIndex = $x
	EndIf
  Next
  ; MOK("digit part", $digitIndex)
  return StringMid($param, $digitIndex)

EndFunc

Func justClick($clicksToDo)
  $xi = 1325
  $yi = 450
  if $clicksToDo == 0 Then
    MsgBox($MB_OKCANCEL, "Oops", "Need a number, positive or negative")
	Exit
  EndIf
  if $clicksToDo < 0 Then
    Local $aPos = MouseGetPos()
	$xi = $aPos[0]
	$yi = $aPos[1]
	$clicksToDo = - $clicksToDo
  EndIf
  for $i = 1 to $clicksToDo
    MouseClick ( "left", $xi, $yi, 1 )
    MouseMove(_Max(0, $xi - 50), _Max(0, $yi - 50))
    if $i < $clicksToDo Then
      sleep(2000)
    Endif
  Next
EndFunc

Func Init()
  HotKeySet("{F6}", "Bail")
  HotKeySet("{F7}", "Bail")
  HotKeySet("{F9}", "Bail")
  HotKeySet("{F10}", "Bail")
  HotKeySet("{F11}", "Bail")
EndFunc

Func OpenHabiticaURL($closeWindow)
  Run("C:\Program Files (x86)\Mozilla Firefox\firefox -new-tab http://habitica.com")
  WinActivate("[CLASS:MozillaWindowClass]", "")
  WinWaitActive("[CLASS:MozillaWindowClass]")
  Send("{CTRLDOWN}9{CTRLUP}")
  if $closeWindow Then
	Sleep(10)
    Send("{CTRLDOWN}w{CTRLUP}")
  EndIf
  $didAnything = True
EndFunc

Func Bail()
  exit
EndFunc
