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

create_new_file = True

x = pendulum.today()
dest_title = "Transcription Notes " + x.format("M/D/YYYY")
folder_id = "" # '0BxbuUXtrs7adSFFYMG0zS3VZNFE'
source_id = "1mkbVFs_911fx4qA0NYm1PL4ignwEn6-I4yoJG2oJsTI"

auto_credentials = True

if sys.argv[1] == 'o':
    create_new_file = False

def open_in_browser(x):
    os.system("start https://docs.google.com/document/d/{0}/edit".format(x))

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
                            
def creste_if_not_there(lister, drive):
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
        print(temp_id)
        months[temp_id] = mdy2[0]
        days[temp_id] = mdy2[1]
        if len(mdy2) == 2:
            years[temp_id] = 2018
        else:
            years[temp_id] = mdy2[2]
            if mdy2[2] < 2000: years[temp_id] += 2000
        title_of[temp_id] = full_title
    mdy_sorted = sorted(months, key=lambda x:(years[x], months[x], days[x]), reverse=True)
    print("Top 5 of", len(mdy_sorted))
    for x in range(0, 5): print(x+1, mdy_sorted[x], title_of[mdy_sorted[x]], years[mdy_sorted[x]], months[mdy_sorted[x]], days[mdy_sorted[x]])
    open_in_browser(mdy_sorted[x])

def main():
    os.chdir("c:/writing/scripts")
    drive = get_drive_handle()

    source = drive.CreateFile({'id': source_id})
    source.FetchMetadata('title')

    lister = drive.ListFile().GetList()

    if create_new_file:
        create_if_not_there(lister, drive)
    else:
        open_latest_transcript(lister, drive)
    
if __name__ == '__main__':
    main()