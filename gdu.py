# gdu.py: google drive utilities script
#
# main tasks:
# creates a blank Google Drive daily document, formatted with title and "IMPORTANT" section
# also opens latest drive document created
#

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from collections import defaultdict
import os
import re
import pendulum
import sys
import mytools as mt
import time

cred_file = "mycreds.txt"
bail_if_created = False

create_new = False
show_time = True
look_for_last = False
look_for_last_mult = False
look_for_last_num = 1
back_range = (0, 0)
last_back = 1
max_back = 9

x = pendulum.today()
dest_title = "Transcription notes " + x.format("M/D/YYYY")
folder_id = "" # '0BxbuUXtrs7adSFFYMG0zS3VZNFE'
source_id = "1mkbVFs_911fx4qA0NYm1PL4ignwEn6-I4yoJG2oJsTI"

auto_credentials = True

if len(sys.argv) == 1:
    print("No parameters. GDU.PY now requires a parameter to run.")
    print("The most popular are -c to create a new document or -l to open the last created daily document.")
    print("Or you can combine the two to create a document--unless it's there, then open today's document.")
    sys.exit()

def usage():
    print("Not many commands to use.")
    print("-c = just create new, -cl= create, but if there, open last, -l/o/ol/lo = open last (main single usage paramaters)")
    print("-nl/-no/-ln/-on = don't look for most recently created file (only with other parameters)")
    print("-st/-ts = show time taken, -nt/-tn = no time taken")
    print("-a3 = back 1, 2, 3, -b3 = back 3, 2-5=back 2, 3, 4, 5")
    print()
    print("dft.py downloads finished transcripts from Google Drive")
    print("keso.py sorts the files by idea type")
    print()
    print("Default usage = create today's file and open the latest if it's already there.")
    exit()

def open_in_browser(x, file_desc = "google doc"):
    my_url = "https://docs.google.com/document/d/{0}/edit".format(x)
    print("Opening {0} in browser: {1}".format(file_desc, my_url))
    os.system("start {0}".format(my_url))

def get_drive_handle():
    gauth = GoogleAuth()
    if auto_credentials:
        gauth.LoadCredentialsFile(cred_file)
        if gauth.credentials is None:
            # Authenticate if they're not there
            gauth.LocalWebserverAuth()
        elif gauth.access_token_expired:
            # Refresh them if expired
            gauth.Refresh()
        else:
            # Initialize the saved creds
            gauth.Authorize()
        # Save the current credentials to a file
        gauth.SaveCredentialsFile(cred_file)
        gauth.LocalWebserverAuth()
        drive = GoogleDrive(gauth)
    return drive

def copy_file(service, source_id, dest_title):
    copied_file = {'title': dest_title}
    f = service.files().copy(fileId=source_id, body=copied_file).execute()
    return f['id']
                            
def create_if_not_there(lister, drive):
    for item in lister:
        if item['title'] == dest_title:
            print("We already have a file named {}. {}.".format(dest_title, "Bailing" if bail_if_created else "Opening latest"))
            if bail_if_created: exit()
            return False

    dest_id = copy_file(drive.auth.service, source_id, dest_title)
    
    dest = drive.CreateFile({'id': dest_id})
    dest.FetchMetadata('title')
    
    print(dest['title'], "created")
    return True

def to_date(doc_title): # for "Transcript dated 1/11/20"
    ary0 = doc_title.split(" ")
    ary1 = [int(x) for x in ary0[-1].split("/")]
    if ary1[-1] < 100:
        ary1[-1] += 2000
    ret_val = pendulum.datetime(ary1[-1], ary1[0], ary1[1])
    return ret_val

