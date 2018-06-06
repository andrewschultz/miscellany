;
; ide.au3
;
; opens Inform IDE and pushes F5 automatically
;

#include "ide-h.au3"
#include <MsgBoxConstants.au3>
#include <Date.au3>

Local $project = EnvGet("PROJ")
Local $stuff = 1;
Local $build = 1;

; $toRead is defined in ide-h.au3
;
; $projHash = ObjCreate("Scripting.Dictionary")
; $projHash.Add ("d",   "dirk")
;
; this is not included here b/c changing the default would mean another github pull/push
; plus there are private projects
;

Opt("WinTitleMatchMode", -2)

Local $cmdCount = 0

While $cmdCount <= $CmdLine[0]
  if $CmdLine[1] == '0' Then
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
    MsgBox($MB_OK, "List of projects", $cmdStr)
    Exit
  Endif
  $cmd = StringLower($CmdLine[$cmdCount])
  if $cmd == 'w' or $cmd == '-w' Then
    $walkthrough = 1
	$cmdCount = $cmdCount + 1
	ContinueLoop
  Else
    $project = $CmdLine[$cmdCount]
    if $projHash.Exists($project) Then
      $project = $projHash.Item($project)
    Endif
  EndIf
  $cmdCount = $CmdCount + 1
WEnd

if $walkthrough Then
  if not $wthruHash.Exists($project) Then
    MsgBox($MB_OK, "Nothing to walkthrough", $project)
    Exit
  EndIf
  if not $waitHash.Exists($project) Then
    MsgBox($MB_OK, "No waithash entry", $project)
    Exit
  EndIf
EndIf

Local $dirToCheck = "c:\\games\\inform\\" & $project & ".inform"

if not FileExists($dirToCheck) Then
  if $project = EnvGet("PROJ") Then
    MsgBox($MB_OK, "No such default directory", "The default directory does not exist. You may need to change the PROJ environment variable.")
  Else
    MsgBox($MB_OK, "no such directory", $dirToCheck & @CRLF & "ide.au3 0 shows all projects and mappings." & @CRLF & "ide-h.au3 is where to add stuff.")
  EndIf
  Exit
EndIf

OpenIDE($project)

;
; end main
;
; function(s) below
;

Func OpenIDE($project)
  $toCheck = "[REGEXPTITLE:$project" & ".inform\*? - Inform]"
  $pwin = $project & ".inform - Inform"
  if (WinExists($toCheck)) Then
    Local $fileTimeA = FileGetTime($dirToCheck & "\\source\\story.ni", $FT_MODIFIED, $FT_ARRAY)
	$fileTime = $fileTimeA[0] & "/" & $fileTimeA[1] & "/" & $fileTimeA[2] & " " & $fileTimeA[3] & ":" & $fileTimeA[4] & ":" & $fileTimeA[5]
	Local $nowTime = _NowCalc()
	Local $dd = _DateDiff('h', $fileTime, $nowTime)

	if $dd >= 23 and not $walkthrough Then
      ; MsgBox($MB_OK, $dd & " hours since last change, not building", "Blah")
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

  if $build == 1 Then
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
