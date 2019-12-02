; hab.au3
;
; clicks the mouse for Habitica for Tools of the Trade
; or switches outfits
;
; a    = opens armoire (needs #)
; b    = fiery blast (needs position and number)
; c    = open for cron
; d    = adjust delay
; f    = fish for items at end
; i    = intelligence outfit (default for adventuring)
; m/w  = mage/wizard skills
; o    = only click to tasks
; p    = perception outfit
; q    = quick-click upper right side (qd = quick delay)
; r    = repeatedly access habit (needs #)
; t/tt = Tools of the Trade clicks (needs #, optional delay)
; te   = test don't click
; tr   = test run
; x    = express (e = equip only, r = reequip only, q = no nag)
;

; in case I ever want to change default constants
; hab-h.au3 is what to change instead of hab.au3, so I don't keep tripping source control for every small choice
; the big one is changing classes
#include <date.au3>
#include "c:\\scripts\\ini.au3"

#include <MsgBoxConstants.au3>
#include <Math.au3>
#include <Array.au3>
#include <File.au3>
#include "c:\\scripts\\andrew.au3"
#include <hab-h.au3>

$vars_file = "c:\scripts\hab.txt"
$equip_file = "c:\scripts\hab-e.txt"
$time_file = "c:\scripts\hab-t.txt"

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

Local $win_size = 1024
; constants for clicking around. Depending on your browser magnification/monitor size, you may wish to change thses.
Local $item_popup_h = 814
Local $item_popup_v = 540
Local $horiz_delta = 95
Local $vert_delta = 160
Local $h_init_page_1 = 250
Local $v_init_page_1 = 430
Local $attr_pulldown_h_init = 1450
Local $attr_pulldown_v_init = 330
Local $attr_pulldown_delta = 30
Local $page_down_adjust = 880
Local $last_row_after_end = 580

Local $pet_feed_init_x = 246
Local $pet_feed_init_y = 528
Local $pet_feed_delta = 94
Local $pet_food_init_x = 690
Local $pet_food_init_y = 960
Local $pet_food_delta = 100
Local $int_per_delta = 184

Local $equip_wait = 750

Local $init_equip = 0
Local $end_equip = 0
Local $max_equip = 6

Local $delay = 3000
Local $mage_delay = $delay
Local $rogue_delay = $delay * 2

Local $quick_click_delay = 800

Local $preDelay = 0

Local $testRun = 0
Local $debug = False

Local $testDontClick = False, $didAnything = False

; put this along with 'a' into its own function.
If $cmdLine[0] == 1 and StringIsInt($cmdLine[1]) Then
    ToHab()
	justClick($cmdLine[1])
	Exit
EndIf

Global $note_daily_force = @CRLF & @CRLF & "NOTE: -md marks today's tasks done."

; read the config file first

; MOK($horiz_delta & " " & $h_init_page_1 & " " & $vert_delta & " " & $v_init_page_1, $item_popup_h & " " & $item_popup_v)
read_hab_cfg($vars_file)
; MOK($horiz_delta & " " & $h_init_page_1 & " " & $vert_delta & " " & $v_init_page_1, $item_popup_h & " " & $item_popup_v)

; process meta commands first

while $cmdCount <= $CmdLine[0]
  $myCmd = StringLower($CmdLine[$cmdCount])
  $nextCmd = $cmdCount + 1

  if StringLeft($myCmd, 1) = '-' Then ; allow for -x = x
    $myCmd = StringMid($myCmd, 2)
  EndIf

  If StringRegExp($myCmd, "^[0-9]+-[0-9]+$") Then
    $temp = StringSplit($myCmd, "-")
    $init_equip = $temp[1]
    $end_equip = $temp[2]
    if $init_equip > $end_equip Then MOK("Error!", "You need initial equip line to be less than end equip line." & @CRLF & @CRLF & $init_equip & " > " & $end_equip, True)
    if $init_equip > $max_equip Then MOK("Error!", "You need initial equip line to be less than max equip line. This is zero indexed." & @CRLF & @CRLF & $init_equip & " > " & $max_equip, True)
	if $end_equip > $max_equip Then MOK("WARNING! End_equip > Max_equip" "Adjusting " & $end_equip & " down to " & $max_equip, True)
    $cmdCount += 1
	ContinueLoop
  EndIf

  if not meta_cmd($myCmd) Then
    $cmdCount = $nextCmd
    ContinueLoop
  EndIf

  $nextNum = digit_part($myCmd)
  $myCmd = string_part($myCmd, True)

  If $myCmd == 'te' Then
    $testDontClick = True
  ElseIf $myCmd == 'tr' Then
    $testRun = True
  ElseIf $myCmd == 'fo' Then
	OpenHabiticaURL(False)
  ElseIf $myCmd == 'fc' and not StringIsDigit($nextNum) Then
    OpenHabiticaURL(True)
	$focused = 1
  ElseIf $myCmd == 'qd' Then
    $quick_click_delay = 100 * $nextNum
  ElseIf $myCmd == 'om' Then
    $onlyTrackMp = 1
  ElseIf $myCmd == 'ca' Then
    $closeAfter = 1
  ElseIf $myCmd == 'as' Then
    getAutosellValues()
  ElseIf $myCmd == '=' or $myCmd == 's' Then
    $startMP = $nextNum
	; MOK("Starting MP", "Starting MP = " & $startMP)
  Else
    MOK("Unrecognized meta-command", $myCmd & " is not a recognized meta-command, even though it passed the meta_cmd test. Bailing.")
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
    if $debug Then MOK("ignored meta command", $myCmd)
    $cmdCount += 1
	ContinueLoop
  EndIf
  $nextCmd = $cmdCount + 1
  $nextNum = -1
  if StringRegExp($myCmd, '^[a-z]+[0-9]+', "") Then
    $nextNum = StringRegExpReplace($myCmd, "^[a-z]+", "")
    $nextNum = StringRegExpReplace($nextNum, "^-?([0-9]+).*$", "\1")
	$myCmd = StringRegExpReplace($myCmd, "[0-9]+$", "")
  ElseIf $cmdCount < $CmdLine[0] and StringIsDigit($CmdLine[$cmdCount+1]) Then
    $nextNum = $CmdLine[$cmdCount+1]
	$skipNextArg = 1
  EndIf

  $didAnything = True
  If StringIsDigit($myCmd) Then
	ToTasks(True)
    if $negative == 0 Then
	  if in_url("habitica.com/") Then
	    MOK("Error", "You need to be on the front page for this to work. Or use a negative number to click at the current mouse point.", True)
	EndIf
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
      clickSkill($BREATH_OF_FIRE, 1, 10, $mage_delay)
      sleep($delay/2)
      MouseMove($MousePos[0], $MousePos[1])
      MouseClick("left")
      sleep($delay/2)
    Next
  ElseIf $myCmd == 'c' or $myCmd == 'cv' or $myCmd == 'co' Then
    if $nextNum == -1 Then
	  $nextNum = 0
	EndIf
    open_for_cron($nextNum, $myCmd == 'c', $myCmd == 'cv')
  ElseIf $myCmd == 'd' Then
    $delay = 1000 * $nextNum
  ElseIf $myCmd == 'f' or $myCmd == 'fi' or $myCmd == 'ft' or $myCmd == 'ff' or $myCmd == 'ffs' or $myCmd == 'fc' or $myCmd == 'cf' or $myCmd == 'fs' Then
    if $nextNum <= 0 Then
	  MsgBox($MB_OK, "Need # of times to fish", "You need to specify a positive number after -f(*)." & @CRLF & @CRLF & "ff = fixed fish (where mouse is) ffs = single" & @CRLF & "fs = fish slow (only 1 click, for casting spells/doing tasks)" & @CRLF & "ft = fish toggle (end by toggling checked status)" & @CRLF & "-f/-fi = no toggle but go to where first unchecked task would be" & @CRLF & "-cf = fish for class stats e.g. after resetting class" & @CRLF & @CRLF & "AFTER:" & @CRLF & "-q = get rid of the stuff in the upper right (about 3x # used)")
	  Exit
    EndIf
	$loc_toggle_at_end = $myCmd <> 'ff' and $myCmd <> 'fc' and $myCmd <> 'cf' and $myCmd <> 'fs'
	$loc_fish_toggle = $myCmd <> 'fc' and $myCmd <> 'cf' and $myCmd <> 'ffs'
	$loc_move_mouse = $myCmd <> 'fc' and $myCmd <> 'cf'
	$loc_need_delay = $myCmd <> 'fc' and $myCmd <> 'cf'
	FishItmBossDmg($nextNum,     $myCmd == 'ft', $loc_toggle_at_end,     $loc_fish_toggle,         $myCmd == 'fs' , $loc_move_mouse, $loc_need_delay)
	;              times to fish toggle at end?  Move mouse after click? Click 2x(true)/1x(false)  delay 1 sec each click?
  ElseIf $myCmd == 'i' Then
    DoInt()
  ElseIf $myCmd == 'id' Then ; this is a test for delay
    DoInt(2)
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
	clickSkill($spellOrd[0], $EARTHQUAKE, 35, $mage_delay)
	if not $onlyTrackMp Then
	  sleep(12000)
    EndIf
	clickSkill($spellOrd[1], $ETHEREAL_SURGE, 30, $mage_delay)
	MOK("Mage/Wizard spells", $spellOrd[0] & " earthquake" & @CRLF & $spellOrd[1] & " surge")
	MarkBuffsDone($CLASS_WIZARD)
	ExitLoop
  ElseIf $myCmd == 'fe' or $myCmd == 'ffe' or $myCmd == 'fef' Then
    ToHab()
    if $myCmd == 'fe' and not in_url("stable") Then MOK("Oops!", "You are not on the stable page.", True)
	; GoStable()
    $times_to_click = int($nextNum / 100)
	if $times_to_click == 0 Then $times_to_click = 9
	if $times_to_click < 0 or $times_to_click > 9 Then
	  MOK("Oops!", "The hundreds digit needs to be between 0 (goes to 9) and 9, for the number of times to feed a pet.", True)
	EndIf
    $top_to_click = Int(Mod($nextNum, 100) / 10)
	$bottom_to_click = Mod($nextNum, 10)
	if $top_to_click > 9 or $top_to_click < 0 Then
	  MOK("Oops!", "Need a number between 00-90 for pet to feed/click on.", True)
    EndIf
	if $bottom_to_click > 9 or $bottom_to_click < 0 Then
	  MOK("Oops!", "Need a number with ones digit between 0 and 5 for the sort of food to feed your pet.", True)
    EndIf
	if $bottom_to_click > 5 Then
      MouseMove($pet_food_next_x, $pet_food_init_y)
	  for $i = 6 to $bottom_to_click
		MouseClick(left)
		Sleep(300)
	  Next
	  $bottom_to_click = 5
	  Exit
    EndIf
	$pet_x = $pet_feed_init_x + $pet_feed_delta * $top_to_click
	$pet_y = $pet_feed_init_y
	$food_x = $pet_food_init_x + $pet_food_delta * $bottom_to_click
	$food_y = $pet_food_init_y
	for $i = 1 to $times_to_click
	  MouseMove($food_x, $food_y)
	  Sleep($delay/5)
	  MouseClick("left")
	  MouseMove($pet_x, $pet_y)
	  Sleep($delay/5)
	  MouseClick("left")
    Next
  ElseIf $myCmd == 'e' Then ; todo: error checking for if anything case
    checkClass($CLASS_MAGE)
	ToTasks(True)
    $clicks = $nextNum
    CheckClicks()
	for $i = 1 to $nextNum
      clickSkill(2, $ETHEREAL_SURGE, 30, True, $mage_delay)
	  sleep($delay)
      clickSkill(1, $EARTHQUAKE, 35, $mage_delay)
	  if $i < $nextNum Then
        sleep($delay)
      EndIf
	Next
	MarkBuffsDone($CLASS_WIZARD)
  ElseIf $myCmd == 'm' or $myCmd == 'w' Then ; todo: error checking for if anything case
    if $cmdLine[0] >= $cmdCount+1 and $cmdLine[$cmdCount+1] > 0 Then
      $clicks = $nextNum
    Endif
    if $cmdLine[0] >= $cmdCount+2 and $cmdLine[$cmdCount+2] > 0 Then
      $clicks2 = removeEndNonDigit($cmdLine[$cmdCount + 2])
    Endif
	ToTasks(True)
    CheckClicks()
    clickSkill($clicks, $ETHEREAL_SURGE, 30, $mage_delay)
    clickSkill($clicks2, $EARTHQUAKE, 35, $mage_delay)
  ElseIf $myCmd == 'em' or $myCmd == 'mm' or $myCmd == 'wm' Then
    checkClass($CLASS_WIZARD)
	MarkBuffsDone($CLASS_WIZARD, $bail = True)
  ElseIf $myCmd == 'o' Then
    ToHab()
    MouseClick ( "left", 200, 100, 1 )
  ElseIf $myCmd == 'p' Then
    DoPer()
  ElseIf $myCmd == 'q' Then
    Local $hWnd = WinWait("", "Habitica - Gamify Your Life", 1)
	if not $hWnd Then
	  MsgBox($MB_OK, "OOPS", "No Habitica window open.")
	  Exit
    EndIf
    $clicks = $nextNum
    $xxx = WinGetClientSize($hWnd)
	ToHab()
	for $i = 1 to $clicks
      MouseMove($xxx[0] - 136, 136)
	  MouseClick("left")
	  sleep($quick_click_delay)
    Next
	WinClose($hWnd)
	Exit
  ElseIf $myCmd == 'r' Then
    ToHab()
    CheckIfOnTask()
    for $i = 1 to $nextNum
      MouseClick("left")
      sleep($delay)
    Next
  Elseif $myCmd == 't' or $myCmd == 'tt' Then ; cast Tools of the Trade X times
	checkClass($CLASS_ROGUE)
    $clicks = $nextNum
    ToolsTrade($clicks, False, False)
	MarkBuffsDone($CLASS_ROGUE)
  Elseif $myCmd == 'tm' or $myCmd == 'ttm' Then
    MarkBuffsDone($CLASS_ROGUE)
  ElseIf $myCmd == 'md' Then
    MarkBuffsDone($my_class)
  ElseIf StringLeft($myCmd, 1) == 'x' Then
	checkClass($CLASS_ROGUE)
	if $myCmd == "xm" Then MarkBuffsDone($CLASS_ROGUE, $bail = True)
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
	; if r is in the string, we only reequip. If e is in the string, we only equip. We only check Max MP equal on 'x' ... when we equip and re-equip.
	$avoid_equip_p = StringInStr($additional, 'r')
	$avoid_reequip_i = StringInStr($additional, 'e')
    if $avoid_equip_p and $avoid_reequip_i and not $testRun Then MOK("Oops canceling suboptions", "You can use the r (reequip) or e (equip) options with x, but not both. Use -t just to cast tools.", True)
	; # of clicks, equip personality gear, reequip intelligence gear, detect MP before/after
	ToolsTrade($clicks, not $avoid_equip_p, not $avoid_reequip_i, not $avoid_equip_p and not $avoid_reequip_i)
	MarkBuffsDone($CLASS_ROGUE)
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

Func PickItem($x, $y)
  ; this varies based on screen size
  $x2 = $x * $horiz_delta + $h_init_page_1
  $y2 = $y * $vert_delta + $v_init_page_1
  MouseClick ( "left", $x2, $y2, 1)
  sleep(2000)
  ; verify you want to equip the item
  MouseClick ( "left", $item_popup_h, $item_popup_v, 1)
  sleep(2000)
EndFunc

Func GoInv($which_inv)
  MouseMove ( 250, 89 )
  sleep(1000)
  MouseClick ( "left", 250, 130 + $which_inv * 35, 1 )
  sleep(2000)
EndFunc

Func GoItems()
  GoInv($ITEM_POSITION)
EndFunc

Func GoEquip()
  GoInv($EQUIP_POSITION)
EndFunc

Func GoStable()
  GoInv($STABLE_POSITION)
EndFunc

Func ClickTasks()
  MouseClick ( "left", 160, 90)
EndFunc

Func ToTasks($hab_too = True, $loc_delay=1000)
  if $hab_too then
    ToHab()
  endif
  sleep($loc_delay)
  ClickTasks()
  sleep($loc_delay)
EndFunc

Func ToHab()
  WinActivate("Habitica - Gamify Your Life - Mozilla Firefox")
  WinWaitActive("Habitica - Gamify Your Life - Mozilla Firefox")
  if $win_size == 0 Then
    $win_size = WinGetClientSize("Habitica - Gamify Your Life - Mozilla Firefox")
  EndIf
  ToHome()
EndFunc

Func PickAttr($y)
    MouseClick ( "left", $attr_pulldown_h_init, $attr_pulldown_v_init, 1)
    sleep(1000)
    MouseClick ( "left", $attr_pulldown_h_init, $attr_pulldown_v_init + $attr_pulldown_delta * ($y + 1), 1)
    sleep(2000)
EndFunc

Func clickSkill($clicks, $x, $cost, $my_delay, $delayLast = False)
  ToHab()
  Send("{ESC}") ; this is so I get rid of a search box, which disrupted me before
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
      sleep($my_delay)
    Endif
  Next
  ToTasks()
EndFunc

Func getAutosellValues($go_to_items = True)
  ToHab()
  ;GoItems()
  $my_autosell = 0
  Send("^a")
  sleep(500)
  Send("^c")
  sleep(500)
  $clip_in = ClipGet()
  local $autosell_value = 0
  local $ary = StringSplit($clip_in, @CR & @LF, $STR_ENTIRESPLIT)
  local $my_num
  local $got_eggs = False
  local $got_hatch = False
  local $got_food = False

  for $q = 1 to $ary[0]
    if StringLeft($ary[$q], 4) == "Eggs" Then
	  $got_eggs = True
	  $autosell_value += num_at_end($ary[$q]) * 3
    elseif StringLeft($ary[$q], 16) == "Hatching Potions" Then
	  $got_hatch = True
	  $autosell_value += num_at_end($ary[$q]) * 89 / 30
    elseif StringLeft($ary[$q], 16) == "Food and Saddles" Then
	  $got_food = True
	  $autosell_value += num_at_end($ary[$q])
    EndIf
  Next
  MOK("Autosell value = " & Floor($autosell_value), (($got_eggs and $got_hatch and $got_food) ? "Found eggs/hatching potions/food" : "Missing one or more of eggs/hatching potions/food:" & @CRLF & @CRLF & "Eggs " & $got_eggs & " Hatching " & $got_hatch & " Food " & $got_food))
  Exit
EndFunc

Func MaxAttr($attr_to_max, $delays = 0)
  ToHab()
  $equip_file_handle = FileOpen($equip_file, 0)
  Local $equip_line = 0
  Local $equip_count = 0
  Local $lastPagesDown = 0
  Local $this_line_attr = 0
  Local $columns = 8
  While 1
    $equip_line += 1
    $line = FileReadLine($equip_file_handle)
	If StringLeft($line, 1) == '#' Then
	  ContinueLoop
	ElseIf StringLeft($line, 1) == ';' or StringLen($line) == 0 Then
	  ExitLoop
    EndIf
	$vars = StringSplit($line, ",")
	if $vars[0] < 8 Then
	  MOK("WARNING too short line " & $equip_line, $line & " needs " & $columns & " CSVs and only has " & $vars[0])
	  Exit
	EndIf
	if $vars[0] > 8 Then
	  MOK("WARNING too long line " & $equip_line, $line & " needs " & $columns & " CSVs and has " & $vars[0])
	EndIf
	$classAdj = dict_or_actual($vars[2], $classHash)
	if $classAdj <> $my_class and $classAdj <> 0 Then
	  ContinueLoop
    EndIf
	$line_max_attr = dict_or_actual($vars[1], $attrHash)
	if $line_max_attr <> $attr_to_max Then
	  ContinueLoop
    EndIf
	$line_adj_attr = dict_or_actual($vars[3], $attrHash)
	$mainOrExtra = $vars[4]
	$flipToEnd = $vars[5]
	$column = $vars[6]
	$row = $vars[7]
    if $init_equip and ($row < $init_equip) Then ContinueLoop
    if $end_equip and ($row > $end_equip) Then ContinueLoop
    $vert_equip_delta = $vars[8]
	if $line_adj_attr <> $this_line_attr Then
	  SendWait("{HOME}")
	  PickAttr($line_adj_attr)
	  $this_line_attr = $line_adj_attr
	  $lastPagesDown = 0
	EndIf
	$the_x = $h_init_page_1 + $horiz_delta * $column
	$the_y = $v_init_page_1 + $vert_delta * $row
	$thisPagesDown = _Max(0, Int(($the_y + $page_down_adjust - $win_size) / $page_down_adjust))
	if $thisPagesDown > $lastPagesDown Then
	  For $i = $lastPagesDown to $thisPagesDown - 1
	    SendWait("{PGDN}")
	  Next
	  $lastPagesDown = $thisPagesDown
    EndIf
	if $thisPagesDown < $lastPagesDown Then
	  For $i = $thisPagesDown to $lastPagesDown - 1
	    SendWait("{PGUP}")
	  Next
	  $lastPagesDown = $thisPagesDown
    EndIf
	$equip_count += 1
    $the_y -= $thisPagesDown * $page_down_adjust
	$equip_mult = 1 + ($equip_count <= $delays)
    Sleep($equip_wait)
	MouseMove($the_x, $the_y)
	MouseClick("left")
    Sleep($equip_wait * $equip_mult)
	MouseMove($item_popup_h, $item_popup_v + $vert_equip_delta)
	MouseClick("left")
	Sleep(100)
	Send("{ESC}")

	; MOK("Where to click " & $column & " " & $row & " " & $equip_line, " x " & $the_x & " Y " & $the_y & " p " & $thisPagesDown & @CRLF & $line)
  WEnd
  FileClose($equip_file_handle)
  if $thisPagesDown > 0 Then Send("{PGUP}")
  ToTasks(False)
EndFunc

Func dance_around($x, $y)
  MouseMove($x - 50, $y)
  MouseMove($x, $y - 50)
  MouseMove($x + 50, $y)
  MouseMove($x, $y + 50)
EndFunc

Func dict_or_actual($val, $dic)
  if $dic.Exists($val) Then
    return $dic($val)
  EndIf
  return $val
EndFunc

Func DoInt($delays=0)
  ; intelligence
  ToHab()
  GoEquip()

  MaxAttr(4, $delays)

EndFunc

Func DoPer($delays=0)
  ; perception
  ToHab()
  GoEquip()

  MaxAttr(2, $delays)

EndFunc

Func ClickEquipItem($vert_delt)
  sleep(1000)
  MouseClick("left", 814, $item_popup_v + $vert_delt, 1)
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

Func ToolsTrade($times, $equipPer, $unequipPer, $check_max_mp = False, $check_cur_mp = True, $check_eq_adj = True)
  ; number of times to cast Tools

  CheckClicks()

  ; adjust delay: need to rewrite code elsewhere
  ; if $cmdLine[0] > 2 and $CmdLine[3] > 0 Then
  ;   $delay = $CmdLine[3] * 1000
  ; Endif

  ; MOK("debug popup", " " & $clicks & " clicks and delay = " & $delay)

  local $mp_start
  local $my_end

  $check_any = $check_max_mp or $check_cur_mp or $check_eq_adj

  if $check_any Then
    ClickTasks()
    $start_stat_array = find_player_stat($STAT_MP, True, True)
	$cur_mp_start = $start_stat_array[0]
	$cur_mp_exp = $cur_mp_start - 25 * $times
	$max_mp_start = $start_stat_array[1]
  EndIf

  if $equipPer == True Then
    DoPer(2)
	Sleep($equip_wait)
  EndIf

  if $equipPer and $check_eq_adj Then
    $equip_recheck_array = find_player_stat($STAT_MP, True, True)
	$max_mp_post_equip = $equip_recheck_array[1]
	$exp_per_equip = $max_mp_start - $int_per_delta
	if $max_mp_start - $int_per_delta <> $max_mp_post_equip Then
	  MOKC("Potential failure equipping Personality", $exp_per_equip & " is what we should have, but " & $max_mp_post_equip & " is what we got.")
    EndIf
  EndIf

  ToHab()
  ToTasks()

  clickSkill($times, 2, 25, $delay)

  if $unequipPer == True Then
    DoInt(2)
  EndIf

  if $check_max_mp or $check_cur_mp Then
    $end_stat_array = find_player_stat($STAT_MP, True, True)
	$cur_mp_end = $end_stat_array[0]
	$max_mp_end = $end_stat_array[1]
	if $check_max_mp Then
	  if $max_mp_end <> $max_mp_start Then MOKC("WARNING MaxMP discrepancy before/after", $max_mp_end & " " & ($max_mp_end > $max_mp_start ? "greater" : "lower") & " than " & $max_mp_start)
	  if $max_mp_end == 0 or $max_mp_start == 0 Then MOKC("Uh oh, bad/no reading", "start MP = " & $max_mp_start & " end MP = " & $max_mp_end & $note_daily_force)
    EndIf
	if $check_cur_mp and ($cur_mp_exp <> $cur_mp_end) Then
	  $trade_casts = ($cur_mp_start - $cur_mp_end) / 25
	  MOKC("CurMP discrepancy before/after", $cur_mp_exp & " expected, " & $cur_mp_end & " actual." & @CRLF & "Check # of times you cast Tools. Wanted " & $times & " but it looks like only " & $trade_casts)
    EndIf
  EndIf

EndFunc

Func find_player_stat($whichStat = $STAT_MP, $find_max = True, $copy_new_in = True)
  local $stat_number = 0
  ;_ArrayDisplay($ary)

  ToHab()
  local $got_data = False
  local $loop_count = 0

  while not $got_data and $loop_count < 10
  $loop_count += 1
  if $copy_new_in Then
    Send("^a")
    sleep(500)
    Send("^c")
    sleep(500)
    $clip_in = ClipGet()
    Send("^f;")
    sleep(500)
    Send("{ESC}")
  Else
    $clip_in = ClipGet()
  EndIf

  local $ary = StringSplit($clip_in, @CR & @LF, $STR_ENTIRESPLIT)

  for $q = 1 to $ary[0]
    $line = $ary[$q]
    if StringInStr($ary[$q], " / ") Then
	  $stat_number += 1
      if $stat_number == 3 Then
	    $statData = StringSplit($line, "/")
		Local $retVal[2]
		$retVal[0] = Number($statData[1])
		$retVal[1] = Number($statData[2])
	    return $retVal
      EndIf
	EndIf
  Next

  if not $copy_new_in Then ExitLoop ; if we aren't looking at the webpage, it doesn't make sense to wait for it to reload

  sleep(1000)

  WEnd

  MOK("Cut/paste error", $copy_new_in ? "Current clipboard data is bad." : "Could not get meaningful data from webpage", True)

EndFunc

Func CheckClicks() ; this is not perfect but it does the job for now
  if $clicks < 1 and $clicks2 < 1 Then
	if $testRun Then
	  MOK("Just checking", "You are running 0 times for a test.")
    else
      MOK("Oops!", "Must specify -tr for test run or positive number of clicks after " & $cmdLine[0] & ".", True)
    EndIf
  Endif
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
  Local $metas[9] = [ 'as', 'om', 'te', '=', 's', 'ca', 'fo', 'fc', 'tr']
  Local $um = UBound($metas) - 1

  if StringRegExp($param, "^[0-9]+-[0-9]+$") Then Return True

  For $x = 0 to $um
    if $param == $metas[$x] Then Return True
  Next

  if not StringRegExp($param, "[0-9]+$") Then Return False

  Local $metas_need_num[1] = [ 'qd' ]
  Local $umn = UBound($metas_need_num) - 1

  $nextNum = StringRegExpReplace($param, "^[a-z]+", "")
  Local $myCmd = StringRegExpReplace($param, "[0-9]+$", "")

  For $x = 0 to $umn
    if $myCmd == $x Then Return True
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
      sleep($delay/2)
    Endif
  Next
EndFunc

Func FishItmBossDmg($fishTimes, $toggle_at_end = False, $adjustMouse = True, $fishToggle = True, $fishSlow = False, $everMouseMove = True, $anyDelay = True)
  local $multiplier = 1
  if $fishToggle and not $fishSlow Then $multiplier += 1
  local $locDelay = 1000
  if $fishSlow Then $locDelay = $delay
  if not $anyDelay Then $locDelay = 0
  if $adjustMouse Then
    ToHab()
    $mouseX = 670
    $mouseY = 300
  Else
    Local $aPos = MouseGetPos()
	$mouseX = $aPos[0]
	$mouseY = $aPos[1]
  EndIf
  for $i = 1 to $fishTimes * $multiplier
    sleep($locDelay)
	MouseClick("left", $mouseX, $mouseY, 1) ; click it on *and* off
	if $everMouseMove Then MouseMove($mouseX + 20, $mouseY) ; click it on *and* off
  Next
  if $toggle_at_end == True Then
    sleep($locDelay)
	MouseClick("left", $mouseX, $mouseY, 1)
	MouseMove($mouseX + 20, $mouseY) ;
  EndIf
  Beep(700, 700)
EndFunc

Func OpenHabiticaURL($closeWindow)
  Run("C:\Program Files (x86)\Mozilla Firefox\firefox -new-tab http://habitica.com")
  WinActivate("[CLASS:MozillaWindowClass]", "")
  WinWaitActive("[CLASS:MozillaWindowClass]")
  Send("{CTRLDOWN}9{CTRLUP}")
  if $closeWindow Then
	Sleep(1000)
    Send("{CTRLDOWN}w{CTRLUP}")
  EndIf
  $didAnything = True
EndFunc

Func open_for_cron($hours_after, $auto_close_after = True, $auto_visit_after = False)
  local $x = _Now()
  Local $aMyDate, $aMyTime
  _DateTimeSplit($x, $aMyDate, $aMyTime)

  Local $hours = $aMyTime[1]
  Local $minutes = $aMyTime[2]
  Local $seconds = $aMyTime[3]

  if StringInStr($x, "PM") Then
    $hours += 12
  EndIf

  if $hours_after > 24 or $hours_after < 0 Then
    MsgBox($MB_OK, "Oops", "Hours after/before must be between 0 and 24.")
    Exit()
  EndIf

  $secondsLeft = 86460 - 3600 * $hours - 60 * $minutes - $seconds + 3600 * $hours_after

  $dest_time = _DateAdd( 's', $secondsLeft, _NowCalc())
  MsgBox($MB_SYSTEMMODAL, "Auto-run Habitica " & $hours_after & " hours after cron", "Waiting " & $secondsLeft & " seconds until " & $dest_time)

  sleep($secondsLeft * 1000)

  RunWait(@ComSpec & " /c " & "start http://habitica.com")

  Sleep(12000)

  WinActivate("[CLASS:MozillaWindowClass]")
  WinWaitActive("[CLASS:MozillaWindowClass]")

  if $auto_close_after Then
    Send("^9")
    Sleep(3000)
    Send("^w")
  ElseIf $auto_visit_after Then
    Send("^9")
  EndIf

  Exit()

EndFunc

Func read_hab_cfg($x)
  $vars_file_handle = FileOpen($x, 0)
  Local $cfg_count = 0
  While 1
    $cfg_count += 1
    $line = FileReadLine($vars_file_handle)
	If StringLeft($line, 1) == '#' Then
	  ContinueLoop
	ElseIf StringLeft($line, 1) == ';' or StringLen($line) == 0 Then
	  ExitLoop
    EndIf
	$vars = StringSplit($line, ",")
	If verify_first_entry($vars, 'ItemPop', 3) Then
	  $item_popup_h = $vars[2]
	  $item_popup_v = $vars[3]
	ElseIf verify_first_entry($vars, 'Delay', 2) Then
	  $delay = $vars[2]
	  if $delay < 100 Then
	    $delay *= 1000
	  EndIf
    Elseif verify_first_entry($vars, 'Class', 2) Then
	  $my_class = StringLower($vars[2])
	  if $classHash.Exists($my_class) Then $my_class = $classHash.Item($my_class)
	  if $my_class < 1 or $my_class > 4 Then
	    MOK("Oops!", $vars[2] & " needs to be 1-4 or a class name (case insensitive) e.g. " & $allClasses)
		Exit
	  EndIf
    Elseif verify_first_entry($vars, 'DeltaHV', 3) Then
	  $horiz_delta = $vars[2]
	  $vert_delta = $vars[3]
    Elseif verify_first_entry($vars, 'PetFeedDelta', 4) Then
	  $pet_feed_init_x = $vars[2]
	  $pet_feed_init_y = $vars[3]
	  $pet_feed_delta = $vars[4]
    Elseif verify_first_entry($vars, 'PetFoodDelta', 5) Then
	  $pet_food_init_x = $vars[2]
	  $pet_food_init_y = $vars[3]
	  $pet_food_delta = $vars[4]
	  $pet_food_next_x = $vars[5]
    Elseif verify_first_entry($vars, 'IntPerDelta', 2) Then
	  $int_per_delta = $vars[2]
    Elseif verify_first_entry($vars, 'InitHV', 3) Then
	  $h_init_page_1 = $vars[2]
	  $v_init_page_1 = $vars[3]
    Elseif verify_first_entry($vars, 'PullInitDelt', 4) Then
	  $attr_pulldown_h_init = $vars[2]
	  $attr_pulldown_v_init = $vars[3]
	  $attr_pulldown_delta = $vars[4]
    Elseif verify_first_entry($vars, 'PgDownAdjust', 2) Then
	  $page_down_adjust = $vars[2]
    Elseif verify_first_entry($vars, 'EndHV', 2) Then
	  $last_row_after_end = $vars[2]
    Elseif verify_first_entry($vars, 'EquipWait', 2) Then
	  $equip_wait = $vars[2]
    Elseif not StringIsDigit($line) Then
	  MOK("Bad cfg line" & $cfg_count, $line)
	EndIf
	; MOK("This", $vars[1] & @CRLF & $line)
  WEnd
  FileClose($vars_file)
  if $my_class == $CLASS_UNDEF Then
    MOK("No class defined in hab.txt", "You may wish to define a class in hab.txt.")
  EndIf
EndFunc

Func verify_first_entry($var_array, $first_entry, $how_many_entries)
  if $var_array[1] <> $first_entry Then
    return False
  EndIf
  if $var_array[0] > $how_many_entries Then
    MOK("Cutting off extraneous entries", $first_entry & " has " & $var_array[0] & " needs " & $how_many_entries)
	return True
  EndIf
  if $var_array[0] < $how_many_entries Then
    MOK("Too few entries, bailing.", $first_entry & " has " & $var_array[0] & " needs " & $how_many_entries)
	Exit
  EndIf
  return True
EndFunc

Func MarkBuffsDone($which_stat = $CLASS_ROGUE, $bail = False)
  $time_file_handle = FileOpen($time_file, 0)
  if $time_file_handle == -1 Then MOK("Run -idf", "Can't open " & $time_file, True)
  $time_back = "c:\scripts\hab-t-back.txt"
  $time_back_handle = FileOpen($time_back, 2)
  While 1
    $line = FileReadLine($time_file_handle)
    If StringLen($line) == 0 Then ExitLoop
    if StringInStr($line, $which_stat & '=') Then
      FileWriteLine($time_back_handle, $which_stat & '=' & _NowCalcDate() & " " & _NowTime(5))
      $gotOne = True
      ContinueLoop
	EndIf
	FileWriteLine($time_back_handle, $line)
  WEnd
  FileClose($time_back_handle)
  FileClose($time_file_handle)
  if $gotOne Then FileCopy($time_back, $time_file, 1)
  RunWait("py c:\writing\scripts\dailies.py -rw hab")
  if $bail Then Exit()
EndFunc

Func CheckClass($desired_class)
   if $desired_class <> $my_class Then MOK("Oops!", "You shouldn't be running " & $my_class == $CLASS_ROGUE : "Tools of the Trade when not a rogue.", "Earthquake/Ethereal Surge when not a mage", True)
EndFunc

Func Usage($questionmark, $badCmd = "")
  Local $usgAry[20] = [ "-a, -as, -b, -c, -ca, -d, -e, -f, -i, -iw, -m/-w, -o, -p, -q, -r, -s/-=, -t or -x are the main options.", _
  "-a (or only a number in the arguments) opens the armoire # times. Negative number clicks where the mouse is # times", _
  "-as determines autosell value for rebirth (approximately)", _
  "-b does fiery blast, needs # and positioning", _
  "-c = open then close for cron, -co = keep open, -cv = (keep open and) visit after", _
  "-ca closes the tab after", _
  "-d adjusts delay, though it needs to come before other commands", _
  "-f fishes for items X times by double-clicking daily tasks (-fi). -ff = fixed XY where cursor is, -ft = toggle daily task status at end", _
  "-fe = feeds pet #X Y times (feXY). ffe or fef (force feed) skips checking if you're on the stable page.", _
  "-i = intelligence gear", _
  "-iw = initial wait", _
  "-m / -w = mage skills, 1st # = ethereal surge, 2nd # = earthquake, -e does 2 surge 1 earthquake per #. -mm, -wm, -em mark mage buffs as done for the day.", _
  "-md = mark buffs done in case a script terminated and I got to do what I wanted anyway", _
  "-o = only click tasks: test option", _
  "-p = perception gear", _
  "-q = quick click in upper right (to get rid of gain reports)", _
  "-r = repeated habit on the left column, needs # and positioning", _
  "-s or -= = gives starting MP so you can see final MP as well", _
  "-t / -tt (tools of the trade) needs a number after for clicks, with an optional second for delays.", _
  "-x (eXpress) equips perception outfit, runs Tools (#) times and re-equips the intelligence outfit. q ignores the nag. e only equips. r only reequips. -xm/-tm/-ttm marks tools of the trade as run for the day." _
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
