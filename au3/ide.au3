;
; ide.au3
;
; opens Inform IDE and pushes F5 automatically
;

#include "ide-h.au3"
#include <MsgBoxConstants.au3>
#include <Date.au3>

Local $project = "buck-the-past";
Local $stuff = 1;
Local $build = 1;

; $toRead is defined in ide-h.au3
;
; $hash = ObjCreate("Scripting.Dictionary")
; $hash.Add ("d",   "dirk")
;
; this is not included here b/c changing the default would mean another github pull/push
; plus there are private projects
;

Opt("WinTitleMatchMode", -2)

if $CmdLine[0] > 0 Then
  if $CmdLine[1] == '0' Then
    Local $cmdStr = ""
	Local $count = 0
    For $key In $hash
	  if Mod($count, 3) > 0 Then
	    $cmdStr = $cmdStr & " / "
	  ElseIf $count > 0 Then
	    $cmdStr = $cmdStr & @CRLF
	  Endif
	  $count = $count + 1
	  $cmdStr = $cmdStr & $key & " " & $hash.Item($key)
    Next
	if Mod ($count, 2) == 1 Then
	  $cmdStr = $cmdStr & @CRLF
    Endif
	$cmdStr = $cmdStr & @CRLF & $count & " total projects. ide-h.au3 is where to add stuff."
    MsgBox($MB_OK, "List of projects", $cmdStr)
    Exit
  Endif
  $project = $CmdLine[1]
  if $hash.Exists($project) Then
    $project = $hash.Item($project)
  Endif
Endif

Local $dirToCheck = "c:\\games\\inform\\" & $project & ".inform"

if not FileExists($dirToCheck) Then
  MsgBox($MB_OK, "no such directory", $dirToCheck & @CRLF & "ide.au3 0 shows all projects and mappings." & @CRLF & "ide-h.au3 is where to add stuff.")
  Exit
EndIf

OpenIDE($project)

;
; end main
;
; function(s) below
;

Func OpenIDE($project)
  if (WinExists($project & ".inform - Inform")) Then
    Local $fileTimeA = FileGetTime($dirToCheck & "\\source\\story.ni", $FT_MODIFIED, $FT_ARRAY)
	$fileTime = $fileTimeA[0] & "/" & $fileTimeA[1] & "/" & $fileTimeA[2] & " " & $fileTimeA[3] & ":" & $fileTimeA[4] & ":" & $fileTimeA[5]
	Local $nowTime = _NowCalc()
	Local $dd = _DateDiff('h', $fileTime, $nowTime)
	if $dd > 23 Then
      ; MsgBox($MB_OK, $dd & " hours since last change, not building", "Blah")
      WinActivate($project & ".inform");
      WinWaitActive($project & ".inform");
	  return
    Endif
  Endif
  if (WinExists($project & ".inform - Inform")) or (WinExists($project & ".inform* - Inform")) Then
    WinActivate($project & ".inform");
    WinWaitActive($project & ".inform");
  Else
  run("C:\\Program Files (x86)\\Inform 7\\Inform7.exe");
  sleep(1);

  WinWaitActive("Welcome to Inform 7");

  Send("!O");

  sleep(1);
  WinWaitActive("Open a project", "Project &name");

  Send("c:\games\inform\" & $project & ".inform!O");

  Endif

  if $build == 1 Then
    sleep(1);
    WinWaitActive($project & ".inform");
    Send("{F5}");
    $x = ControlGetHandle(".inform", "", "[CLASS:ToolbarWindow32; INSTANCE:2]");
  Endif
  Beep (600, 200)

EndFunc
