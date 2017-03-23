; this is potentially a morally bad script
;
; it allows you to pretend like you did something to keep a daily codecademy.com streak going
; even if you didn't really
;
; the sleep times are so that the page loads
;
; it then opens your profile page
;
; you may need to change the link

Local $delay = 5000;

Run('"c:\program files (x86)\mozilla firefox\firefox" "https://www.codecademy.com/courses/introduction-to-python-6WeG3/0/1"');

if $CmdLine[0] > 0 Then
    $delay = $CmdLine[1] * 1000
Endif

WinWaitActive("Python Syntax");

sleep($delay);
send("A{BS}^{ENTER}");
sleep(2000);
send("^w");

ShellExecute("cac.pl")
