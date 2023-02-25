Version 1/200614 of Punctuation Stripper by Andrew Schultz begins here.

volume I6 stuff

"I took the highest-priority bits from Emily Short's Punctuation Removal for this. When including this, I probably want to insert the punctuation-munge rule from here where appropriate in after reading the player's command."

include (-

Global dashwarn = 0;
Global aposwarn = 0;

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

	for (ix=0 : ix<buffer_length : ix++)
		if (buffer->(WORDSIZE+ix) == '-')
		{
			buffer->(WORDSIZE+ix) = ' ';
			found++;
		}
	if ((found > 0) && (dashwarn == 0))
	{
		dashwarn = 1;
		print "NOTE: found a hyphen and replaced it with a space. You never need to use hyphens in commands. ", (string) Story, " will replace hyphens without nagging you in the future.^" ;
	}
	found = 0;
	iy = 0;
	! print WORDSIZE;
	! print " = word size.^";
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
	if (found > 0)
	{
		if (aposwarn == 0)
		{
			aposwarn = 1;
			style underline;
			print "[NOTE: ";
			print "found an apostrophe and removed it. You never need to use apostrophes in commands. ", (string) Story, " will eliminate apostrophes without nagging you in the future.]^";
			print "^";
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

this is the punctuation-munge rule:
	if is-comment, reject the player's command;
	parse-continue;

volume sample code

[after reading a command: abide by the punctuation-munge rule;]

Punctuation Stripper ends here.

---- DOCUMENTATION ----