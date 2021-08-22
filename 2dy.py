#
# 2dy.py: replacement for perl script that went X daily files back.
#
# 2dy.txt is the CFG file
#
# note that this is a misnomer as I in fact only create a file once a week
#
# but it still creates the latest daily file, and the "daily" directory name is kept for posterity
#
# todo: map line of best fit of hourly deltas, then assume average is the value of the trendline at the most recent hour
#

import glob
import xml.etree.ElementTree as ET
import sys
import pendulum
import os
from collections import defaultdict
from shutil import copy
import mytools as mt
from stat import S_IREAD, S_IRGRP, S_IROTH
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates
import matplotlib
import colorama

#init_sect = defaultdict(str)

glob_string = "20*.txt"

#d = pendulum.now()
d = pendulum.today()

#these are covered in the config file, but keep them here to make sure
max_days_new = 7
max_days_back = 1000
goal_per_file = 7000 # deliberately low but will be changed a lot

latest_daily = True
write_base_stats = True

daily = "c:/writing/daily"
daily_proc = "c:/writing/daily/to-proc"
daily_done = "c:/writing/daily/done"

my_daily_dir = daily

stats_file = "c:/writing/temp/daily-stats.txt"

file_header = ""

color_dict = defaultdict(int)
sect_ary = []

files_back_wanted = 1
verbose = False

my_sections_file = "c:/writing/scripts/2dy.txt"

def see_back(this_file = d, my_dir = "", days_back = 7):
    my_file = this_file.subtract(days=days_back).format('YYYYMMDD') + ".txt"
    return os.path.join(my_dir, my_file)

def check_unsaved():
    open_array = []
    e = ET.parse(mt.np_xml)
    root = e.getroot()
    for elem in e.iter('File'):
        itersize += 1
        t = elem.get('filename')
        if 'daily' in t and re.search("[\\\/][0-9]{8}\.txt", t):
            bfp = elem.get("backupFilePath")
            if bfp:
                if not os.path.exists(bfp):
                    print("No backup file for", t, "exists. It should be", bfp)
                    continue
                print(t, "has backup/needs re-saving")
                open_array.append(t)
    if not len(open_array): return
    for x in open_array:
        mt.npo(x, bail = False)

