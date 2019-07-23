import os

def done_of(dir_path):
    return os.path.join(dir_path, "done")

def slashy_equals(dir_1, dir_list):
    for dir_2 in dir_list:
        d1 = dir_1.replace("\\", "/").lower()
        d2 = dir_2.replace("\\", "/").lower()
        if (d1 == d2): return dir_2
    return ""
    
def copy_to_done(file_name, dir_path):
    done_path = done_of(dir_path)
    done_from = os.path.join(dir_path, file_name)
    done_target = os.path.join(done_path, file_name)
    if not os.path.exists(done_target):
        print("Copying", done_from, "to", done_target)
        copy(done_from, done_target)

def valid_file(file_name, dir_name): # this should work for from_drive\drive_mod or 
    if "daily" in dir_name or "from_drive" in dir_name: return re.search("^20[0-9]{6}\.txt$", file.lower())
    print("Bad dir name in", dir_name, "for", file_name)
    return False

