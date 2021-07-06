Version 1/140928 of Debug Levels and Checks by Andrew Schultz begins here.

"This goes beyond Trivial Niceties's debug-state flag. It allows for debug levels to filter out unimportant information and a quicker way to say 1., 2., etc. to track what code is touched."

volume debug levels

current-debug-level is a number that varies.

to dl-say (t - text) and (n - a number):
	if current-debug-level >= n:
		say "[t]";

chapter dla

dlaing is an action applying to one number.

understand the command "dla" as something new.

understand "dla[number]" as dlaing.

carry out dlaing:
	if the number understood < 0:
		say "You need a positive number." instead;
	else if the number understood is 0:
		say "Turning debug levels off.";
	else if the number understood is current-debug-level:
		say "Keeping debug level of [current-debug-level].";
	else:
		say "Moving debug level [if number understood > current-debug-level]up[else]down[end if] from [current-debug-level] to [the number understood].";
	now current-debug-level is the number understood;
	the rule succeeds;

Debug Levels and Checks ends here.
