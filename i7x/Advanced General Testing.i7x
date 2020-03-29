Version 1/140928 of Advanced General Testing by Andrew Schultz begins here.

"This puts in test stubs I've used more frequently as time goes on."

include Trivial Niceties by Andrew Schultz

chapter unxing

a thing can be examined or unexamined. a thing is usually unexamined.

unxing is an action applying to one visible thing.

understand the command "unx" as something new.

understand "unx [any visible thing]" as unxing.

carry out unxing:
	if noun is unexamined:
		say "NOTE: [the noun] was already unexamined.";
	else:
		say "Unexamining [the noun].";
	now noun is unexamined;
	the rule succeeds.

chapter unving

unving is an action applying to one visible thing.

understand the command "unv" as something new.

understand "unv [any room]" as unving.

carry out unxing:
	if noun is unvisited:
		say "NOTE: [the noun] was already unvisited.";
	else:
		say "Unvisiting [the noun].";
	now noun is unvisited;
	the rule succeeds.


chapter dfling

dfling is an action applying to one number.

understand the command "dfl" as something new.

understand "dfl [number]" as dfling.

carry out dfling:
	let Q be number understood;
	if Q > 31:
		say "You need a flag between 1 and 31. You can use negative flags to flag a bunch of numbers." instead;
	if Q > 0:
		choose row Q in the table of debug flags;
		now dfl-state entry is whether or not dfl-state entry is false;
		say "Set flag [Q] [dfl-text entry] to [dfl-state entry].";
		the rule succeeds;
	now Q is 0 - Q;
	let myrow be 0;
	while myrow <= 30:
		repeat through table of debug flags:
			if the remainder after dividing Q by 2 is 1:
				now dfl-state entry is true;
				say "Set [myrow] [dfl-text entry].";
			else:
				now dfl-state entry is false;
			now Q is Q / 2;
	the rule succeeds.

table of debug flags
dfl-text	dfl-state
"test 1"	False
"test 2"	False
"test 3"	False
"test 4"	False
"test 5"	False
"test 6"	False
"test 7"	False
"test 8"	False
"test 9"	False
"test 10"	False
"test 11"	False
"test 12"	False
"test 13"	False
"test 14"	False
"test 15"	False
"test 16"	False
"test 17"	False
"test 18"	False
"test 19"	False
"test 20"	False
"test 21"	False
"test 22"	False
"test 23"	False
"test 24"	False
"test 25"	False
"test 26"	False
"test 27"	False
"test 28"	False
"test 29"	False
"test 30"	False

chapter dlving

debug-level is a number that varies.

dlving is an action applying to one number.

understand the command "dlv" as something new.

understand "dlv [number]" as dlving.

carry out dlving:
	if number understood < 0 or number understood > 10:
		say "Debug level must be between 0 and 10 inclusive." instead;
	now debug-level is the number understood;
	say "Debug level at [the number understood]. Higher numbers give deeper debugging.";
	the rule succeeds.

Advanced General Testing ends here.

---- DOCUMENTATION ----