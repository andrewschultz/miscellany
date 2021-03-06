;header file for hab.au3
;originally not part of GitHub but moved there once I realized I didn't 

; note: it would make sense if the attributes were in the same order as the classes, but they aren't. So we need to re-define them. (con=healer str=warrior int=mage)
Global $attrHash = ObjCreate("Scripting.Dictionary")

$attrHash.add("none", 0)
$attrHash.add("constitution", 1)
$attrHash.add("perception", 2)
$attrHash.add("strength", 3)
$attrHash.add("intelligence", 4)

Global $classHash = ObjCreate("Scripting.Dictionary")

$classHash.add("none", 0)
$classHash.add("warrior", 1)
$classHash.add("wizard", 2)
$classHash.add("mage", 2)
$classHash.add("healer", 3)
$classHash.add("rogue", 4)

Local $allClasses = "Classes:"

for $myKey in $classHash.keys
  $allClasses &= " " & $myKey & "/" & $classHash.Item($myKey)
Next

; still useful to match up with class_hash above. Don't delete.
Const $CLASS_UNDEF = 0, $CLASS_WARRIOR = 1, $CLASS_WIZARD = 2, $CLASS_HEALER = 3, $CLASS_ROGUE = 4

; constants for mage skill names, which are the ones I'm most likely to use variably
Const $BURST_OF_FLAME = 0, $ETHEREAL_SURGE = 1, $EARTHQUAKE = 2, $CHILLING_FROST = 3

; constants for stats to track with find_player_stat. $STAT_MP is most worth tracking.
Const $STAT_HP = 1, $STAT_EXP = 2, $STAT_MP = 3

; constants for where to click on a skill
Local $xi = 540, $yi = 980, $xd = 190
Local $delay = 6000

; I don't need to change this when changing class. This should be changed in hab.txt under the "Class," line.
Local $my_class = $CLASS_UNDEF

Local $ITEM_POSITION = 0
Local $EQUIP_POSITION = 1
Local $STABLE_POSITION = 2
