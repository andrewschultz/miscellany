#
# zup.py replaces zup.pl
#
# zip up project utility, to bring all files into a zip file
#
# todo:
# 2 switch statement in CFG reader (if possible)

import glob
import re
import mytools as mt
import i7
import zipfile
import sys
import os
import shutil
import pyperclip
import filecmp
import shlex
import colorama

from collections import defaultdict

class zip_project:
    def __init__(self, name): #alphabetical
        self.vertical = False
        self.build_type = 'b' if is_beta(name) else 'r'
        self.command_post_buffer = []
        self.command_pre_buffer = []
        self.dir_copy = []
        self.dropbox_location = ''
        self.file_map = defaultdict(str)
        self.launch_files = []
        self.max_zip_size = 0
        self.max_specific_file_size = defaultdict(int)
        self.min_zip_size = 0
        self.min_specific_file_size = defaultdict(int)
        self.out_name = ''
        self.post_build = []
        self.size_compare = defaultdict(tuple)
        self.time_compare = []
        self.version = '1'

zups = defaultdict(zip_project)

zip_dir = "c:/games/inform/zip"
dropbox_bin_dir = "c:/users/andrew/dropbox/bins"
zup_cfg = "c:/writing/scripts/zup.txt"

default_from_cfg = ""

copy_link = False
copy_link_only = False
skip_temp_out = False
bail_on_first_build_error = True
build_before_zipping = False
open_config_on_error = True
auto_bail_on_cfg_error = True
verbose = False
copy_dropbox_after = False

def usage(header="Usage for zup.py"):
    print(header)
    print("=" * 50)
    print("b = build before zipping")
    print("bby/ybb bbn/nbb = bail on first build error, or not")
    print("bcy/ybc bcn/nbc = bail on first cfg read error, or not")
    print("c/ce/e = open config file for editing")
    print("cd = copies to dropbox after")
    print("cl/clo = copy link/copy link only")
    print("v = verbose")
    print("specify project(s) to zip on command line")
    exit()

def copy_first_link(project_array, bail = True):
    for p in project_array:
        if len(project_array) > 1:
            print("Only copying first link from project")
        if zups[p].dropbox_location:
            pyperclip.copy(zups[p].dropbox_location)
            print("Copied", p, "dropbox location to", zups[p].dropbox_location)
            if bail:
                sys.exit()
        else:
            print("Skipping", p, "as it has no dropbox location")
    print("Found nothing to copy over.{}".format(" Bailing." if bail else ""))
    if bail:
        sys.exit()

def project_or_beta_name(proj_read_in, accept_alt_proj_name):
    if accept_alt_proj_name:
        return proj_read_in
    temp_project = i7.proj_exp(proj_read_in, return_nonblank = False)
    if temp_project:
        return temp_project
    temp_project = i7.proj_exp(proj_read_in[:-2], return_nonblank = False)
    if temp_project:
        return temp_project + "-b"
    temp_project = i7.proj_exp(proj_read_in[:-1], return_nonblank = False)
    if temp_project:
        if temp_project + '-b' in zups:
            return temp_project + '-b'
        return temp_project + "b"
    return i7.proj_exp(proj_read_in, return_nonblank = False)

def is_beta(proj_read_in):
    temp_project = i7.proj_exp(proj_read_in, return_nonblank = False)
    if temp_project:
        return False
    if proj_read_in[-2:] == '-b':
        temp_project = i7.proj_exp(proj_read_in[:-2], return_nonblank = False)
        if temp_project:
            return True
    if proj_read_in[-1:] == 'b':
        temp_project = i7.proj_exp(proj_read_in[:-1], return_nonblank = False)
        if temp_project:
            return True
    return False

def zip_write_nonzero_file(zip_handle, from_path, to_path):
    if not os.path.exists(from_path):
        sys.exit("Could not find file {}. Bailing.".format(from_path))
    if os.stat(from_path).st_size == 0:
        sys.exit("Tried to write zero-byte file {} to zip. Bailing.".format(from_path))
    zip_handle.write(from_path, to_path, zipfile.ZIP_DEFLATED)

