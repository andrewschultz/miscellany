Version 1/140928 of Trivial Niceties by Andrew Schultz begins here.

"Does nothing much yet"

volume stuff I've used multiple games

debug-state is a truth state that varies.

book screen effects [I always do something silly with the status line, or try a creative wait for any key, because that's fun]

include basic screen effects by Emily Short.

book thanks to Zarf

section track memory used

[used to see if a z8 was close to being a blorb]

Include (- Switches z; -) after "ICL Commands" in "Output.i6t".

section transcripting stub

[This makes a check for if the transcript is on. I use it to check if a person starts with * but transcripting is off. Thanks to Zarf!]

Include (-
[ CheckTranscriptStatus;
#ifdef TARGET_ZCODE;
return ((0-->8) & 1);
#ifnot;
return (gg_scriptstr ~= 0);
#endif;
];
-).

To decide whether currently transcripting: (- CheckTranscriptStatus() -)

book favorite abbreviations

to decide what region is mrlp:
	decide on map region of location of player.

book waiting stubs

waited-yet is a truth state that varies.

ignore-wait is a truth state that varies.

to wfak:
	if ignore-wait is false:
		if waited-yet is false:
			say "[i][bracket]NOTE: when the prompt does not appear, it means to push any key to continue[close bracket][r]";
			now waited-yet is true;
			wait for any key;
			say "[paragraph break]";
		else:
			wait for any key;

to say wfak-d:
	if debug-state is false:
		wfak;

book style abbreviations

to say r:
	say "[roman type]";

to say i:
	say "[italic type]";

to say b:
	say "[bold type]";

to say on-off of (t - a truth state):
	say "[if t is true]on[else]off[end if]";

book screenreading hooks

to say 2da: [this is so people with screen readers won't be annoyed by dashes]
	say "[unless screenread is true]--[end if]";

to say equal-banner of (nu - a number):
	if screenread is true:
		continue the action;
	let nu2 be nu;
	if nu2 > 80:
		now nu2 is 80;
	if nu2 < 0:
		continue the action;
	repeat with nu3 running from 1 to nu2:
		say "=";

to say srsp:
	if screenread is true:
		say " ";

screenread is a truth state that varies.

to ask-screenread:
	say "This game has some support for screen readers, such as eliminating excess punctuation. Are you using one?";
	if the player consents:
		now screenread is true;
	else:
		now screenread is false;
	say "Screen reading support will be [on-off of screenread] for this session. Toggle it with SCREEN.";

to say on-off of (ts - a truth state):
	say "[if ts is true]on[else]off[end if]"

chapter screening

screening is an action out of world.

understand the command "screen" as something new.

understand "screen" as screening.

carry out screening:
	if screenread is true:
		now screenread is false;
	else:
		now screenread is true;
	say "Screen reader support is now [on-off of screenread].";		
	the rule succeeds;

book footnotes on the fly

to ital-say (x - text):
	say "[italic type][bracket]NOTE: [x][close bracket][roman type][line break]";

volume debug printing

to d (myt - indexed text):
	if debug-state is true:
		say "DEBUG: [myt][line break]";

to dn (myt - indexed text):
	if debug-state is true:
		say "[myt]";

volume yes-no substitutes

[this lets the programmer skip over yes/no decides]

debug-auto-yes is a truth state that varies.

to decide whether the player yes-consents:
	(- YesOrNoExt(1) -).

to decide whether the player no-consents:
	(- YesOrNoExt(0) -).
	
to decide whether the player switch-consents:
	(- YesOrNoDebugForce( (+ debug-auto-yes +) ) -)

Include (-

[ YesOrNoDebugForce yn;
	if ( (+ debug-state +) == 1)
	{
	    return ( (+ debug-auto-yes +) );
	}
	return YesOrNo();
];

[ YesOrNoExt yn;
	if ( (+ debug-state +) == 1)
	{
	    return yn;
	}
	return YesOrNo();
];

-)

Trivial Niceties ends here.

---- DOCUMENTATION ----