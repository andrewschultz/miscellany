Local $project = "Compound";

if $CmdLine[0] > 0 Then
  $project = $CmdLine[1];
  if $CmdLine[1] == "b" Then
    $project = "basic";
  Endif
  if $CmdLine[1] == "d" Then
    $project = "dirk";
  Endif
  if $CmdLine[1] == "s" Then
    $project = "sa";
  Endif
  if $CmdLine[1] == "r" Then
    $project = "roiling";
  Endif
  if $CmdLine[1] == "roi" Then
    $project = "roiling";
  Endif
  if $CmdLine[1] == "pc" Then
    $project = "Compound";
  Endif
  if $CmdLine[1] == "sc" Then
    $project = "slicker-city";
  Endif
  if $CmdLine[1] == "3d" Then
    $project = "threediopolis";
  Endif
  if $CmdLine[1] == "4d" Then
    $project = "fourdiopolis";
  Endif
Endif

run("C:\\Program Files (x86)\\Inform 7\\Inform7.exe");

WinWaitActive("Welcome to Inform 7");

Send("!O");

WinWaitActive("Open a project", "Project &name");

Send("c:\games\inform\" & $project & ".inform!O");

WinWaitActive($project & ".inform");

Send("{F5}");

#comments-start
if ($CmdLine[0] > 1) Then
  Sleep(1000);
  Do
    Sleep(100);
  Until ControlCommand (".inform", "", 59392, "IsEnabled", "");
  WinClose($project & ".inform");
Endif
#comments-end