def zipdir(path_from, path_to, zip_handle): # thanks https://stackoverflow.com/questions/1855095/how-to-create-a-zip-archive-of-a-directory-in-python
    for root, dirs, files in os.walk(path_from):
        for file in files:
            zip_write_nonzero_file(zip_handle, os.path.join(root, file), os.path.join(path_to, os.path.relpath(os.path.join(root, file), path_from)))

def flag_cfg_error(line_count, bail_string = "No bail string specified", auto_bail = True):
    print(colorama.Fore.MAGENTA + colorama.Back.WHITE + bail_string + colorama.Style.RESET_ALL)
    if open_config_on_error:
        mt.npo(zup_cfg, line_count)
    if auto_bail_on_cfg_error:
        print(colorama.Fore.RED + "Bailing after first error. To change this, set flag -bbn/nbb." + colorama.Style.RESET_ALL)
        sys.exit()

def flag_zip_build_error(bail_string):
    print(bail_string)
    if bail_on_first_build_error:
        print("Bailing after first error. To change this, set flag -bbn/nbb.")
        sys.exit()

def add_to_file_map(this_map, from_file, to_file, line_count):
    from_file_mod = os.path.normpath(from_file)
    if from_file_mod in this_map:
        flag_cfg_error(line_count, "Line {} has duplicate file {} to {}.".format(line_count, from_file, to_file))
        return
    this_map[from_file_mod] = to_file

