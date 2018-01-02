Version 1/171230 of Trivial Niceties by Andrew Schultz begins here.

"This adds indexed text stubs to a glulx project. We avoid it for Z8 because indexed text can take a LOT of memory/space in the compiler."

include Trivial Niceties by Andrew Schultz.

volume debug printing

to d (myt - indexed text):
	if debug-state is true:
		say "DEBUG: [myt][line break]";

to dl (myt - indexed text): [this is for stuff you really want to delete]
	if debug-state is true:
		say "DEBUG: [myt][line break]";

to dn (myt - indexed text):
	if debug-state is true:
		say "[myt]";

Trivial Niceties ends here.

---- DOCUMENTATION ----