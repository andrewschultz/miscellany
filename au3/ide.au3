;
; ide.au3
;
; opens Inform IDE and pushes F5 automatically
;

#include <Array.au3>
#include <File.au3>

#include "ide-h.au3"
#include <MsgBoxConstants.au3>
#include <Date.au3>
#include "c:\\scripts\\andrew.au3"
#include <File.au3>

Local $project = EnvGet("PROJ")
Local $stuff = 1;
Local $walkthrough = 0;
Local $force_build = 0;
Local $i7p = "c:/writing/scripts/i7p.txt"
Local $hdr_array[0]

Local $hours = 23

Global $projHash

Opt("WinTitleMatchMode", -2)

Local $cmdCount = 1

ReadProjectHash()

While $cmdCount <= $CmdLine[0]
  ; MOK($cmdCount, $CmdLine[$cmdCount])
  $arg = $CmdLine[$cmdCount]
  $a1 = StringLeft($arg, 1)
  if $arg == '0' Then
    Local $cmdStr = ""
	Local $count = 0
    For $key In $projHash
	  if Mod($count, 3) > 0 Then
	    $cmdStr = $cmdStr & " / "
	  ElseIf $count > 0 Then
	    $cmdStr = $cmdStr & @CRLF
	  Endif
	  $count = $count + 1
	  $cmdStr = $cmdStr & $key & " " & $projHash.Item($key)
    Next
	if Mod ($count, 2) == 1 Then
	  $cmdStr = $cmdStr & @CRLF
    Endif
	$cmdStr = $cmdStr & @CRLF & $count & " total projects. ide-h.au3 is where to add stuff."
    MOK("List of projects", $cmdStr)
    Exit
  Elseif $a1 == 'd' or $a1 == 'h' Then
    $num = StringMid($cmd, 2)
	if not StringIsDigit($num) Then
	  MOK("Need number right after d/h", "d20 or h20 is ok, d 20 or h 20 is not")
	  Exit
    EndIf
	$hours = $num
	if StringLeft($arg, 1) == 'h' Then
	  $hours *= 24
    EndIf
    $hours -= 1
  Elseif $arg == 'f' Then
    $force_build = 1
  Elseif $arg == 'nf' or $arg == 'fn' or $arg == 'n' Then
    $force_build = -1
  Elseif $arg == 'w' or $arg == '-w' Then
    $walkthrough = 1
	$cmdCount = $cmdCount + 1
  Elseif $arg == '?' Then
    Usage(1, "")
  Else
    $project = $arg
    if $projHash.Exists($project) Then
      $project = $projHash.Item($project)
    Else
	  MOK("No project for " & $project, "ide.au3 0 shows all projects and mappings." & @CRLF & "ide-h.au3 is where to add stuff." & @CRLF & "? shows usage.")
    EndIf
  EndIf
  $cmdCount = $CmdCount + 1
WEnd

FindProjHeaderFiles($project)

if $walkthrough Then
  if not $wthruHash.Exists($project) Then
    MOK("Need wthruhash entry", "Define wthruhash entry for " & $project & " in ide-h.au3.")
    Exit
  EndIf
  if not $waitHash.Exists($project) Then
    MOK("Need waithash entry", "Define waithash entry for " & $project & " in ide-h.au3.")
    Exit
  EndIf
EndIf

Local $dirToCheck = "c:\\games\\inform\\" & $project & ".inform"

if not FileExists($dirToCheck) Then
  if $project = EnvGet("PROJ") Then
    MOK("No such default directory", "The default directory does not exist. You may need to change the PROJ environment variable.")
  Else
    MOK("no such directory", $dirToCheck & @CRLF & "ide.au3 0 shows all projects and mappings." & @CRLF & "ide-h.au3 is where to add stuff.")
  EndIf
  Exit
EndIf

OpenIDE($project)

;
; end main
;
; function(s) below
;

Func ReadProjectHash()

  Local $aInput
  $file = $i7p
  _FileReadToArray($file, $aInput)
  $projHash = ObjCreate("Scripting.Dictionary")

  For $i = 1 to UBound($aInput) - 1
	if StringLeft($aInput[$i], 1) == '#' Then
	  ContinueLoop
    EndIf
	if StringInStr($aInput[$i], ":") Then
	  ContinueLoop
	EndIf
    ; MsgBox ($MB_OK, "Line # " & $i, $aInput[$i])
	if not StringInStr($aInput[$i], "=") Then
	  ContinueLoop
    EndIf
	$my_ary = StringSplit($aInput[$i], "=")
	$my_from = StringSplit($my_ary[2], ",")
	for $j = 1 to UBound($my_from) - 1
      ; MsgBox ($MB_OK, "Line # " & $i, "From: " & $my_from[$j] & @CRLF & "To: " & $my_ary[1])
	  $projHash.add($my_from[$j], $my_ary[1])
	Next
  Next

