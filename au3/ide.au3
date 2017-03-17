#include <MsgBoxConstants.au3>

Local $project = "buck-the-past";
Local $stuff = 1;
Local $build = 1;

if $CmdLine[0] > 0 Then
  if $CmdLine[$stuff] == "nb" Then
    $build = 0;
	$stuff = $stuff + 1;
  Endif
  $project = $CmdLine[$stuff];
  if $CmdLine[$stuff] == "b" Then
    call("openIDE", "basic");
  ElseIf $CmdLine[$stuff] == "d" Then
    call("openIDE", "dirk");
  ElseIf $CmdLine[$stuff] == "s" Then
    call("openIDE", "shuffling");
  ElseIf $CmdLine[$stuff] == "sa" Then
    call("openIDE", "shuffling");
  ElseIf $CmdLine[$stuff] == "r" Then
    call("openIDE", "roiling");
  ElseIf $CmdLine[$stuff] == "ro" Then
    call("openIDE", "roiling");
  ElseIf $CmdLine[$stuff] == "roi" Then
    call("openIDE", "roiling");
  ElseIf $CmdLine[$stuff] == "pc" Then
    call("openIDE", "Compound");
  ElseIf $CmdLine[$stuff] == "sc" Then
    call("openIDE", "slicker-city");
  ElseIf $CmdLine[$stuff] == "3" Then
    call("openIDE", "threediopolis");
  ElseIf $CmdLine[$stuff] == "4" Then
    call("openIDE", "fourdiopolis");
  ElseIf $CmdLine[$stuff] == "3d" Then
    call("openIDE", "threediopolis");
  ElseIf $CmdLine[$stuff] == "4d" Then
    call("openIDE", "fourdiopolis");
  ElseIf $CmdLine[$stuff] == "as" Then
    call("openIDE", "Compound");
	call("openIDE", "slicker-city");
	call("openIDE", "buck-the-past");
  ElseIf $CmdLine[$stuff] == "opo" Then
    call("openIDE", "threediopolis");
	call("openIDE", "fourdiopolis");
  ElseIf $CmdLine[$stuff] == "sts" Then
    call("openIDE", "roiling");
	call("openIDE", "sa");
  ElseIf $CmdLine[$stuff] == "" Then
    call("openIDE", "slicker-city");
  ElseIf $CmdLine[$stuff] == "btp" Then
    call("openIDE", "buck-the-past");
  ElseIf $CmdLine[$stuff] == "in" Then
    call("openIDE", "grubbyville");
  ElseIf $CmdLine[$stuff] == "e16" Then
    call("openIDE", "ectocomp16");
  ElseIf $CmdLine[$stuff] == "e15" Then
    call("openIDE", "heezy-park");
  ElseIf $CmdLine[$stuff] == "e14" Then
    call("openIDE", "Candy Rush Saga");
  ElseIf $CmdLine[$stuff] == "e13" Then
    call("openIDE", "ghost");
  ElseIf $CmdLine[$stuff] == "e11" Then
    call("openIDE", "dash");
  ElseIf $CmdLine[$stuff] == "ss" Then
    call("openIDE", "seeker-status");
  Else
    call("openIDE", $CmdLine[$stuff]);
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

  if $build == 1 Then
    sleep(1);
    WinWaitActive($project & ".inform");
    Send("{F5}");
    $x = ControlGetHandle(".inform", "", "[CLASS:ToolbarWindow32; INSTANCE:2]");
  Endif
  Beep (600, 200)

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
