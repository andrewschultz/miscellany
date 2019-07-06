Version 1/151212 of In-Game Mapping by Andrew Schultz begins here.

"Writes a text map of a game"

Volume the main map thing

map-room-height is a number that varies. map-room-height is usually 1.

map-room-width is a number that varies. map-room-width is usually 1.

a room can be map-pinged. a room is usually not map-pinged.

chapter maping

maping is an action out of world.

understand the command "map" as something new.

understand "map" as maping.

carry out maping:
	print-current-map;
	the rule succeeds;

to print-current-map:
	if number of mappable rooms is 0:
		say "Nothing to map.";
		continue the action;
	if number of mappable rooms is 1:
		say "This is the only room to map. Once you explore another, this command will be more interesting and informative.";
		continue the action;
	say "[fixed letter spacing]";
	let xmi be xmin;
	let ymi be ymin;
	let xma be xmax;
	let yma be ymax;
	let found-one be false;
	repeat with q running from ymi to yma:
		repeat with r running from xmi to xma: [print top text]
			now found-one is false;
			repeat through table of map coordinates:
				if r is x entry and q is y entry:
					now found-one is true;
					if rm entry is mappable:
						say "[l1 entry]";
					else:
						say "     ";
					unless room east of rm entry is nowhere or rm entry is unvisited:
						say "=";
					else:
						say " ";
			unless found-one is true:
				say "      ";
		say "[line break]";
		repeat with r running from xmi to xma: [print bottom text]
			now found-one is false;
			repeat through table of map coordinates:
				if r is x entry and q is y entry:
					if rm entry is mappable:
						say "[l2 entry]";
					else:
						say "     ";
					now found-one is true;
					say " ";
			unless found-one is true:
				say "      ";
		say "[line break]";
		repeat with r running from xmi to xma: [vertical right here]
			repeat through table of map coordinates:
				let drawVert be false;
				if r is x entry and q is y entry:
					if room south of rm entry is not nowhere:
						if rm entry is visited or room south of rm entry is visited:
							now drawVert is true;
					if drawVert is true:
						say "  |  ";
					else:
						say "     ";
			say " [no line break]"; [reserved for diagonal later]
		say "[line break]";
	say "[variable letter spacing]";

to decide what number is xmin:
	let temp be -1;
	repeat through table of map coordinates:
		if rm entry is mappable:
			if x entry < temp or temp is -1:
				now temp is x entry;
	decide on temp;

to decide what number is ymin:
	let temp be -1;
	repeat through table of map coordinates:
		if rm entry is mappable:
			if y entry < temp or temp is -1:
				now temp is y entry;
	decide on temp;

to decide what number is xmax:
	let temp be -1;
	repeat through table of map coordinates:
		if rm entry is mappable:
			if x entry > temp:
				now temp is x entry;
	decide on temp;

to decide what number is ymax:
	let temp be -1;
	repeat through table of map coordinates:
		if rm entry is mappable:
			if y entry > temp:
				now temp is y entry;
	decide on temp;

definition: a room (called rm) is mappable:
	if rm is a rm listed in table of map coordinates:
		if there is a view-rule entry:
			consider the view-rule entry;
			if the rule succeeded, decide yes;
			decide no;
	if rm is visited, decide yes;
	if rm is map-pinged, decide yes;
	decide no;

table of map coordinates
rm	x	y	l1	l2	indir	outdir	updir	downdir	view-rule
room	number	number	text	text	direction	direction	direction	direction	rule

In-Game Mapping ends here.

---- DOCUMENTATION ----