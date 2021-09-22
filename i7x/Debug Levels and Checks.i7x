Version 1/140928 of Debug Levels and Checks by Andrew Schultz begins here.

"This goes beyond Trivial Niceties's debug-state flag. It allows for debug levels to filter out unimportant information and a quicker way to say 1., 2., etc. to track what code is touched."

[It is recommended to include this in a separate section we can toggle between RELEASE and NOT FOR RELEASE. We want it for testing, but we want to eliminate this code in the final release.
If we include this in NOT FOR RELEASE, all functions below will be caught.]

volume includes

include Trivial Niceties by Andrew Schultz.

volume debug levels

current-debug-level is a number that varies.

to dl-say (t - text) and (n - a number):
	if debug-state is false, continue the action;
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

volume debug checks

debug-count is a number that varies.

to dc-say (t - text):
	if debug-state is false, continue the action;
	increment debug-count;
	say "[debug-count]. [t][line break]";

to d1-say (t - text):
	if debug-state is false, continue the action;
	dcr;
	say "[debug-count]. [t][line break]";

to dcr:
	debug-count-reset;

to dc0:
	debug-count-reset;

to debug-count-reset:
	if debug-state is false, continue the action;
	now debug-count is 0;


Debug Levels and Checks ends here.
