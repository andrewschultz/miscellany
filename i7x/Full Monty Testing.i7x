Version 1/161019 of Full Monty Testing by Andrew Schultz begins here.

"Runs tests on a game according to what the player asks for"

volume montying

montying is an action applying to one topic.

ignore-widdershins is a truth state that varies.

widdershins is a direction. turnwise is a direction. the opposite of widdershins is turnwise. the opposite of turnwise is widdershins.

chapter main monty table

this is the try-exits rule:
	try exitsing;

this is the try-inventory rule:
	try taking inventory;

this is the try-smelling rule:
	try smelling;

this is the try-listening rule:
	try listening;

this is the try-scoring rule:
	try requesting the score;

this is the try-wid rule:
	try going widdershins;

tracked-room is a room that varies.

this is the try-dirs rule:
	now tracked-room is location of player;
	say "[tracked-room] = base room.";
	shift-player inside;
	shift-player outside;
	shift-player east;
	shift-player west;
	shift-player south;
	shift-player north;
	unless ignore-widdershins:
		shift-player widdershins;
		shift-player turnwise;

to shift-player (Q - a direction):
	say "Going [Q] from [location of the player]:";
	try going q;
	move player to tracked-room, without printing a room description;

this is the try-think rule:
	try thinking;

this is the try-sleep rule:
	try sleeping;

chapter main monty verb

understand the command "monty" as something new.

understand "monty" as a mistake ("[monty-sum]")

to say monty-sum:
	say "MONTY usage for running a test-command every move:[paragraph break]";
	repeat through table of monties:
		say "[2da][test-title entry] can be turned on/off with [topic-as-text entry][line break]";
	say "[line break]MONTY FULL/ALL and MONTY NONE tracks all these every-move tries, or none of them.[no line break]";

understand "monty [text]" as montying.

monty-full is a truth state that varies.

carry out montying:
	let found-toggle be false;
	if the topic understood matches "all" or the topic understood matches "full":
		repeat through table of monties:
			now on-off entry is true;
		the rule succeeds;
	if the topic understood matches "none":
		repeat through table of monties:
			now on-off entry is false;
		the rule succeeds;
	repeat through table of monties:
		if the topic understood matches montopic entry:
			now on-off entry is whether or not on-off entry is false;
			say "[test-title entry] is now [if on-off entry is true]on[else]off[end if].";
			now found-toggle is true;
	if found-toggle is false:
		say "That wasn't a recognized flag for MONTY.[paragraph break][monty-sum][line break]";
	the rule succeeds;

table of monties
montopic (topic)	on-off	test-title (text)	test-action	topic-as-text (text)
"exits"	false	"LISTING EXITS"	try-exits rule	"exits"
"i/inventory"	false	"INVENTORY"	try-inventory rule	"i/inventory"
"s/smell"	false	"SMELLING"	try-smelling rule	"s/smell"
"l/listen"	false	"LISTENING"	try-listening rule	"l/listen"
"sc/score"	false	"SCORING"	try-scoring rule	"sc/score"
"dir/noway"	false	"GOING NOWHERE"	try-wid rule	"dir/noway"
"dirs"	false	"GOING BASIC DIRS"	try-dirs rule	"dirs"
"think"	false	"THINK tracking"	try-think rule	"think"
"sleep"	false	"SLEEP tracking"	try-sleep rule	"sleep"

hide-headers is a truth state that varies.

every turn (this is the full monty test rule) :
	let test-output-yet be false;
	repeat through table of monties:
		if on-off entry is true:
			if test-output-yet is false and hide-headers is false, say "========START TESTS[line break]";
			now test-output-yet is true;
			if hide-headers is false, say "========[test-title entry]:[line break]";
			follow the test-action entry;
	if test-output-yet is true and hide-headers is false:
		say "========END TESTS[line break]";

chapter montyhing

montyhing is an action out of world.

understand the command "montyh" as something new.

understand "montyh" as montyhing.

carry out montyhing:
	now hide-headers is whether or not hide-headers is false;
	say "Hide-headers is now [if hide-headers is true]on[else]off[end if].";
	the rule succeeds;

chapter montyiing

montyiing is an action out of world.

understand the command "montyi" as something new.

understand "montyi" as montyiing.

carry out montyiing:
	now ignore-widdershins is whether or not ignore-widdershins is false;
	say "ignore-widdershins is now [if ignore-widdershins is true]on[else]off[end if].";
	the rule succeeds;

Full Monty Testing ends here.

---- DOCUMENTATION ----