def open_latest_transcript(lister, drive):
    months = defaultdict(int)
    days = defaultdict(int)
    years = defaultdict(int)
    title_of = defaultdict(str)
    max_month = 0
    for item in lister:
        #print(item)
        full_title = item['title']
        if not re.search(r'[0-9]+(\/[0-9]+){1,2}$', full_title):
            continue
        if full_title.lower().startswith("clan store"): continue
        if full_title.lower().startswith("roster"): continue
        temp_title = re.sub(".* ", "", full_title)
        mdy = temp_title.split("/")
        if len(mdy) > 3:
            print("Skipping", mdy, "which has too many slashes:", temp_title)
            continue
        temp_id = item['id']
        try:
            mdy2 = [int(x) for x in mdy]
        except:
            print(temp_title, "is not of the numerical form MM/DD/(YYYY)")
            continue
        # print(temp_id)
        months[temp_id] = mdy2[0]
        days[temp_id] = mdy2[1]
        if len(mdy2) == 2:
            years[temp_id] = 2018
        else:
            years[temp_id] = mdy2[2]
            if mdy2[2] < 2000: years[temp_id] += 2000
        title_of[temp_id] = full_title
    mdy_sorted = sorted(months, key=lambda x:(years[x], months[x], days[x]), reverse=True)
    print("Top {} of {}".format(max_back, len(mdy_sorted)))
    for x in range(0, max_back): print(x+1, mdy_sorted[x], title_of[mdy_sorted[x]], years[mdy_sorted[x]], months[mdy_sorted[x]], days[mdy_sorted[x]])

    global back_range
    if back_range[0] == 0:
        back_range = (last_back, last_back + 1)
    for x in range(back_range[0], back_range[1]):
        open_in_browser(mdy_sorted[x - 1], title_of[mdy_sorted[x - 1]])

def main():
    os.chdir("c:/writing/scripts")
    drive = get_drive_handle()

    source = drive.CreateFile({'id': source_id})
    source.FetchMetadata('title')

    lister = drive.ListFile().GetList()

    if create_new:
        temp = create_if_not_there(lister, drive)
        if temp:
            return

    if look_for_last:
        open_latest_transcript(lister, drive)
    
b4 = time.time()

cmd_count = 1

gdu_abbrev = defaultdict(str)
see_mod = []
mod_back_days = 7

with open(gdu_data) as file:
    for (line_count, line) in file:
        if line.startswith(";"): break
        if line.startswith("#"): continue
        if line.count('=') != 1:
            print("Line {} needs one equals: {}".format(line_count, line.strip()))
            continue
        x = line.strip().split("=")
        if len(x[1]) != id_length:
            print("Line {} bad id length of {}. Should be {}.".format(len(x[1]), id_length))
            continue
        gdu_abbrev[x[0]] = x[1]

sys.exit()

while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    if arg == 'o' or arg == 'l' or arg == 'lo' or arg == 'ol':
        create_new = True
        look_for_last = False
    elif arg == 'cl' or arg == 'lc':
        create_new = True
        look_for_last = True
        last_back = 1
    elif arg == 'lo' or arg == 'ol' or arg == 'l' or arg == 'o':
        create_new = False
        look_for_last = True
        last_back = 1
    elif arg == 'nt' or arg == 'tn':
        show_time = False
    elif arg == 'st' or arg == 'ts':
        show_time = True
    elif arg == 'nl' or arg == 'ln':
        look_for_last = False
    elif arg[:2] == 'lm':
        see_mod.extend(arg[2:].split(","))
        for q in arg[2:].split(","):
            if q not in gdu_abbrev:
                print(q, "not vaild abbreviation.")
                continue
            see_mod.append(q)
    elif arg[:2] == 'lmd':
        try:
            mod_back_days = int(arg[3:])
        except:
            sys.exit("Need integer for LMD last modified days")
    elif arg[0] == 'b' and mt.is_posneg_int(arg[1:], allow_zero = False):
        look_for_last = True
        look_for_last_mult = False
        look_for_last_num = abs(int(arg[1:]))
        back_range = (abs(int(arg[1:])), abs(int(arg[1:])+1))
    elif arg[0] == 'a' and mt.is_posneg_int(arg[1:], allow_zero = False):
        look_for_last = True
        look_for_last_mult = True
        back_range = (1, abs(int(arg[1:])) + 1)
    elif arg.isdigit():
        look_for_last = True
        last_back = int(arg)
        if last_back > max_back:
            print("Can only go", max_back, "back.")
            last_back = max_back
    elif re.search("^[0-9]+-[0-9]+$", arg):
        ary = [int(x) for x in sorted(re.split("-", arg))]
        if ary[1] > max_back:
            print("Can only go", max_back, "back.")
            ary[1] = max_back
            if ary[0] > max_back:
                ary[0] = max_back
        if ary[0] < 1:
            sys.exit("You need to specify a positive number for the go-back range.")
        back_range = (ary[0], ary[1] + 1)
    elif arg == '?':
        usage()
    else:
        print("Bad parameter", arg)
        usage()
    cmd_count += 1

if __name__ == '__main__':
    main()

if show_time:
    af = time.time()
    print("Program took {:4.2f} seconds.".format(af - b4))