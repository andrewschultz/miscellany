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

section pronoun setting

[This allows us to refer to a plural noun as it/them. Thanks to Climbingstars!]

To set the/-- pronoun it to (O - an object): (- LanguagePronouns-->3 = {O}; -).
To set the/-- pronoun him to (O - an object): (- LanguagePronouns-->6 = {O}; -).
To set the/-- pronoun her to (O - an object): (- LanguagePronouns-->9 = {O}; -).
To set the/-- pronoun them to (O - an object): (- LanguagePronouns-->12 = {O}; -).

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

book basic math

to decide what number is abs of (n - a number):
	if n < 0, decide on 0 - n;
	decide on n;

book style abbreviations

to say r:
	say "[roman type]";

to say i:
	say "[italic type]";

to say b:
	say "[bold type]";

to say fw:
	say "[fixed letter spacing]"

to say vw:
	say "[variable letter spacing]"

to say on-off of (t - a truth state):
	say "[if t is true]on[else]off[end if]";

to say off-on of (t - a truth state):
	say "[if t is true]off[else]on[end if]";

book screenreading hooks

to say 2da: [this is so people with screen readers won't be annoyed by dashes]
	say "[unless screenread is true]--[end if]";

to say equal-banner of (nu - a number):
	if screenread is true, continue the action;
	let nu2 be nu;
	if nu2 > 80:
		now nu2 is 80;
	if nu2 < 0, continue the action;
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

chapter banishing

banishing is an action applying to one visible thing.

understand the command "banish" as something new.

understand "banish [any thing]" as banishing.

carry out banishing:
	now noun is off-stage;
	say "Now [the noun] is off-stage.";
	the rule succeeds;

book footnotes on the fly

to ital-say (x - text):
	say "[italic type][bracket]NOTE: [x][close bracket][roman type][line break]";

to score-now:
	increment the score;
	consider the notify score changes rule;

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

volume yes-no substitutes

[this lets the programmer skip over yes/no decides]

chapter complex consents

debug-auto-yes is a truth state that varies.

yn-auto is a number that varies.

to decide whether the player dir-consents:
	if debug-state is true:
		if yn-auto is 1, decide yes;
		if yn-auto is -1, decide no;
	if the player consents, decide yes;
	decide no;

chapter scling

scling is an action out of world.

understand the command "scl" as something new.

understand "scl" as scling.

carry out scling:
	say "List of scenery:[line break]";
	repeat with QQ running through visible scenery:
		say "--[QQ][line break]";
	the rule succeeds;

chapter bkling

bkling is an action out of world.

understand the command "bkl" as something new.

understand "bkl" as bkling.

carry out bkling:
	say "List of scenery:[line break]";
	repeat with QQ running through visible backdrops:
		say "--[QQ][line break]";
	the rule succeeds;

chapter auing

auing is an action applying to one number.

understand the command "au" as something new.

understand "au [number]" as auing.

carry out auing:
	if number understood > 1 or number understood < -1, say "1 = auto-yes 0 = auto-off -1 = auto-no." instead;
	if number understood is yn-auto, say "It's already set to [auto-set]." instead;
	say "Y/N responses changed from [auto-set] to ";
	now yn-auto is number understood;
	say "[auto-set].";
	the rule succeeds;

to say auto-set:
	say "[if yn-auto is 1]auto-yes[else if yn-auto is -1]auto-no[else]no auto[end if]";

chapter direction stubs

definition: a direction (called d) is diagonal:
	if d is northwest or d is northeast or d is southwest or d is southeast, decide yes;
	decide no;

definition: a direction (called d) is cardinal:
	if d is west or d is east or d is south or d is north, decide yes;
	decide no;

definition: a direction (called thedir) is planar:
	if thedir is cardinal or thedir is diagonal, decide yes;
	decide no;

chapter basic consents

to decide whether the player test-consents:
	if debug-state is true:
		say "[line break]> ";
	if the player consents, decide yes;
	decide no;

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