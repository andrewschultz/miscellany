Version 1/140928 of Trivial Niceties Z-Only by Andrew Schultz begins here.

"This puts in stubs I've used often and probably will again. The non-Z-only in Trivial Niceties includes these and also has functions that takes up more memory e.g. indexed text."

volume stuff I've used multiple games

debug-state is a truth state that varies.

to say fill-in-here: say "!!!!" [This is something that should never be in a game's release. At times I want to be able to compile the game but still reliably note when something needs to be implemented. I track this with a script elsewhere.]

book screen effects [I always do something silly with the status line, or try a creative wait for any key, because that's fun]

include Basic Screen Effects by Emily Short.

to force-status: (- DrawStatusLine(); -); [ this is so you can change the status line at the start of the game ]

book thanks to Zarf and Climbingstars

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

section avoid line breaks in consider/follow

[thanks to Climbingstars and Zarf https://www.intfiction.org/forum/viewtopic.php?p=41700]

To process (RL - a rule): (- ProcessRulebook({RL}, 0, true); -)

To skip upcoming rulebook break: (- say__pc = say__pc | PARA_NORULEBOOKBREAKS; -). [this is when a weird line break pops up because Inform thinks it should after a rule, and you don't want it to. Often seen when writing a list of stuff after processing/considering/following rules and nothing gets printed out.]

book I figured this out! Yay!

[this is useful if we have a problem that occurs before we make a single move]

to force-rules: (- debug_Rules = 1; -)

to force-all-rules: (- debug_Rules = 2; -)

book waiting stubs

waited-yet is a truth state that varies.

ignore-wait is a truth state that varies.

to wfak:
	if ignore-wait is false:
		if waited-yet is false:
			say "[i][bracket]NOTE: when the prompt does not appear, it means you need to push any key to continue[close bracket][r]";
			now waited-yet is true;
			wait for any key;
			say "[paragraph break]";
		else:
			wait for any key;

any-key-yet is a truth state that varies.

to say wfak:
	if any-key-yet is false, say " (when text pauses like this, it means press any key to continue)";
	now any-key-yet is true;
	if debug-state is false, wfak;

book plural

to say plur of (n - a number): if n is not 1, say "s"

to say this-these of (nu - a number): say "th[if nu is 1]is[else]ese[end if]"

book basic math

to decide what number is abs of (n - a number):
	if n < 0, decide on 0 - n;
	decide on n;

book style abbreviations

to say r: say "[roman type]";

to say i: say "[italic type]";

to say b: say "[bold type]";

to say fw: say "[fixed letter spacing]"

to say vw: say "[variable letter spacing]"

to say on-off of (t - a truth state): say "[if t is true]on[else]off[end if]";

to say off-on of (t - a truth state): say "[if t is true]off[else]on[end if]";

book screenreading hooks

to say 2da: say "[unless screenread is true]--[end if]"; [this is so people with screen readers won't be annoyed by dashes]

to say equal-banner of (nu - a number):
	if screenread is true, continue the action;
	let nu2 be nu;
	if nu2 > 80, now nu2 is 80;
	if nu2 < 0, continue the action;
	repeat with nu3 running from 1 to nu2:
		say "=";

to say sp: if screenread is true, say " ";

to say srsp: say "[sp]"

screenread is a truth state that varies.

use-custom-screenread is a truth state that varies.

to ask-screenread:
	if use-custom-screenread is false, say "This game has some support for screen readers, such as eliminating excess punctuation. Are you using one?";
	if the player consents:
		now screenread is true;
	else:
		now screenread is false;
	say "Screen reading support will be [on-off of screenread] for this session. Toggle it with SCREEN or SCR.";

chapter screening

screening is an action out of world.

understand the command "screen" as something new.
understand the command "scr" as something new.

understand "screen" and "scr" as screening.

carry out screening:
	now screenread is whether or not screenread is false;
	say "Screen reader support is now [on-off of screenread].";
	the rule succeeds;

chapter banishing

banishing is an action applying to one visible thing.

understand the command "banish" as something new.

understand "banish [any thing]" as banishing.

carry out banishing:
	if noun is off-stage, say "But [the noun] is already off-stage!" instead;
	now noun is off-stage;
	say "Now [the noun] is off-stage.";
	the rule succeeds;

book footnotes on the fly

to ital-say (x - text): say "[italic type][bracket]NOTE: [x][close bracket][roman type][line break]"; [NOTE: if we find an error here, try ital-txt instead]

to score-now:
	increment the score;
	consider the notify score changes rule;

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

[ * scenery listing ]

scling is an action out of world.

understand the command "scl" as something new.

understand "scl" as scling.

carry out scling:
	say "List of scenery:[line break]";
	repeat with QQ running through visible scenery:
		say "--[QQ][line break]";
	the rule succeeds;

chapter bkling

[ * backdrop listing ]

bkling is an action out of world.

understand the command "bkl" as something new.

understand "bkl" as bkling.

carry out bkling:
	say "List of backdrops:[line break]";
	repeat with QQ running through visible backdrops:
		say "--[QQ][line break]";
	the rule succeeds;

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

chapter dtoging - not for release

[ * toggles debug state ]

dtoging is an action out of world.

understand the command "dtog/debug/db" as something new.

understand "dtog" as dtoging.
understand "debug" as dtoging.
understand "db" as dtoging.

carry out dtoging:
	now debug-state is whether or not debug-state is false;
	say "Debug-state is now [on-off of debug-state].";
	the rule succeeds;

chapter drop-player-at

to drop-player-at (myrm - a room):
	move player to myrm, without printing a room description;
	say "[b][myrm][r][paragraph break]"

chapter basic consents

[ "if the player direct-consents" is useful for when I am running a regex script and want to test full yes/no behavior, especially if I need to undo.
  "if the player switch-consents" is useful for when I want to say no automatically. ]

to decide whether the player direct-consents:
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

volume big-picture game state hacking - not for release

chapter auing

[* this lets the user switch how the debug version auto-responds to yes/no prompts *]

auing is an action out of world applying to one number.

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

chapter wining

[* this automatically wins the game so I can test post-game options *]

wining is an action applying to nothing.

understand the command "win" as something new.

understand "win" as wining.

carry out wining:
	end the story finally;
	the rule succeeds;

Trivial Niceties Z-Only ends here.

---- DOCUMENTATION ----