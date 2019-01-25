; this is the header file for id3.au3
; it defines miscellaneous hash values that can't easily be set in i7p.txt

Local $ide_special_file = "c:/writing/scripts/ide.txt"
Local $any_error = False

$wthruHash = ObjCreate("Scripting.Dictionary")

If @error Then
  MsgBox(0, '', 'Non-fatal error creating the walkthrough hash dictionary object')
  $any_error = True
EndIf

$waitHash = ObjCreate("Scripting.Dictionary")

If @error Then
  MsgBox(0, '', 'Non-fatal error creating the wait-x-seconds dictionary object')
  $any_error = True
EndIf

If not $any_error Then
  $auxil_file_handle = FileOpen($ide_special_file)
  $line = "!"
  While $line
    $line = FileReadLine($auxil_file_handle)
	If StringLeft($line, 1) == '#' Then
	  ContinueLoop
	ElseIf StringLeft($line, 1) == ';' or StringLen($line) == 0 Then
	  ExitLoop
    EndIf
	if StringRegExp($line, "^(WTHRU|WAIT):") Then
	  $l2 = StringRegExpReplace($line, "^[A-Z]+:", "")
      $vars = StringSplit($line, ",")
	  if $vars[0] < 2 Then
	    MOK("WARNING BAD LINE", $line)
	  ElseIf $vars[0] > 2 Then
	    MOK("WARNING TOO MANY VARS", $line)
	  EndIf
	  if StringLeft($line, 4) == "WAIT" Then
	    $waitHash($vars[1]) = $vars[2]
	  Else
	    $wthruHash($vars[1]) = $vars[2]
	  EndIf
    EndIf
  WEnd
  FileClose($auxil_file_handle)
EndIf

; $wthruHash.Add ("ailihphilia", "rollup")
;  $waitHash.Add ("ailihphilia", 20)
