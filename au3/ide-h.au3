; this is the header file for id3.au3
; it defines miscellaneous hash values that can't easily be set in i7p.txt

$wthruHash = ObjCreate("Scripting.Dictionary")

If @error Then
  MsgBox(0, '', 'Error creating the dictionary object')
Else
  $wthruHash.Add ("ailihphilia", "rollup")
EndIf

$waitHash = ObjCreate("Scripting.Dictionary")

If @error Then
  MsgBox(0, '', 'Error creating the dictionary object')
Else
  $waitHash.Add ("ailihphilia", 20)
EndIf