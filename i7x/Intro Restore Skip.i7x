Version 1/190730 of Intro Restore Skip by Andrew Schultz begins here.

"A stub so that, at the game start, you can skip the introduction if you want to, or you have a game to restore. The usage is: abide anonymously by the check-skip-intro rule."

volume intro/restore/skip

include Trivial Niceties by Andrew Schultz.

this is the check-skip-intro rule:
	if debug-state is false:
		let got-good-key be false;
		say "If you've played [story title] before, you may wish to jump ahead a bit. ";
		while got-good-key is false:
			say "Would you like to see the full introduction (F or I), restore a previous game (R), or skip the introduction (S)?";
			let Q be the chosen letter;
			if Q is 70 or Q is 73 or Q is 102 or Q is 105, continue the action;
			if Q is 83 or Q is 115, the rule succeeds;
			if Q is 82 or Q is 114:
				say "Restoring...";
				try restoring the game;
			if got-good-key is false, say "[line break][if q is 82 or q is 114]Restore failed. Let's try again[else]I didn't recognize that letter[end if].";
	continue the action;

Intro Restore Skip ends here.

---- DOCUMENTATION ----