EndFunc

Func FindProjHeaderFiles($p)
  $auxil_file_handle = FileOpen($i7p)
  $head_dir = "c:\Program Files (x86)\Inform 7\Inform7\Extensions\Andrew Schultz"
  While $line
    $line = FileReadLine($auxil_file_handle)
	If StringLeft($line, 1) == '#' Then
	  ContinueLoop
	ElseIf StringLeft($line, 1) == ';' or StringLen($line) == 0 Then
	  ExitLoop
    EndIf
	if StringRegExp($line, "^HEADER(S)?:") Then
	  $l2 = StringRegExpReplace($line, "^[A-Z]+:", "")
      $vars = StringSplit($l2, "=")
	  if $vars[1] <> $p Then
	    ContinueLoop
	  EndIf
	  if $vars[0] < 2 Then
	    MOK("WARNING BAD LINE", $line)
	  ElseIf $vars[0] > 2 Then
	    MOK("WARNING TOO MANY VARS", $line)
	  EndIf
	  $hdrs = StringSplit($vars[2], ",")
	  For $i = 1 to $hdrs[0]
	    $temp = $head_dir & "\" & $vars[1] & " " & $hdrs[$i] & ".i7x"
		_ArrayAdd($hdr_array, $temp)
	  Next
    EndIf
  WEnd
  FileClose($auxil_file_handle)
  ; _ArrayDisplay($hdr_array, "!")
EndFunc

Func see_time_diff($x, $h)
    Local $fileTimeA = FileGetTime($x, $FT_MODIFIED, $FT_ARRAY)
	$fileTime = $fileTimeA[0] & "/" & $fileTimeA[1] & "/" & $fileTimeA[2] & " " & $fileTimeA[3] & ":" & $fileTimeA[4] & ":" & $fileTimeA[5]
	Local $nowTime = _NowCalc()
	Local $dd = _DateDiff('h', $fileTime, $nowTime)
	return $dd < $h
EndFunc

Func OpenIDE($project)
  $toCheck = "[REGEXPTITLE:$project" & ".inform\*? - Inform]"
  $pwin = $project & ".inform - Inform"
  $any_today = see_time_diff($dirToCheck & "\\source\\story.ni", $hours)
  for $i = 0 to UBound($hdr_array) - 1
    $temp = StringRegExpReplace($hdr_array[$i], "-", " ")
	$any_today &= see_time_diff($temp, $hours)
  Next
  if (WinExists($toCheck)) Then
	if not $any_today and not $walkthrough and $force_build <> -1 Then
      ; MOK($dd & " hours since last change, not building", "Blah")
	  ; only activate this
      WinActivate($toCheck);
      WinWaitActive($toCheck);
	  return
    Endif
  Endif
  if (WinExists($pwin)) or (WinExists($project & ".inform* - Inform")) Then
    WinActivate($pwin);
    WinWaitActive($pwin);
  Else
  ; open the window
  run("C:\\Program Files (x86)\\Inform 7\\Inform7.exe");
  sleep(1);

  WinWaitActive("Welcome to Inform 7");

  Send("!O");

  sleep(1);
  WinWaitActive("Open a project", "Project &name");

  Send("c:\games\inform\" & $project & ".inform!O");

  Endif

  if $force_build <> -1 Then
    sleep(1000);
    WinWaitActive($project & ".inform - Inform");
    sleep(1000);
    MouseClick ( "left", 50, 50, 1 )
    ; Send("{F5}");
    $x = ControlGetHandle(".inform - Inform", "", "[CLASS:ToolbarWindow32; INSTANCE:2]");
  Endif
  Beep (600, 200)

  if $walkthrough Then
    MouseClick ( "left", 1200, 800, 1 )
	Sleep(40000)
	Send("test " & $wthruHash.item($project) & @CRLF)
  EndIf

EndFunc

Func Usage($questionmark, $badCmd = "")
  Local $usgAry[5] = [ "-d, -f, -fn, -nf, -h", _
  "-d specifies days back changes are ok", _
  "-h specifies hours back changes are ok", _
  "-f forces a build", _
  "-fn/nf forces no build" _
  ]
  Local $header = "Bad/missing parameter(s)"

  if $questionmark Then
    $header = "IDE.AU3 command line argument usage popup box"
  EndIf

  if $badCmd Then
    $header = $header & " " & $badCmd
  EndIf

  MOK($header,  _ArrayToString($usgAry, @CRLF, 0, UBound($usgAry)-1))
  Exit
EndFunc
