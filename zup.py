#
# zup.py replaces zup.pl
#
# zip up project utility, to bring all files into a zip file
#
# todo:
# 2 switch statement in CFG reader (if possible)

import re
import mytools as mt
import i7
import zipfile
import sys
import os

from collections import defaultdict

class zip_project:
    def __init__(self, name):
        self.vertical = False
        self.file_map = defaultdict(str)
        self.time_compare = []
        self.max_zip_size = 0
        self.min_zip_size = 0
        self.version = 1
        self.max_specific_file_size = defaultdict(int)
        self.min_specific_file_size = defaultdict(int)
        self.out_name = ''
        self.command_buffer = []
        self.dropbox_location = ''
        self.size_compare = defaultdict(tuple)

zups = defaultdict(zip_project)

zup_cfg = "c:/writing/scripts/zup.txt"

open_config_on_error = True
auto_bail_on_cfg_error = True

def flag_cfg_error(line_count, bail_string = "No bail string specified", auto_bail = True):
    print(bail_string)
    if open_config_on_error:
        mt.npo(zup_cfg, line_count)
    if auto_bail_on_cfg_error:
        sys.exit()

def read_zup_txt():
    cur_zip_proj = ''
    with open(zup_cfg) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith(';'): break
            if line.startswith('#'): continue
            if not line.strip():
                if cur_zip_proj: # maybe do something super verbose in here
                    cur_zip_proj = ''
                    current_file = ''
                    continue
            if line.startswith("!"):
                print("Remove old artifact (!) from config file at line", line_count)
                continue
            if line.startswith(">>"):
                print("Deprecated >> should be converted to cmd: at line", line_count)
                curzip.command_buffer.append(line[2:].strip())
                continue
            try:
                (prefix, data) = mt.cfg_data_split(line.strip())
            except:
                print("Badly formed data line {} {}".format(line_count, line.strip()))
                continue
            prefix = prefix.lower()

            # keep the below alphabetized

            if prefix == 'cmd':
                curzip.command_buffer.append(data)
                continue
            elif prefix == 'dl':
                curzip.dropbox_location = data
            elif prefix == 'f':
                file_array = data.split("\t")
                if len(file_array) == 1:
                    curzip.file_map[file_array[0]] = os.path.basename(file_array[0])
                elif len(file_array) == 2:
                    curzip.file_map[file_array[0]] = file_array[1]
                else:
                    print("Badly split file line at {} has {} entr(y/ies).".format(line_count, len(file_array)))
                current_file = file_array[0]
            elif prefix == 'min':
                if current_file:
                    curzip.min_specific_file_size[current_file] = int(data)
                else:
                    curzip.min_zip_size = int(data)
            elif prefix == 'max':
                if current_file:
                    curzip.max_specific_file_size[current_file] = int(data)
                else:
                    curzip.max_zip_size = int(data)
            elif prefix == 'proj' or prefix == 'projx':
                accept_alt_proj_name = (prefix == 'projx')
                if cur_zip_proj:
                    flag_cfg_error(line_count, "BAILING redefinition of current project at line")
                proj_read_in = mt.chop_front(line.lower().strip())
                proj_candidate = i7.proj_exp(proj_read_in, return_nonblank = accept_alt_proj_name)
                if proj_candidate:
                    cur_zip_proj = proj_candidate
                    #print("Reading:", cur_zip_proj)
                else:
                    flag_cfg_error(line_count, "BAILING bad project at line {} is {}.".format(line_count, proj_read_in))
                if proj_candidate in zups:
                    flag_cfg_error(line_count, "BAILING redefining zip project at line {} with {}/{}.".format(line_count, proj_read_in, proj_candidate))
                else:
                    zups[proj_candidate] = zip_project(proj_candidate)
                    print("Switching project to", proj_candidate)
                    curzip = zups[proj_candidate]
            elif prefix == 'time':
                time_array = re.split("[<>]", data)
                if len(time_array) != 2:
                    print("Bad timing line {} needs exactly one < or >.".format(line_count))
                    continue
                if '>' in data:
                    curzip.time_compare.append((time_array[0], time_array[1]))
                else:
                    curzip.time_compare.append((time_array[1], time_array[0]))
            elif prefix == 'v':
                zups[proj_candidate].version = int(data)
            else:
                print("Unknown prefix", prefix, "line", line_count)
    print(zup_cfg, "read successfully...")

cmd_count = 1

project_array = []

read_zup_txt()

while cmd_count < len(sys.argv):
    my_proj = i7.proj_exp(sys.argv[cmd_count], return_nonblank = False)
    if my_proj:
        if my_proj in project_array:
            print("Duplicate project", my_proj, "/", sys.argv[cmd_count])
        else:
            project_array.append(my_proj)
        cmd_count += 1
        continue
    arg = mt.nohy(sys.argv[cmd_count])
    cmd_count += 1

print("Project(s):", ', '.join(project_array))