def compare_thousands(my_dir = "c:/writing/daily", bail = True, this_file = "", file_index = -1, overwrite = False):
    os.chdir(my_dir)
    if not this_file:
        g = glob.glob(my_dir + "/" + glob_string)
        this_file = os.path.basename(g[file_index])
    my_size = os.stat(this_file).st_size

    os.chdir(my_dir)
    f = open(stats_file, "r")
    raw_stat_lines = [x for x in f.readlines() if x.strip()]
    f.close()

    ary = raw_stat_lines[-1].split("\t")
    last_size = int(ary[-1])
    hour_delta = my_size - last_size
    header_color = colorama.Back.WHITE
    if hour_delta < 0:
        header_color += colorama.Fore.RED
    elif hour_delta < 200:
        header_color += colorama.Back.RED
    elif hour_delta < 500:
        header_color += colorama.Fore.YELLOW
    elif hour_delta < 1000:
        header_color += colorama.Fore.BLACK
    elif hour_delta < 2000:
        header_color += colorama.Fore.GREEN
    elif hour_delta < 3000:
        header_color += colorama.Fore.BLUE
    elif hour_delta < 4000:
        header_color += colorama.Fore.CYAN
    else:
        header_color += colorama.Fore.MAGENTA
    my_string = header_color + "HOURLY BYTE/THOUSANDS NOW/BEFORE COUNT: {} vs {}, {} vs {}, +{}.".format(my_size, last_size, my_size // 1000, last_size // 1000, my_size - last_size) + colorama.Style.RESET_ALL
    mt.center(my_string)
    thousands = my_size // 1000 - last_size // 1000
    until_next = (1000 - (my_size % 1000))
    right_now = pendulum.now()
    minutes_adjusted = (right_now.minute + 57) % 60
    try:
        rate_for_next = until_next * 60 / (3600 - minutes_adjusted * 60 - right_now.second)
    except:
        print("Oops! Synchronicity! You did this right at x:03! We're going to pretend you have one second left. Just run it again to see the upcoming hour.")
        rate_for_next = 1
    if thousands == 0:
        print(colorama.Fore.CYAN + "No new graph at the top of the hour+3. You need {} bytes, or {:.2f} per minute (including seconds) for the next plateau.".format(until_next, rate_for_next) + colorama.Style.RESET_ALL)
    elif thousands < 0:
        print("Somehow, you dropped down a thousands-plateau from the top of the hour. Hooray, compaction scripts? At any rate you need {} bytes, or {:.2f} per minute (including seconds) for the next distant step up.".format(until_next, rate_for_next))
    else:
        print(colorama.Fore.GREEN + "There will be a new graph at the top of the hour+3. You eclipsed {} thousand{}. {:.2f} per minute (including seconds) for next. Or you need to get just under that, to sandbag.".format(thousands, mt.plur(thousands), rate_for_next) + colorama.Style.RESET_ALL)
    if bail:
        sys.exit()

def dhms(my_int):
    my_int = abs(my_int)
    return '{}d{}h{}m{}s'.format(my_int // 86400, (my_int // 3600) % 24, (my_int // 60) % 60, my_int % 60)

def check_weekly_rate(my_dir = "c:/writing/daily", bail = True, this_file = "", file_index = -1, overwrite = False):
    os.chdir(my_dir)
    if not this_file:
        g = glob.glob(my_dir + "/" + glob_string)
        this_file = os.path.basename(g[file_index])
    t_base = pendulum.local(int(this_file[:4]), int(this_file[4:6]), int(this_file[6:8]))
    t_now = pendulum.now()
    t_goal = t_base.add(days=max_days_new)
    weekly_interval_so_far = (t_now - t_base).in_seconds()
    full_weekly_interval = (t_goal - t_base).in_seconds()
    current_goal = goal_per_file * weekly_interval_so_far // full_weekly_interval
    current_size = os.stat(this_file).st_size
    seconds_delta_from_pace = (current_size - current_goal) * full_weekly_interval // goal_per_file
    current_pace_seconds_delta = weekly_interval_so_far * goal_per_file / current_size
    t_eta = t_base.add(seconds = current_pace_seconds_delta)
    equivalent_time = t_base.add(seconds = current_size * full_weekly_interval // goal_per_file).format("YYYY-MM-DD HH:mm:ss")
    cur_time_readable = t_now.format("YYYY-MM-DD HH:mm:ss")
    print("... calculating notes size vs. goals ...")
    time_dir_string = 'behind' if current_size < current_goal else 'ahead'
    if current_size > goal_per_file:
        mt.center(colorama.Back.YELLOW + colorama.Fore.BLACK + 'Hooray! You hit your weekly goal!' + colorama.Style.RESET_ALL)
    else:
        print((colorama.Fore.RED if current_size < current_goal else colorama.Fore.GREEN) + "Right now at {} you have {} bytes. To be on pace for {} before creating a file, you need to be at {}, so you're {} by {}.".format(cur_time_readable, current_size, goal_per_file, current_goal, time_dir_string, abs(current_goal - current_size)))
        print("That equates to {} second(s) {} of the break-even time for your production, which is {}, {} away.".format(seconds_delta_from_pace, time_dir_string, equivalent_time, dhms(seconds_delta_from_pace) + colorama.Style.RESET_ALL))
    projection = current_size * full_weekly_interval // weekly_interval_so_far
    mt.center(colorama.Fore.YELLOW + "Expected end-of-cycle/week goal: {} bytes, {}{} {}.".format(projection, '+' if projection > goal_per_file else '', projection - goal_per_file, 'ahead' if projection > goal_per_file else 'behind') + colorama.Style.RESET_ALL)
    if current_size < goal_per_file:
        mt.center(colorama.Fore.YELLOW + "ETA to achieve goal: {}, {} away.".format(t_eta.format("YYYY-MM-DD HH:mm:ss"), dhms((t_eta - t_now).in_seconds())) + colorama.Style.RESET_ALL)
        seconds_remaining = full_weekly_interval - weekly_interval_so_far
        bytes_remaining = goal_per_file - current_size
        bytes_per_hour_to_go = bytes_remaining * 3600 / seconds_remaining
        bytes_per_hour_so_far = current_size * 3600 / weekly_interval_so_far
        bytes_per_hour_overall = goal_per_file * 3600 / full_weekly_interval
        mt.center(colorama.Fore.CYAN + "Bytes per hour to hit end-of-week goal: {:.2f}. Bytes overall: {:.2f}. Bytes so far: {:.2f}.".format(bytes_per_hour_to_go, bytes_per_hour_overall, bytes_per_hour_so_far) + colorama.Style.RESET_ALL)
    if bail:
        sys.exit()

def graph_stats(my_dir = "c:/writing/daily", bail = True, this_file = "", file_index = -1, overwrite = False, launch_present = False):
    if not this_file:
        g = glob.glob(my_dir + "/" + glob_string)
        this_file = os.path.basename(g[-abs(file_index)])

    matplotlib.rcParams['timezone'] = 'US/Central'

    os.chdir(my_dir)
    f = open(stats_file, "r")
    raw_stat_lines = f.readlines()
    f.close()

    relevant_stats = []

    for this_line in raw_stat_lines:
        ary = this_line.split("\t")
        if ary[0].lower() == this_file.lower():
            relevant_stats.append(this_line)


    times = []
    sizes = []
    color_array = []
    shape_array = []

    current_size = os.stat(this_file).st_size

    init_ary = relevant_stats[0].split("\t")
    last_ary = relevant_stats[-1].split("\t")
    first_size = int(init_ary[2])
    first_time = pendulum.parse(init_ary[1])
    last_size = int(last_ary[2])
    last_time = pendulum.parse(last_ary[1])
    # print(current_size, last_size, first_size, first_size, first_time, last_size, last_time, (last_time - first_time).total_seconds())

    for r in relevant_stats:
        ary = r.strip().split("\t")
        my_time = pendulum.parse(ary[1])
        times.append((my_time - pendulum.from_timestamp(0)).total_seconds() / 86400)
        sizes.append(int(ary[2]))
        if len(sizes) == 1:
            color_array.append('black')
            shape_array.append(30)
            last_time = my_time
            continue
        if (sizes[-1] // 1000) - (sizes[-2] // 1000) > 0:
            shape_array.append(30 + 30 * (sizes[-1] // 1000 - sizes[-2] // 1000))
        else:
            shape_array.append(30)
        size_delta = sizes[-1] - sizes[-2]
        color_array.append(mt.text_from_values(color_dict, size_delta))
        if my_time.hour == last_time.hour:
            print("WARNING line", ' / '.join(ary), "has duplicate hour. Minutes are {} vs {}. You probably ran a test twice. It'd be best to delete it.\n    Run 2dy.py es to do so.".format(last_time.minute, my_time.minute))
        elif my_time.hour - last_time.hour > 1:
            print("WARNING line", ' / '.join(ary), "skipped at least one hour. You probably deleted data. It's not a big deal, but O Lost and all that sort of thing.\n    Run 2dy.py es to see the line.".format(last_time.minute, my_time.minute))
        last_time = my_time

    init_from_epoch = (first_time - pendulum.from_timestamp(0)).total_seconds() / 86400

    times = np.array(times)
    sizes = np.array(sizes)

    (a, b) = np.polyfit(times, sizes, 1)
    b0 = b + a * init_from_epoch
    my_label = "{}\nbytes={:.2f}*days{}{:.2f}".format(my_time.to_day_datetime_string(), a, '+' if b0 > 0 else '', b0)

    my_graph_graphic = "c:/writing/temp/daily-{}{}".format('past-' if abs(file_index) > 1 else '', my_time.format("YYYY-MM-DD-HH.png"))

    if not overwrite and os.path.exists(my_graph_graphic):
        print(my_graph_graphic, "already exists. I am not overwriting it. Use the -gso flag or specify files back, e.g. gs1 to override this reject.{}".format("" if launch_present else " -gsl launches."))
        if launch_present:
            mt.text_in_browser(my_graph_graphic)
        if bail:
            sys.exit()
        return

    mso = mt.modified_size_of(this_file)
    if mso > current_size:
        my_label += "\n{} bytes (unsaved) since last data check".format(mso - current_size)
    elif current_size > last_size:
        my_label += "\n{} bytes since last data check".format(current_size - last_size)

    if current_size > first_size:
        expected_kb = (current_size - first_size) * 86400 * 7 / (last_time - first_time).total_seconds() + first_size
        my_label += "\nAverage from last exp bytes: {:.2f}".format(expected_kb)

    if a:
        my_label += "\nBest-fit exp bytes: {:.2f}/{:.2f}".format(7 * a + b0, times[-1] * a + b)

    plt.figure(figsize=(15, 12))
    plt.xticks(rotation=45, ha='right')
    plt.scatter(times, sizes, color = color_array, s = shape_array, label=my_label)
    plt.xlabel("days")
    plt.ylabel("bytes")

    plt.plot(times, a*times+b) # line of best fit
    per_day = goal_per_file // max_days_new
    plt.plot(times, per_day * times - per_day * init_from_epoch) # general pacing line assuming consistent output

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:00'))
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval = 6 if times[-1] - times[0] < 4 else 12))
    plt.legend(loc='upper left')
    plt.savefig(my_graph_graphic)
    mt.text_in_browser(my_graph_graphic)
    if bail:
        sys.exit()

def put_stats(bail = True, print_on_over = 0, check_floor = False):
    os.chdir("c:/writing/daily")
    f = open(stats_file, "a")
    ld = mt.last_daily_of()
    pn = pendulum.now()
    out_string = "{}\t{}\t{}".format(ld, pendulum.now(), os.stat(ld).st_size)
    f.write(out_string + "\n")
    print(out_string)
    f.close()

    if check_floor:
        f = open(stats_file)
        ary = f.readlines()
        f.close()
        before_last_bytes = int(ary[-2].split("\t")[2]) // 1000
        last_bytes = int(ary[-1].split("\t")[2]) // 1000
        byte_delta = last_bytes - before_last_bytes
        if byte_delta:
            print("Thousands-floor increased from {} to {}, so I am opening a new graph".format(before_last_bytes, last_bytes))
            graph_stats()
        else:
            print("Thousands-floor stayed constant at {}, so I am not going to create a new graph".format(last_bytes))
    if print_on_over:
        f = open(stats_file)
        ary = f.readlines()
        f.close()
        before_last_bytes = int(ary[-2].split("\t")[2])
        last_bytes = int(ary[-1].split("\t")[2])
        byte_delta = last_bytes - before_last_bytes
        if byte_delta >= print_on_over:
            print(last_bytes, "increase at or over threshold of", byte_delta, "so I am opening a new graph")
            graph_stats()
        else:
            print(last_bytes, "is short of", byte_delta, "so I am not going to create a new graph")

    if bail:
        sys.exit()

def move_to_proc(my_dir = "c:/writing/daily"):
    import win32ui
    import win32con

    os.chdir(my_dir)
    print("Moving", my_dir, "to to-proc.")
    g1 = mt.dailies_of(my_dir)
    g2 = mt.dailies_of(my_dir + "/to-proc")

    threshold = see_back(d, '', 7)
    temp_save_string = ""

    for q in g1:
        if q > threshold:
            print(q, "above threshold of", threshold, "so ignoring. Set mn=0 to harvest/read-only all files.") # this should only happen once per run
            continue
        if mt.is_daily(q):
            abs_q = os.path.abspath(q)
            if mt.is_npp_modified(abs_q):
                temp = win32ui.MessageBox("{} is open in notepad. Save and click OK, or CANCEL.".format(abs_q), "Save {} first!".format(q), win32con.MB_OKCANCEL)
                if temp == win32con.IDCANCEL:
                    temp_save_string += "\n" + q
                    continue
            if q not in g2:
                print(q, "needs to be moved to to-proc and set read-only. Let's do that now!")
                copy(q, "to-proc/{}".format(q))
                os.chmod(q, S_IREAD|S_IRGRP|S_IROTH)
            else:
                if os.access(q, os.W_OK):
                    print(q, "needs to be set read-only in the base directory. Let's do that now!")
                    os.chmod(q, S_IREAD|S_IRGRP|S_IROTH)

    if temp_save_string:
        to_save = "c:/writing/temp/daily-to-save.htm"
        f = open(to_save, "w")
        f.write("Daily file(s) that need saving:")
        f.write(temp_save_string)
        f.close()
        mt.text_in_browser(to_save)

    if 'daily' not in my_dir:
        sys.exit("Bailing since we're using non-daily directory.")

def usage(param = 'Cmd line usage'):
    print(param)
    print('=' * 50)
    print("(-?)f (#) = # files back (or # without f)")
    print("(-?)m (#) = # max days back")
    print("(-?)mn/n/nm (#) = # max new days back")
    print("(-?)l or ln/nl = latest-daily (or not)")
    print("(-?)v or vn/nv = toggle verbosity")
    print("(-?)p/tp = move to to_proc, tk/kt and dt/td to keep/drive")
    print("(-?)ps = put stats, (-?)gs = get stats, (-?)es = edit stats, (-?)ss = sift stats")
    print("(-)e = edit 2dy.txt to add sections or usage or adjust days_new. ec = edit code, es = edit stats")
    print("(-)ct(o) checks thousands, (-)wr(o) checks weekly writing goals based on current document size. O = only do this")
    exit()

def poss_thousands(my_int):
    my_int = int(my_int)
    if my_int < 1000:
        return my_int * 1000
    return my_int

def read_2dy_cfg():
    global sect_ary
    global file_header
    global goal_per_file
    global max_days_new
    global min_days_new
    global glob_string
    global file_header
    global color_dict
    this_weeks_goal = 0
    temp_glob = []
    with open(my_sections_file) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith("#"): continue
            if line.startswith(";"): break
            (prefix, data) = mt.cfg_data_split(line)
            if prefix == 'goalperfile':
                goal_per_file = poss_thousands(data)
            elif prefix == 'maxnew':
                max_days_new = int(data)
            elif prefix == 'maxback':
                min_days_new = int(data)
            elif prefix == 'glob':
                glob_string = data
            elif prefix == 'file_header':
                file_header += data.replace("\\", "\n") + "\n"
            elif prefix in ( 'color', 'colors' ):
                color_dict = mt.quick_dict_from_line(line, use_ints = True)
            elif prefix in ( 'defaults', 'sect', 'section', 'sections' ):
                sect_dict = mt.quick_dict_from_line(line)
                if len(sect_ary):
                    print("Adding to non-blank sections array on line {}".format(line_count))
                sect_ary.extend(sect_dict)
            elif prefix.isdigit() and len(prefix) == 8:
                file_name = prefix + ".txt"
                if not len(temp_glob):
                    temp_glob = glob.glob("c:/writing/daily/20*.txt")
                if file_name != os.path.basename(temp_glob[-1]):
                    print("WARNING line {} has outdated custom goal {}. Comment it out or delete it.".format(line_count, file_name))
                else:
                    this_weeks_goal = poss_thousands(data)
            else:
                print("WARNING", my_sections_file, "line", line_count, "unrecognized data", line.strip())
    if this_weeks_goal > 0:
        goal_per_file = this_weeks_goal
    if len(sect_ary) == 0:
        print("WARNING", my_sections_file, "has no default sections.")

def create_new_file(my_file, launch = True):
    print("Creating new daily file", my_file)
    f = open(my_file, "w")
    if file_header:
        f.write(file_header)
    for s in sect_ary: f.write("\n\\{:s}\n".format(s))
    f.close()
    if write_base_stats and my_daily_dir == daily:
        put_stats(bail = False)
    if launch: mt.npo(my_file, my_line = 500)

#
# main coding block
#
# todo: look on command line

os.chdir("c:/writing/scripts")

cmd_count = 1

read_2dy_cfg()

while cmd_count < len(sys.argv):
    arg = mt.nohy(sys.argv[cmd_count])
    if arg[0] == 'f' and arg[1:].isdigit():
        files_back_wanted = int(arg[1:])
        latest_daily = False
    elif arg.isdigit():
        files_back_wanted = int(arg)
        latest_daily = False
    elif arg[0] == 'm' and arg[1:].isdigit():
        max_days_back = int(arg[1:])
        latest_daily = False
    elif arg[:2] in ( 'mn', 'nm' ) and arg[2:].isdigit():
        max_days_new = int(arg[2:])
        latest_daily = False
    elif arg == 'l': latest_daily = True
    elif arg in ( 'nl', 'ln' ): latest_daily = False
    elif arg == 'v': verbose = True
    elif arg in ( 'nv', 'vn' ): verbose = False
    elif arg == 'e': mt.npo(my_sections_file)
    elif arg == 'em': mt.npo(__file__)
    elif arg == 'es': mt.npo(stats_file)
    elif arg in ( 'p', 'tp', 'pt', 't'): move_to_proc()
    elif arg == 'cto':
        compare_thousands(bail = True)
    elif arg == 'ct':
        compare_thousands(bail = False)
    elif arg.startswith('wr'):
        run_weekly_check = True
        weekly_bail = arg.startswith('wro')
        temp = arg[2 + weekly_bail:]
        if temp.isdigit():
            goal_per_file = 1000 * int(temp)
            print("Adjusting goal to", goal_per_file)
    elif arg.startswith('g=') or (arg.startswith('g') and arg[1:].isdigit()):
        if arg[1] == '=':
            try:
                goal_per_file = 1000 * int(arg[2:])
            except:
                sys.exit("Need a number after g=")
        else:
            goal_per_file = 1000 * int(arg[1:])
    elif arg == 'gs': graph_stats()
    elif arg[:2] == 'gs' and arg[2:].isdigit():
        file_index = int(arg[2:])
        if abs(file_index) == 1:
            print("Note: this is not zero-based, so 1 is the most recent and the default.")
        graph_stats(file_index = file_index, overwrite = True)
    elif arg == 'gsl': graph_stats(overwrite = True, launch_present = True)
    elif arg == 'gso': graph_stats(overwrite = True)
    elif arg == 'gsu': graph_stats(overwrite = False)
    elif arg == 'ps': put_stats()
    elif arg == 'psr': put_stats(check_floor = True)
    elif arg == 'bs': write_base_stats = False
    elif arg[:2] == 'ps' and arg[2:].isdigit(): put_stats(print_on_over = int(arg[2:]))
    elif arg in ( 'gk', 'kg' ): my_daily_dir = "c:/coding/perl/proj/from_keep"
    elif arg in ( 'gd', 'dg' ): my_daily_dir = "c:/coding/perl/proj/from_drive"
    elif arg in ( 'tk', 'kt' ): move_to_proc("c:/coding/perl/proj/from_keep")
    elif arg in ( 'td', 'dt' ): move_to_proc("c:/coding/perl/proj/from_drive")
    elif arg == '?': usage()
    else: usage("Bad parameter {:s}".format(arg))
    cmd_count += 1

if run_weekly_check:
    check_weekly_rate(bail = weekly_bail)

os.chdir(my_daily_dir)

if latest_daily:
    found_done_file = False
    for x in range(0, max_days_new):
        day_file = see_back(d, my_daily_dir, x)
        day_done_file = see_back(d, os.path.join(my_daily_dir, "done"), x)
        if os.path.exists(day_file):
            if os.stat(day_file).st_size == 0:
                print("Ignoring blank file", day_file)
                continue
            print("Found recent daily file {:s}, opening.".format(day_file))
            os.system(day_file)
            exit()
        if os.path.exists(day_done_file): found_done_file = day_done_file
    if found_done_file: sys.exit("Found {:s} in done folder. Not opening new one.")
    print("Looking back", max_days_new, "days, daily file not found.")
    create_new_file(see_back(d, my_daily_dir, 0))
    exit()

files_back_in_dir = 0

for x in range(0, max_days_back):
    day_file = see_back(d, my_daily_dir, x)
    if os.path.exists(day_file):
        if os.stat(day_file).st_size == 0:
            print("Ignoring blank file", day_file)
            continue
        files_back_in_dir += 1
        if verbose and files_back_in_dir <= files_back_wanted: print("Skipping", day_file)
    if files_back_in_dir > files_back_wanted:
        print("Got daily file", day_file, files_back_wanted, "files back.")
        os.system(day_file)
        exit()

print("Failed to get a file in the last", max_days_back, "every 6 hours")

