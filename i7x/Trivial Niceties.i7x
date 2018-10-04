Version 1/171230 of Trivial Niceties by Andrew Schultz begins here.

"This adds indexed text stubs to a glulx project. We avoid it for Z8 because indexed text can take a LOT of memory/space in the compiler."

include Trivial Niceties Z-Only by Andrew Schultz.

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

debug-count is a number that varies;

to d1:
	now debug-count is 1;
	say "[debug-count].";

to dn:
	increment debug-count;
	say "[debug-count]";

volume intro/restore/skip

read-intro is a truth state that varies.

to intro-restore-skip:
	now read-intro is true;
	if debug-state is false:
		let got-good-key be false;
		while got-good-key is false:
			let Q be the chosen letter;
			if Q is 70 or Q is 73 or Q is 102 or Q is 105:
				now read-intro is true;
				now got-good-key is true;
			else if Q is 82 or Q is 114:
				say "Restoring...";
				try restoring the game;
			else if Q is 83 or Q is 115:
				now read-intro is false;
				now got-good-key is true;
			if got-good-key is false, say "[line break][if q is 82 or q is 114]Restore failed. Let's try again[else]I didn't recognize that[end if]. Would you like to see the full introduction (F or I), restore a previous game (R), or skip the introduction (S)?";

Trivial Niceties ends here.

---- DOCUMENTATION ----