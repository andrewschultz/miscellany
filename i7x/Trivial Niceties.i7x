Version 1/140928 of Trivial Niceties by Andrew Schultz begins here.

"This puts in stubs I've used often and probably will again. The non-Z-only in Trivial Niceties includes these and also has functions that takes up more memory e.g. indexed text."

volume includes

include Trivial Text Shortcuts by Andrew Schultz.

volume stuff I've used multiple games

use OMIT_UNUSED_ROUTINES of 1. [ this may not be strictly necessary with the 6.40 compiler in place, but just in case I need to revert, I want it here. It means up to 0x5000 memory saved if I'm trying to compress a game into Z5. ]

debug-state is a truth state that varies.

in-beta is a truth state that varies.

to say this-game-noi: (- print (string) Story; -)

to say this-game: say "[i][this-game-noi][r]"

to say fill-in-here: say "!!!!" [This is something that should never be in a game's release. At times I want to be able to compile the game but still reliably note when something needs to be implemented. I track this with a script elsewhere.]

definition: a thing (called qvc) is qv:
	if qvc is enclosed by location of player, yes;
	no;

To decide what action name is the action-to-be: (- action_to_be -). [ this is "if action-to-be is the gotoing action: / not "if action-to-be is gotoing" used a lot for parser errors ]

section debug state - not for release

when play begins (this is the TN debug true rule):
	say "The TN debug true rule sets debug-state to true. It does not appear in release mode. Disable with 'the TN debug true rule does not appear in any rulebook.'";
	now debug-state is true;

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

to set-all (O - an object):
	set the pronoun it to O;
	set the pronoun him to O;
	set the pronoun her to O;
	set the pronoun them to O;

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

To abide-nlb (RL - a rule): (- if (ProcessRulebook({RL}, 0, true)) rtrue; -) - in to only.

To skip upcoming rulebook break: (- say__pc = say__pc | PARA_NORULEBOOKBREAKS; -). [this is when a weird line break pops up because Inform thinks it should after a rule, and you don't want it to. Often seen when writing a list of stuff after processing/considering/following rules and nothing gets printed out.]

book I figured this out! Yay!

[this is useful if we have a problem that occurs before we make a single move]

to force-rules: (- debug_Rules = 1; -)

to force-all-rules: (- debug_Rules = 2; -)

[to decide which number is game-state:
	(- deadflag -) ;

to decide whether game-over:
	if game-state is 0, no;
	yes;

to decide whether game-on:
	if game-state is 0, yes;
	no;
]

to decide whether game-on:
	(- GameOn() -);

to decide whether game-over:
	(- GameOn() == false -);

Include (-

[ GameOn ;
	return (deadflag == 0);
];

-)

book waiting stubs

waited-yet is a truth state that varies.

ignore-wait is a truth state that varies.

to wfak:
	if debug-state is true, continue the action;
	if ignore-wait is false:
		if any-key-yet is false:
			say "[i][bracket][b]NOTE[r][i]: when the prompt does not appear, it means you need to push any key to continue[close bracket][r]";
			now any-key-yet is true;
			wait for any key;
			say "[paragraph break]";
		else:
			wait for any key;

any-key-yet is a truth state that varies.

to say wfak:
	if any-key-yet is false, say " [i](when text pauses like this, it means press any key to continue)[r]";
	if debug-state is false:
		wfak;
		if any-key-yet is false:
			say "[paragraph break]";
	now any-key-yet is true;

book plural

to say plur of (n - a number): if n is not 1, say "s"

to say plurnos of (n - a number): if n is 1, say "s"

to say this-these of (nu - a number): say "th[if nu is 1]is[else]ese[end if]"

book basic math-ish stuff

to decide what number is abs of (n - a number):
	if n < 0, decide on 0 - n;
	decide on n;

[boolval of x + boolval of y simplifies "to decide what number is quests-solved"] [binval or binary also ... put this in so I can search easily if I forget] [thanks to Zed Lopez for the simplification]

to decide what number is boolval of (ts - a truth state): (- {ts} -).

book style abbreviations

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
	if use-custom-screenread is false, say "[line break]This game has some support for screen readers, such as eliminating excess punctuation. Are you using one?";
	if the player consents:
		now screenread is true;
	else:
		now screenread is false;
	say "[line break]Screen reading support will be [on-off of screenread] for this session. Toggle it with SCREEN or SCR.";

chapter screening

screening is an action out of world.

understand the command "screen" as something new.
understand the command "scr" as something new.

understand "screen" and "scr" as screening.

carry out screening:
	now screenread is whether or not screenread is false;
	say "Screen reader support is now [on-off of screenread].";
	the rule succeeds;

section scying - not for release

scying is an action out of world.

understand the command "scy" as something new.

understand "scy" as scying.

carry out scying:
	say "Screen reader support is forced on.";
	now screenread is true;
	the rule succeeds;

section scning - not for release

scning is an action out of world.

understand the command "scn" as something new.

understand "scn" as scning.

carry out scning:
	say "Screen reader support is forced off.";
	now screenread is false;
	the rule succeeds;

chapter banishing - not for release

banishing is an action applying to one visible thing.

understand the command "banish" as something new.

understand "banish [any thing]" as banishing.

carry out banishing:
	if noun is off-stage, say "But [the noun] is already off-stage!" instead;
	now noun is off-stage;
	say "Now [the noun] is off-stage.";
	the rule succeeds;

book footnotes on the fly

to ital-say (x - indexed text):
	ital-say-nob x;
	say "[line break]"; [NOTE: if we find an error here, try ital-txt instead]

to ital-say-nob (x - indexed text): say "[i][bracket]NOTE: [x][close bracket][r]"; [NOTE: if we find an error here, try ital-txt instead]

to ital-say-lb (x - indexed text):
	say "[line break]";
	ital-say x;

to score-now:
	increment the score;
	consider the notify score changes rule;

volume yes-no substitutes

[this lets the programmer skip over yes/no decides]

chapter complex consents

yn-auto is a number that varies.

to decide whether the player dir-consents:
	if debug-state is true:
		say "in debug, yn-auto = [yn-auto].";
		if yn-auto is 2, decide yes;
		if yn-auto is 0, decide no;
	if the player consents:
		decide yes;
	decide no;

section debug - not for release

yn-auto is 1. [if need be we can put a "when play begins" rule at the start, but we shouldn't need to.]

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

definition: a direction (called thedir) is vertical:
	if thedir is up or thedir is down, yes;
	no;

chapter debug toggling - not for release

[ * toggles debug state ]

to debug-to (ts - a truth state):
	say "Debug is [if ts is debug-state]already[else]now[end if]";
	now debug-state is ts;
	say "[on-off of debug-state].";

section off

doffing is an action out of world.

understand the command "doff" as something new.

understand "doff" as doffing.

carry out doffing:
	debug-to false;

section on

doning is an action out of world.

understand the command "don" as something new.

understand "don" as doffing.

carry out doning:
	debug-to true;

chapter drop-player-at

to drop-player-at (myrm - a room):
	move player to myrm, without printing a room description;
	say "[b][myrm][r][paragraph break]"

chapter basic consents

[ "if the player regex-prompt-consents" is useful for when I am running a regex script and want to test full yes/no behavior, especially if I need to undo.
  "if the player switch-consents" is useful for when I want to say no automatically. ]
[ this is superseded by dir-consents for the most part, as we often just want to set "yes" automatically to run through test cases. ]

to decide whether the player regex-prompt-consents: [used to be (mis)named "direct-consents"]
	if debug-state is true:
		say "[line break]FOR TESTING: WE NEED A Y OR N.[line break]> ";
	if the player consents, decide yes;
	decide no;

to decide whether the player yes-consents:
	(- YesOrNoExt(1) -).

to decide whether the player no-consents:
	(- YesOrNoExt(0) -).

to decide whether the player switch-consents:
	(- YesOrNoDebugForce( (+ yn-auto +) ) -)

Include (-

[ YesOrNoDebugForce yn;
	if ( (+ yn-auto +) == 2 ) return true;
	if ( (+ yn-auto +) == 0 ) return false;
	return YesOrNo();
];

[ YesOrNoExt yn;
	#ifdef DEBUG;
	return yn;
	#ifnot;
	return YesOrNo();
	#endif;
];

-)

volume big-picture game state hacking - not for release

chapter auing

[* this lets the user switch how the debug version auto-responds to yes/no prompts *]

[ note that it is 2, 1, 0 instead of 1, 0, -1 because some parsers strip hyphens ]

auing is an action out of world applying to one number.

understand the command "au" as something new.

understand "au [number]" as auing.

carry out auing:
	if number understood > 2 or number understood < -1, say "2 = auto-yes 1 = auto-off 0 = auto-no." instead;
	let temp be number understood;
	if temp is yn-auto, say "It's already set to [auto-set]." instead;
	say "Y/N responses changed from [auto-set] to ";
	now yn-auto is temp;
	say "[auto-set].";
	the rule succeeds;

to say auto-set:
	say "[if yn-auto is 2]auto-yes[else if yn-auto is 0]auto-no[else]no auto[end if]";

chapter wining

[* this automatically wins the game so I can test post-game options *]

wining is an action applying to nothing.

understand the command "win" as something new.

understand "win" as wining.

carry out wining:
	end the story finally;
	the rule succeeds;

volume forcegoing (for Glulx only)

chapter fging

fging is an action applying to one visible thing.

understand the command "fg" as something new.

understand "fg [direction]" as fging.

carry out fging:
	if noun is not a direction, say "We need a direction.";
	if the room noun of location of player is nowhere, say "That doesn't lead anywhere.";
	move player to the room noun of location of player;
	the rule succeeds.

volume debug printing

chapter dt (debug text, from i6)

Include (-
[ InDebug;
#ifdef DEBUG;
return true;
#ifnot;
return false;
#endif;
];
-).

to decide whether in-debug: (- InDebug() -)

to dt (t - text): if in-debug, say "[t]";

chapter Glulx d/dl/dn (for Glulx only)

to d (myt - indexed text):
	if debug-state is true:
		say "DEBUG: [myt][line break]";

to dl (myt - indexed text): [this is for stuff you really want to delete]
	if debug-state is true:
		say "DEBUG: [myt][line break]";

to dn (myt - indexed text):
	if debug-state is true:
		say "[myt]";

chapter Z-Machine d/dl/dn (for Z-Machine only)

to d (myt - text):
	if debug-state is true:
		say "DEBUG: [myt][line break]";

to dl (myt - text): [this is for stuff you really want to delete]
	if debug-state is true:
		say "DEBUG: [myt][line break]";

to dn (myt - text):
	if debug-state is true:
		say "[myt]";

chapter ital-txt

to ital-txt (x - indexed text): say "[italic type][bracket]NOTE: [x][close bracket][roman type][line break]".

volume trivial rules and cases

to decide whether always-no: decide no;
to decide whether always-yes: decide yes;

this is the trivially false rule: the rule fails;
this is the trivially true rule: the rule succeeds;
this is the trivially ignorable rule: continue the action;

Trivial Niceties ends here.

---- DOCUMENTATION ----