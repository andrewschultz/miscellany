# bgdd.py: blank google drive daily document
#
# creates a blank Google Drive daily document, formatted with title and "IMPORTANT" section
#

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from collections import defaultdict
import os
import re
import pendulum
import sys
from mytools import nohy

look_for_last = False
back_range = (0, 0)
last_back = 1
max_back = 9

x = pendulum.today()
dest_title = "Transcription notes " + x.format("M/D/YYYY")
folder_id = "" # '0BxbuUXtrs7adSFFYMG0zS3VZNFE'
source_id = "1mkbVFs_911fx4qA0NYm1PL4ignwEn6-I4yoJG2oJsTI"

auto_credentials = True

def usage():
    print("Not many commands to use.")
    print("-c = create today's file")
    print("-l/o/ol/lo = look for most recently created file")
    exit()

def open_in_browser(x, file_desc = "google doc"):
    my_url = "https://docs.google.com/document/d/{0}/edit".format(x)
    print("Opening {0} in browser: {1}".format(file_desc, my_url))
    os.system("start {0}".format(my_url))

def get_drive_handle():
    gauth = GoogleAuth()
    if auto_credentials:
        gauth.LoadCredentialsFile("c:/coding/perl/proj/mycreds.txt")
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
        gauth.SaveCredentialsFile("mycreds.txt")
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
            sys.exit("We already have a file named " + dest_title + ". Bailing.")

    dest_id = copy_file(drive.auth.service, source_id, dest_title)
    
    dest = drive.CreateFile({'id': dest_id})
    dest.FetchMetadata('title')
    
    print(dest['title'], "created")

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
    print("Top ", max_back, " of", len(mdy_sorted))
    for x in range(0, max_back): print(x+1, mdy_sorted[x], title_of[mdy_sorted[x]], years[mdy_sorted[x]], months[mdy_sorted[x]], days[mdy_sorted[x]])

    global back_range
    if back_range[0] == 0:
        back_range = (last_back, last_back + 1)
    for x in range(back_range[0], back_range[1]):
        print(x, back_range[0], back_range[1])
        open_in_browser(mdy_sorted[x - 1], title_of[mdy_sorted[x - 1]])

def main():
    os.chdir("c:/writing/scripts")
    drive = get_drive_handle()

    source = drive.CreateFile({'id': source_id})
    source.FetchMetadata('title')

    lister = drive.ListFile().GetList()

    if look_for_last:
        open_latest_transcript(lister, drive)
    else:
        create_if_not_there(lister, drive)
    
cmd_count = 1
while cmd_count < len(sys.argv):
    arg = nohy(sys.argv[cmd_count])
    if arg == 'o' or arg == 'l' or arg == 'lo' or arg == 'ol':
        look_for_last = True
        last_back = 1
    elif arg == 'c':
        look_for_last = False
    elif arg.isdigit():
        look_for_last = True
        last_back = int(arg)
        if last_back > max_back:
            print("Can only go", max_back, "back.")
            last_back = max_back
    elif re.search("^[0-9]+-[0-9]+$", arg):
        ary = sorted(re.split("-", arg))
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