Local $project = "Compound";

if $CmdLine[0] > 0 Then
  $project = $CmdLine[1];
  if $CmdLine[1] == "pc" Then
    $project = "Compound";
  Endif
  if $CmdLine[1] == "sc" Then
    $project = "Compound";
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

WinWaitActive("Open a project");

Send("c:\games\inform\" & $project & ".inform!O");

WinWaitActive($project & ".inform - Inform");

Send("{F5}");



