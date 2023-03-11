Version 1/200614 of Punctuation Stripper by Andrew Schultz begins here.

"I took the highest-priority bits from Emily Short's Punctuation Removal for this. When including this, I probably want to insert the punctuation-munge rule from here where appropriate in after reading the player's command."

volume I7 definition(s)

remove-commas is a truth state that varies. remove-commas is true.
remove-apostrophes is a truth state that varies. remove-apostrophes is true.
remove-dashes is a truth state that varies. remove-dashes is true.

volume I6 stuff

include (-

Global dashwarn = 0;
Global aposwarn = 0;
Global commawarn = 0;

[
	isComment;
	if ((buffer->WORDSIZE == '*') || (buffer->WORDSIZE == ';') || (buffer->WORDSIZE == '!'))
	{
		print "Comment noted. If you wanted this as a command, get rid of the starting character.^^";
		rtrue;
	}
	rfalse;
];

[
	ParsePunc   ix iy li found buffer_length;

	found = 0;

#ifdef TARGET_ZCODE;
	buffer_length = (buffer->1)+(WORDSIZE-1);
#endif;
#ifdef TARGET_GLULX;
	buffer_length = (buffer-->0)+(1-1);
#endif;

	if ( (+ remove-commas +) == true)
	{
		for (ix=0 : ix<buffer_length : ix++)
			if (buffer->(WORDSIZE+ix) == ',')
			{
				buffer->(WORDSIZE+ix) = ' ';
				found++;
			}
	}

	if ((found > 0) && (commawarn == 0))
	{
		commawarn = 1;
		print "NOTE: found a comma and replaced it with a space. You never need to use commas in commands. ", (string) Story, " will replace commas without nagging you in the future.^^" ;
	}

	found = 0;

	if ( (+ remove-dashes +) == true )
	{
		for (ix=0 : ix<buffer_length : ix++)
			if (buffer->(WORDSIZE+ix) == '-')
			{
				buffer->(WORDSIZE+ix) = ' ';
				found++;
			}
	}

	if ((found > 0) && (dashwarn == 0))
	{
		dashwarn = 1;
		print "NOTE: found a hyphen and replaced it with a space. You never need to use hyphens in commands. ", (string) Story, " will replace hyphens without nagging you in the future.^^" ;
	}

	found = 0;
	iy = 0;
	! print WORDSIZE;
	! print " = word size.^";

	if ( (+ remove-apostrophes +) == true )
	{
		for (ix=0 : ix<buffer_length : ix++)
		{
			! print buffer->(WORDSIZE+ix);
			! print "^";
			if (iy ~= ix)
			{
				buffer->(WORDSIZE+iy) = buffer->(WORDSIZE+ix);
			}
			if ((buffer->(WORDSIZE+ix) == 39) || (buffer->(WORDSIZE+ix) == 45))
			{
				found++;
			}
			else
			{
				iy++;
			}
		}
	}

	if (found > 0)
	{
		if (aposwarn == 0)
		{
			aposwarn = 1;
			style underline;
			print "[NOTE: found an apostrophe and removed it. You never need to use apostrophes in commands. ", (string) Story, " will eliminate apostrophes without nagging you in the future.]^^";
			style roman;
		}
#ifdef TARGET_ZCODE;
	buffer->1 = iy;
	buffer->(WORDSIZE+iy-1) = 0;
#endif;
#ifdef TARGET_GLULX;
	buffer-->0 = iy;
	buffer->(WORDSIZE+iy) = 0;
#endif;
		! print "New command: ";
	}
	! print iy, " of ", buffer_length, " kept.^";
	VM_Tokenise(buffer, parse);
	rtrue;
];

-)

to decide whether is-comment: (- isComment() -)

to parse-continue: (- ParsePunc(); -)

after reading a command (this is the punctuation-munge rule):
	if is-comment, reject the player's command;
	parse-continue;

volume sample code

Punctuation Stripper ends here.

---- DOCUMENTATION ----

We shouldn't have to do more than include Punctuation Stripper to get it to run. However, it can be modified if we don't want to eliminate some punctuation.

The main tweaks to the code are in this rule. If all booleans were switched, this extension would have no effect. The most likely one to switch is remove-commas, so you can use "PERSON, COMMAND" if wanted.

Note that commas and hyphens are replaced with spaces, but apostrophes are removed completely. This isn't a one-size-fits-all solution, but it seems the most likely to be what the player intended.

	when play begins:
		now remove-commas is false;
		now remove-dashes is false;
		now remove-apostrophes is false;

You also may wish to add this line in case rules conflict:

	the punctuation-munge rule is listed first in the after reading a command rule.
