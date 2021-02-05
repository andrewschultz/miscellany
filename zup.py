#
# zup.py replaces zup.pl
#
# zip up project utility, to bring all files into a zip file
#

import mytools as mt
import i7
import zipfile
import sys

from collections import defaultdict

class zip_project:
    def __init__(self, name):
        self.vertical = False
        self.file_map = defaultdict(str)
        self.time_compare = defaultdict(tuple)
        self.max_zip_size = 0
        self.min_zip_size = 0
        self.version = 1
        self.out_name = '{}.zip'.format(name)
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
            if line.startswith("!"):
                print("Remove old artifact (!) from config file at line", line_count)
                continue
            if line.startswith("proj=") or line.startswith("projx="):
                accept_alt_proj_name = line.startswith("projx")
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
    print(zup_cfg, "read successfully...")

read_zup_txt()