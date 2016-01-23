Version 1/140928 of Object-Based Hinting by Andrew Schultz begins here.

volume includes

include Trivial Niceties by Andrew Schultz.

include Bypass Disambiguation by Climbing Stars.

rule for asking which do you mean (this is the bypass disambiguation rule):
	if current action is objhinting:
		say "Sorry, [one of]but you may not have been specific enough with the hint-asking request. I'm going to err on the side of caution instead of possibly disambiguating something you haven't seen. This is a possible coding bug (and I'd like to know,) but it may also prevent spoilers. For best results, you should try to visit the location of whatever you want hinted or be more detailed in your request[or]this request seems too vague. If it's a bug, let me know[stopping].";
		bypass disambiguation;
		the rule succeeds;
	continue the action;

after asking which do you mean (this is the bypass disambiguation 2 rule):
	if current action is objhinting:
		bypass disambiguation;
		the rule succeeds;
	continue the action;

volume basic stuff

a thing can be useless or hintworthy. a thing is usually hintworthy.

the macguffin is a privately-named thing. description of macguffin is "Only for testing purposes."

table of hintobjs
myobj	altobj	mytxt	find-rule	hint-if-vis
macguffin	macguffin	"You don't really need to know much about the macguffin."	never-true rule	false

to say i:
	say "[italic type]";

to say r:
	say "[roman type]";

to say plus:
	say "[run paragraph on][one of] (+) [i][bracket]Note: the plus sign means you can HINT again for something more spoilery. (-) means the end of a list of hints.[no line break][r][close bracket][line break][or] (+)[line break][stopping]";

to say minus:
	say "[one of] (-) [bracket][i]A minus sign means you've reached the end of a hint loop. You can cycle through them again, though.[no line break][r][close bracket][or] (-)[stopping][line break]";

this is the never-true rule:
	the rule fails;

this is the always-true rule:
	the rule succeeds;

section can't quite NFR

[this is for release because the character may wish to activate it after an out-of-world command.]

every-move-hint is a truth state that varies. [this is placed here for debugging purposes]

every turn when every-move-hint is true (this is the show debug hints rule):
	say "====Every-move hint[line break]";
	try hinting;

chapter hinting

hinting is an action out of world.

understand the command "hint/hints/help" as something new.

understand "hint" and "hints" and "help" as hinting.

carry out hinting:
	repeat through table of hintobjs:
		if there is a find-rule entry:
			consider the find-rule entry;
			if the rule succeeded:
				say "[mytxt entry]";
				the rule succeeds;
			else:
				do nothing; [can put in a debug command here if you want]
		if there is a myobj entry and there is a hint-if-vis entry and hint-if-vis entry is true:
			if myobj entry is visible:
				try objhinting myobj entry;
				the rule succeeds;
	say "I'm not able to give any hints right now. Sorry about this. Try hinting specific items instead.";
	the rule succeeds;

chapter hintalling - not for release

hintalling is an action out of world.

understand the command "hintall" as something new.

understand "hintall" as hintalling.

carry out hintalling:
	let idx be 0;
	repeat with QQ running through all hintworthy things:
		if QQ is not a myobj listed in table of hintobjs:
			increment idx;
			say "[idx]. Need hint object for [QQ].";
	if idx is 0:
		say "Everything that can be hinted, is.";
	the rule succeeds;

volume emhing - not for release

emhing is an action out of world.

understand the command "emh" as something new.

understand "emh" as emhing.

carry out emhing:
	if every-move-hint is true:
		say "Every move hinting off.";
	else:
		say "Every move hinting on.";
		now every-move-hint is true;
	the rule succeeds;

volume objhinting

understand the command "hint [any thing]" as something new.

understand "hint [any thing]" as objhinting.

objhinting is an action applying to one visible thing.

carry out objhinting:
	repeat through table of hintobjs:
		if there is a myobj entry and myobj entry is noun:
			if there is a mytxt entry:
				say "[mytxt entry]";
			else:
				say "There should be a hint for this item, but there isn't.";
			the rule succeeds;
		if there is an altobj entry and noun is altobj entry:
			try objhinting the altobj entry instead;
	say "There's no hinting for that. There probably should be." instead;

Object-Based Hinting ends here.

---- DOCUMENTATION ----