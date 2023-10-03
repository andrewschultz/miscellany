Version 1/181008 of Old School Verb Carnage by Andrew Schultz begins here.

"This gets rid of a lot of verbs I don't want or need to implement but alerts the player they are deprecated."

[include Old School Verb Total Carnage by Andrew Schultz.]

understand the command "attach" as "slice".
understand the command "buy" as "slice".
understand the command "chop" as "slice".
understand the command "crack" as "slice".
understand the command "embrace" as "slice".
understand the command "fight" as "slice".
understand the command "hop" as "slice".
understand the command "hug" as "slice".
understand the command "jump" as "slice".
understand the command "kill" as "slice".
understand the command "kiss" as "slice".
understand the command "light" as "slice".
understand the command "murder" as "slice".
understand the command "polish" as "slice".
understand the command "prune" as "slice".
understand the command "punch" as "slice".
understand the command "purchase" as "slice".
understand the command "scrub" as "slice".
understand the command "shine" as "slice".
understand the command "sip" as "slice".
understand the command "skip" as "slice".
understand the command "sorry" as "slice".
understand the command "swallow" as "slice".
understand the command "sweep" as "slice".
understand the command "thump" as "slice".
understand the command "tie" as "slice".
understand the command "throw" as "slice".
understand the command "torture" as "slice".
understand the command "touch" as "slice".
understand the command "wipe" as "slice".
understand the command "wreck" as "slice".

[the choice of SLICE is arbitrary. But the point is just to have something to temm the player specifically, "we don't want to overwhelm you with old school verbs"]
understand "slice" as oldschooling.
understand "slice [text]" as os2ing.

oldschooling is an action out of world.

os2ing is an action applying to one topic.

carry out os2ing: try oldschooling instead;

[a "check oldschooling" rule is probably the way to go here.]
carry out oldschooling (this is the generic old school verb rule):
	say "An old school verb like [word number 1 in the player's command] isn't strictly necessary in this game. See [b]V/VERB/VERBS[r] for what is used/useful." instead;

Old School Verb Carnage ends here.

---- DOCUMENTATION ----