def read_zup_txt():
    global default_from_cfg
    cur_zip_proj = ''
    file_base_dir = ''
    file_to_dir = ''
    current_file = ''
    with open(zup_cfg) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith(';'): break
            if line.startswith('#'): continue
            if not line.strip():
                if cur_zip_proj: # maybe do something super verbose in here
                    cur_zip_proj = ''
                    current_file = ''
                    file_base_dir = ''
                continue
            if line.startswith("!"):
                flag_cfg_error(line_count, "Remove old artifact (!) from config file at line", line_count)
                continue
            if line.startswith(">>"):
                flag_cfg_error(line_count, "Deprecated >> should be converted to cmdpre: or cmdpost: at line", line_count)
                curzip.command_buffer.append(line[2:].strip())
                continue
            try:
                (prefix, data) = mt.cfg_data_split(line.strip())
            except:
                flag_cfg_error(line_count, "Badly formed data line {}: |{}|".format(line_count, line.strip()))
                continue
            prefix = prefix.lower()
            if not data:
                flag_cfg_error(line_count, "WARNING blank data at line {}.".format(line_count))
                continue

            # keep the below alphabetized

            if prefix == 'build':
                curzip.build_type = data
            elif prefix == 'cmdpre':
                curzip.command_pre_buffer.append(data)
            elif prefix == 'cmdpost':
                curzip.command_post_buffer.append(data)
            elif prefix == 'default':
                if cur_zip_proj:
                    flag_cfg_error(line_count, "default project definition inside project block line {}.".format(line_count))
                if default_from_cfg:
                    flag_cfg_error(line_count, "default project redefined line {}.".format(line_count))
                default_from_cfg = i7.proj_exp(data)
            elif prefix in ( 'd', 'dircopy' ):
                temp_ary = data.split('=')
                if not os.path.isabs(temp_ary[0]):
                    flag_cfg_error(line_count, "Line {} {} must be absolute path.".format(line_count, temp_ary[0]))
                if '=' not in data:
                    curzip.dir_copy = (temp_ary[0], '.')
                elif data.count('=') == 1:
                    curzip.dir_copy = tuple(temp_ary)
                else:
                    flag_cfg_error(line_count, "Too many = in line {} for dircopy.".format(line_count))
            elif prefix in ( 'dl', 'dropbox' ):
                curzip.dropbox_location = data
            elif prefix in ( 'f', 'file' ):
                file_array = data.split("\t")
                if "*" in file_array[0]:
                    wild_cards = glob.glob(file_array[0])
                    if len(wild_cards) == 0:
                        flag_cfg_error(line_count, "No wild cards in {} for project {} at line {}.".format(file_array[0], cur_zip_proj, line_count))
                        continue
                    for x in wild_cards:
                        add_to_file_map(curzip.file_map, x, os.path.join(file_to_dir, os.path.join(file_array[1], x) if len(file_array) > 1 else os.path.basename(x)), line_count)
                    continue
                if len(file_array) == 1:
                    add_to_file_map(curzip.file_map, file_array[0], os.path.basename(file_array[0]), line_count)
                elif len(file_array) == 2:
                    add_to_file_map(curzip.file_map, file_array[0], file_array[1], line_count)
                else:
                    flag_cfg_error(line_count, "Badly split file line at {} has {} entr(y/ies).".format(line_count, len(file_array)))
                if '*' not in data:
                    current_file = file_array[0]
                    continue
            elif prefix in ( 'fb', 'b' ):
                dir_array = data.split("\t")
                file_base_dir = dir_array[0]
                file_to_dir = dir_array[1] if len(dir_array) > 1 else ''
            elif prefix in ( 'fn', 'n' ):
                if not file_base_dir:
                    flag_cfg_error(line_count, "fn file-nested has no base dir for project {} at line {}.".format(cur_zip_proj, line_count))
                    continue
                if '*' not in data:
                    file_array = data.split("\t")
                    if len(file_array) == 1:
                        to_file = data
                    elif len(file_array) == 2:
                        to_file = file_array[1]
                    else:
                        flag_cfg_error(line_count, "Badly split file line at {} has {} entr(y/ies).".format(line_count, len(file_array)))
                    if file_to_dir:
                        to_file = "{}/{}".format(file_to_dir, to_file)
                    add_to_file_map(curzip.file_map, os.path.join(file_base_dir, data), to_file, line_count)
                    continue
                wild_cards = glob.glob(os.path.join(file_base_dir, data))
                if len(wild_cards) == 0:
                    flag_cfg_error(line_count, "No wild cards in {} for project {} at line {}.".format(file_array[0], cur_zip_proj, line_count))
                    continue
                for x in wild_cards:
                    add_to_file_map(curzip.file_map, x, os.path.join(file_to_dir, os.path.basename(x)), line_count)
            elif prefix == 'lf':
                curzip.launch_files.append(data)
            elif prefix == 'min':
                if current_file:
                    if current_file in curzip.min_specific_file_size:
                        flag_cfg_error(line_count, "Redefined minimum component file size line {}.".format(line_count))
                    curzip.min_specific_file_size[current_file] = int(data)
                else:
                    if curzip.min_zip_size:
                        flag_cfg_error(line_count, "Redefined maximum zipfile size line {}.".format(line_count))
                    curzip.min_zip_size = int(data)
            elif prefix == 'max':
                if current_file:
                    if current_file in curzip.max_specific_file_size:
                        flag_cfg_error(line_count, "Redefined maximum component file size line {}.".format(line_count))
                    curzip.max_specific_file_size[current_file] = int(data)
                else:
                    if curzip.max_zip_size:
                        flag_cfg_error(line_count, "Redefined maximum zipfile size line {}.".format(line_count))
                    curzip.max_zip_size = int(data)
            elif prefix in ( 'out', 'outfile' ):
                if curzip.out_name:
                    flag_cfg_error(line_count, "Renaming outfile name for {} at line {}.".format(cur_zip_proj, line_count))
                curzip.out_name = data
            elif prefix in ( 'proj', 'projx' ):
                if data.endswith('b') and not data.endswith('-b'):
                    if data[:-1] in i7.i7x and data not in i7.i7x:
                        flag_cfg_error(line_count, "WARNING: likely beta build {} should end in -b, not just b.".format(data), auto_bail = False)
                accept_alt_proj_name = (prefix == 'projx')
                if cur_zip_proj:
                    flag_cfg_error(line_count, "BAILING redefinition of current project at line")
                proj_read_in = mt.chop_front(line.lower().strip())
                proj_candidate = project_or_beta_name(proj_read_in, accept_alt_proj_name)
                if proj_candidate:
                    cur_zip_proj = proj_candidate
                    #print("Reading:", cur_zip_proj)
                else:
                    flag_cfg_error(line_count, "BAILING bad project at line {} is {}. Use PROJX if you want something not defined in i7p.txt".format(line_count, proj_read_in))
                if proj_candidate in zups:
                    flag_cfg_error(line_count, "BAILING redefining zip project at line {} with {}/{}.".format(line_count, proj_read_in, proj_candidate))
                else:
                    zups[proj_candidate] = zip_project(proj_candidate)
                    if verbose:
                        print("Switching project to", proj_candidate)
                    curzip = zups[proj_candidate]
            elif prefix == 'postbuild':
                curzip.post_build.append(data)
            elif prefix == 'time':
                time_array = re.split("[<>]", data)
                if len(time_array) != 2:
                    flag_cfg_error(line_count, "Bad timing line {} needs exactly one < or >.".format(line_count))
                    continue
                if '>' in data:
                    curzip.time_compare.append((time_array[0], time_array[1]))
                else:
                    curzip.time_compare.append((time_array[1], time_array[0]))
            elif prefix in ( 'v', 'version' ):
                if re.search("[^0-9\.]", data):
                    flag_cfg_error(line_count, "WARNING version must only contain integers or decimals at line {}".format(line_count))
                zups[proj_candidate].version = data
            else:
                if line.startswith("/") or line.startswith("\\"):
                    flag_cfg_error(line_count, "WARNING we probably need F= before a relative file path at line {}".format(line_count))
                elif re.match("[a-z0-9 \-]+[\\\/]", line, flags=re.IGNORECASE):
                    flag_cfg_error(line_count, "WARNING we probably need F= before a Unix-type file path at line {}".format(line_count))
                elif re.match("[a-z]:[\\\/]", line, flags=re.IGNORECASE):
                    flag_cfg_error(line_count, "WARNING we probably need F= before a Windows-type file path at line {}".format(line_count))
                else:
                    flag_cfg_error(line_count, "Unknown prefix {} line {}".format(prefix, line_count))
    print(zup_cfg, "read successfully...")

