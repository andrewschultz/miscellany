#include <MsgBoxConstants.au3>

Local $project = "Compound";

if $CmdLine[0] > 0 Then
  $project = $CmdLine[1];
  if $CmdLine[1] == "b" Then
    call("openIDE", "basic");
  ElseIf $CmdLine[1] == "d" Then
    call("openIDE", "dirk");
  ElseIf $CmdLine[1] == "s" Then
    call("openIDE", "shuffling");
  ElseIf $CmdLine[1] == "sa" Then
    call("openIDE", "shuffling");
  ElseIf $CmdLine[1] == "r" Then
    call("openIDE", "roiling");
  ElseIf $CmdLine[1] == "ro" Then
    call("openIDE", "roiling");
  ElseIf $CmdLine[1] == "roi" Then
    call("openIDE", "roiling");
  ElseIf $CmdLine[1] == "pc" Then
    call("openIDE", "Compound");
  ElseIf $CmdLine[1] == "sc" Then
    call("openIDE", "slicker-city");
  ElseIf $CmdLine[1] == "3d" Then
    call("openIDE", "threediopolis");
  ElseIf $CmdLine[1] == "4d" Then
    call("openIDE", "fourdiopolis");
  ElseIf $CmdLine[1] == "as" Then
    call("openIDE", "Compound");
	call("openIDE", "slicker-city");
	call("openIDE", "buck-the-past");
  ElseIf $CmdLine[1] == "opo" Then
    call("openIDE", "threediopolis");
	call("openIDE", "fourdiopolis");
  ElseIf $CmdLine[1] == "sts" Then
    call("openIDE", "roiling");
	call("openIDE", "sa");
  ElseIf $CmdLine[1] == "" Then
    call("openIDE", "slicker-city");
  ElseIf $CmdLine[1] == "btp" Then
    call("openIDE", "buck-the-past");
  ElseIf $CmdLine[1] == "in" Then
    call("openIDE", "grubbyville");
  ElseIf $CmdLine[1] == "e16" Then
    call("openIDE", "ectocomp16");
  ElseIf $CmdLine[1] == "e15" Then
    call("openIDE", "heezy-park");
  ElseIf $CmdLine[1] == "e14" Then
    call("openIDE", "Candy Rush Saga");
  ElseIf $CmdLine[1] == "e13" Then
    call("openIDE", "ghost");
  ElseIf $CmdLine[1] == "e11" Then
    call("openIDE", "dash");
  Else
    call("openIDE", $CmdLine[1]);
  Endif
Else
  call("openIDE", $project);
Endif

Func OpenIDE($project)
  run("C:\\Program Files (x86)\\Inform 7\\Inform7.exe");
  sleep(1);

  WinWaitActive("Welcome to Inform 7");

  Send("!O");

  sleep(1);
  WinWaitActive("Open a project", "Project &name");

  Send("c:\games\inform\" & $project & ".inform!O");

  sleep(1);
  WinWaitActive($project & ".inform");

  Send("{F5}");

  $x = ControlGetHandle(".inform", "", "[CLASS:ToolbarWindow32; INSTANCE:2]");
EndFunc

; MsgBox(4096, '', @AutoItVersion) ; 4096 = $MB_SYSTEMMODAL
; MsgBox($MB_OK, $x, $x);

#comments-start
if ($CmdLine[0] > 1) Then
  Sleep($CmdLine[2]);
  Send("test win" & @CRLF);
endif
#comments-end

#comments-start
if ($CmdLine[0] > 1) Then
  Sleep(1000);
  Do
    Sleep(100);
  Until ControlCommand (".inform", "", 59392, "IsEnabled", "");
  Send("test win" & @CRLF);
Endif
#comments-end
