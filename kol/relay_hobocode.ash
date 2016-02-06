boolean hasBit(int x, int y)
{
  int z = x / y;
  if (2*(z/2) != z) { return true; } else { return false; }
}

void main()
{
  print("Running hobo code relay.");
  string x = visit_url("questlog.php?which=5");
  boolean showHoboRelay = (get_property("showHoboRelay") == true);
  int codesfound = 0;
  //matcher q = create_matcher(".*<ul><li>", x);
  //matcher q = create_matcher(".*<ul>", x);
  matcher q = create_matcher(".*<ul><li>", x);
  if (!q.find()) { print ("No list open tag found."); return; }
  WRITE("<html><body><center><font size=+2>HOBO CODE TRACKER</font></center>");
  WRITELN("FOUND:<ol>");
  string y2 = x;
  x = replace_all(q, "");
  
  q=create_matcher("<\/li><\/ul>.*", x);
  x = replace_all(q, "");
  
  string [int] y = split_string(x, "</li><li>");
  
  string [int] [string] [int] codemap;
  
  file_to_map("hobo_code_file.txt", codemap);

  int [int] found;

  foreach z in y
  {
    foreach codeNum, hobLoc, codeType, foundYet in codemap
	{
	  if (hobLoc == y[z])
	  {
      WRITELN ("<li>" + " " + y[z] + "</li>");
	  codesfound = codesfound + 1; found[codeNum] = 1;
	  }
	}
  }
  WRITELN("</ol>");

  if (codesfound == count(codemap)) { WRITELN("You have all " + count(codemap) + " codes!"); }
  if ((codesfound != count(codemap)) || showHoboRelay)
  {
    if (codesfound != count(codemap)) { WRITELN("HAVE " + codesfound + " of " + count(codemap) + ". NOT FOUND:"); } else { WRITELN("<br>Here's full info on them (set showHoboRelay=false in the CLI to get rid of this) :"); }
	WRITELN("<ol>");
    foreach codeNum, hobLoc, codeType, foundYet in codemap
	{
	  if ((found[codeNum] == 0) || (showHoboRelay))
	  {
	    WRITE("<li>" + hobLoc);
		if (found[codeNum] == 0) { WRITE(" not found yet."); }
		else { WRITE (" details:"); }
		if (codeType == 0) { WRITE(" <font color=grey>(no particular difficulties to get)</font>"); }
		else
		{
		  if (hasBit(codeType, 1)) { WRITE(" <font color=orange>(only available durning NS quest)</font>"); }
		  if (hasBit(codeType, 2)) { WRITE(" <font color=purple>(moon sign dependent)</font>"); }
		  if (hasBit(codeType, 4)) { WRITE(" <font color=808000>(only available during non-NS quest)</font>"); }
		  if (hasBit(codeType, 8)) { WRITE(" <font color=blue>(no fun turn burn)</font>"); }
		  if (hasBit(codeType, 16)) { WRITE(" <font color=green>(potential bounty)</font>"); }
		  if (hasBit(codeType, 32)) { WRITE(" <font color=red>(this one sucks especially for speed runners. Casual + goofballs/knob steroids may be necessary.)</font>"); }
		}
		WRITELN("</li>");
	  }
	}
	WRITELN("</ol>");
  }
  else { WRITELN("<p>Set showHoboRelay=true in the CLI to see guidelines to get codes."); }
  WRITELN("</body></html>");
}