cmd_count = 1

project_array = []

read_zup_txt()

while cmd_count < len(sys.argv):
    arg = sys.argv[cmd_count]
    my_proj = project_or_beta_name(arg, False)
    if my_proj:
        if my_proj in project_array:
            print("Duplicate project", my_proj, "/", sys.argv[cmd_count])
        else:
            project_array.append(my_proj)
        cmd_count += 1
        continue
    elif arg in zups:
        print("Likely custom project {} that you specified is added to project array.".format(my_proj if my_proj else arg))
        project_array.append(arg)
        cmd_count += 1
        continue
    arg = mt.nohy(sys.argv[cmd_count])
    if arg == 'b':
        build_before_zipping = True
    elif arg in ( 'bby', 'ybb' ):
        bail_on_first_build_error = True
    elif arg in ( 'bbn', 'nbb' ):
        bail_on_first_build_error = False
    elif arg == 'b':
        build_before = True
    elif arg in ( 'c', 'ce', 'ec' ):
        mt.npo(zup_cfg)
    elif arg in ( 'bcy', 'ybc' ):
        bail_on_first_build_error = True
    elif arg in ( 'bcn', 'nbc' ):
        bail_on_first_build_error = False
    elif arg == 'v':
        verbose = True
    elif arg == 'cl':
        copy_link = True
    elif arg == 'clo':
        copy_link_only = True
    elif arg in ( 'cd', 'dc' ):
        copy_dropbox_after = True
    elif arg == 'oce':
        open_config_on_error = True
    elif arg == 'skiptemp': # this is a hidden option, because I really don't want to expose it unless I have to
        skip_temp_out = True
    elif arg == '?':
        usage()
    else:
        usage("Bad command line argument {}".format(arg))
    cmd_count += 1

if not project_array:
    temp_proj = i7.dir2proj()
    if temp_proj:
        print("Going with project from current directory, {}, since it was not specified.".format(temp_proj))
        if default_from_cfg:
            print("Move if you want to use the general default {}.".format(default_from_cfg))
        project_array.append(temp_proj)
    elif default_from_cfg:
        print("Going with default from cfg file, {}.".format(default_from_cfg))
        project_array.append(default_from_cfg)
    else:
        sys.exit("Could not get a project from command line, current directory or config file. Bailing.")

if copy_link_only:
    copy_first_link(project_array, bail = True)

print("Project(s):", ', '.join(project_array))

for x in zups:
    if zups[x].out_name:
        zups[x].out_name = zups[x].out_name.replace("%", zups[x].version)
    else:
        zups[x].out_name = '{}.zip'.format(name)

out_temp = os.path.join(zip_dir, "temp.zip")

print("Failed creations will go to temp.zip.")

for p in project_array:
    if p not in zups:
        print("WARNING potentially valid project {} not in zup.txt.".format(p))
        continue
    for x in zups[p].command_pre_buffer:
        print("Running pre-command", x)
        subprocess.open(shlex.split(' ', x))
    if build_before_zipping:
        is_beta = p.endswith("-b")
        p2 = p[:-2] if zups[p].build_type == "b" else p
        tempcmd = "icl.py {} {}".format(zups[p].build_type, p2)
    final_zip_file = os.path.join(zip_dir, zups[p].out_name)
    init_zip_file = final_zip_file if skip_temp_out else out_temp
    zip = zipfile.ZipFile(init_zip_file, 'w')
    if p not in zups:
        print("WARNING: {} did not have a manifesto defined in the cfg file.".format(p))
        continue
    for x in zups[p].file_map:
        if not is_beta(p) and ('beta-' in x or 'beta ' in x):
            print(colorama.Fore.MAGENTA + colorama.Back.WHITE + "WARNING: beta-named file {} in non-beta assembly {}.".format(x, p) + colorama.Style.RESET_ALL)
        zip_write_nonzero_file(zip, x, zups[p].file_map[x])
    for x in zups[p].max_specific_file_size:
        if os.stat(x).st_size > zups[p].max_specific_file_size[x]:
            flag_zip_build_error("SINGLE FILE OVER MAX SIZE {} {} > {}".format(x, os.stat(x).st_size, zups[p].max_specific_file_size[x]))
    for x in zups[p].min_specific_file_size:
        if os.stat(x).st_size < zups[p].min_specific_file_size[x]:
            flag_zip_build_error("SINGLE FILE UNDER MIN SIZE {} {} < {}".format(x, os.stat(x).st_size, zups[p].min_specific_file_size[x]))
    zip.close()
    zip_size = os.stat(init_zip_file).st_size
    if zups[p].max_zip_size and zip_size > zups[p].max_zip_size:
        flag_zip_build_error("ARCHIVE OVER MAX SIZE {} {} > {}".format(final_zip_file, zip_size, zups[p].max_zip_size))
    if zip_size < zups[p].min_zip_size:
        flag_zip_build_error("ARCHIVE UNDER MIN SIZE {} {} < {}".format(final_zip_file, zip_size, zups[p].min_zip_size))
    if not skip_temp_out:
        shutil.move(out_temp, final_zip_file)
    print("    SUCCESSFULLY wrote {} from {}.".format(final_zip_file, p))
    for x in zups[p].command_post_buffer:
        print("Running post-command", x)
        subprocess.open(shlex.split(' ', x))
    if copy_dropbox_after:
        if os.path.exists(os.path.join(dropbox_bin_dir, zups[p].out_name)):
            if filecmp.cmp(final_zip_file, os.path.join(dropbox_bin_dir, zups[p].out_name)):
                print("No changes between current dropbox file and recreated zip file {}. Skipping.".format(zups[p].out_name))
                continue
        else:
            print("No dropbox file yet. This is the first copy-over.")
        target = os.path.join(dropbox_bin_dir, zups[p].out_name)
        print("Copying {} to dropbox target {}".format(zups[p].out_name, target))
        shutil.copy(final_zip_file, os.path.join(dropbox_bin_dir, zups[p].out_name))

if not copy_dropbox_after:
    print("-cd copies to dropbox after.")

if copy_link:
    copy_first_link(project_array, bail = False)

if os.path.exists(out_temp):
    os.remove(out_temp)
