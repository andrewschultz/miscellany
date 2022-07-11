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
# todo: "L" batch file that goes back X files should see if there is a to-proc, and if current is read-only and X is not, go to it

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
import re

#init_sect = defaultdict(str)

TOTAL_BYTES = 1
HOURLY_BYTES = 2

glob_string = "20*.txt"

#d = pendulum.now()
d = pendulum.today()

#these are covered in the config file, but keep them here to make sure
max_days_new = 7
max_days_back = 1000
goals_and_stretch = [ 7000 ] # deliberately low but will be changed a lot and also is defined in CFG file
minimum_seconds_between = 3000
super_stretch_delta = 10000
stretch_offset = 0
offset_seconds = 180 # my script runs at 3 and 33 past the hour, and thus calculations should start 180 seconds past the half/top of the hour
post_stretch_max = 10

stretch_special = []

GRAPH_LAUNCH_NEVER = 0
GRAPH_LAUNCH_NO_K_JUMP = 1
GRAPH_LAUNCH_ONLY_K_JUMP = 2
GRAPH_LAUNCH_ALWAYS = GRAPH_LAUNCH_NO_K_JUMP | GRAPH_LAUNCH_ONLY_K_JUMP

latest_daily = True
write_base_stats = True
run_weekly_check = False
force_stats = False
show_all_goals = False
unlimited_stretch_goals = False
print_yearly_pace = False
see_silly_max = False

daily = "c:/writing/daily"
daily_proc = "c:/writing/daily/to-proc"
daily_done = "c:/writing/daily/done"

my_daily_dir = daily

stats_file = "c:/writing/temp/daily-stats.txt"
old_stats_file = "c:/writing/temp/daily-stats.txt"
information_file = "c:/writing/scripts/2dyinfo.txt"

file_header = ""

color_deltas = defaultdict(list)
color_dict = defaultdict(int)
sect_ary = []

files_back_wanted = 1
verbose = False
use_proc_dir = True

my_sections_file = "c:/writing/scripts/2dy.txt"

default_weight = .5

def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def latest_editable(my_file):
    temp = os.path.split(my_file)
    proc_pos = os.path.abspath(os.path.join(temp[0], 'to-proc', temp[1]))
    print(proc_pos)
    if os.path.exists(proc_pos):
        return proc_pos
    return my_file

def open_editable(my_file):
    mt.npo(latest_editable(my_file))

def see_back(this_file = d, my_dir = ".", days_back = max_days_new):
    my_file = this_file.subtract(days=days_back).format('YYYYMMDD') + ".txt"
    return os.path.join(my_dir, my_file)

def digits_only(my_string):
    return int(re.sub("[^0-9]", "", my_string))

def open_latest_daily_from_glob(arg):
    file_wildcard = "2*" + arg + ".txt"
    g = glob.glob(os.path.join(daily_proc, file_wildcard))
    if len(g) == 0:
        sys.exit("No dailies in the glob {}.".format(file_wildcard))
    mt.npo(g[-1])

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

def num_to_text_color(my_num, goal_per_file, deltas='basic'):
    if deltas not in color_deltas:
        print("Unrecognized color_delta {}, going to default. You can choose from {}.".format(', '.join(color_deltas[deltas])))
        deltas = 'basic'
    cd = color_deltas[deltas]
    retval = colorama.Back.WHITE
    if my_num <= 0:
        retval += colorama.Back.RED
    elif my_num < goal_per_file // cd[0]: # we could say goal_per_file // 168 as goal_per_hour but decimal precision etc.
        retval += colorama.Fore.RED
    elif my_num < goal_per_file // cd[1]: # breakeven goal
        retval += colorama.Fore.YELLOW
    elif my_num < goal_per_file // cd[2]:
        retval += colorama.Fore.BLACK
    elif my_num < goal_per_file // cd[3]:
        retval += colorama.Fore.GREEN
    elif my_num < goal_per_file // cd[4]:
        retval += colorama.Fore.BLUE
    elif my_num < goal_per_file // cd[5]:
        retval += colorama.Fore.CYAN
    else:
        retval += colorama.Fore.MAGENTA
    return retval

def date_match(line_1, line_2):
    try:
        d1 = line_1.split("\t")
        d2 = line_2.split("\t")
    except:
        print("Bad line formatting when checking date_match")
        print(line_1)
        print(line_2)
        sys.exit()
    return d1[0] == d2[0] and d1[1][:10] == d2[1][:10] # we may need to tighten this up later e.g. x.replace('-', '')[:8], but the dates have dashes for now

def compare_thousands(my_dir = "c:/writing/daily", bail = True, this_file = "", file_index = -1, overwrite = False):
    os.chdir(my_dir)
    if not this_file:
        g = glob.glob(my_dir + "/" + glob_string)
        this_file = os.path.basename(g[file_index])
    my_size = os.stat(this_file).st_size

    os.chdir(my_dir)
    f = open(stats_file, "r")
    raw_stat_lines = mt.filelines_no_comments(f)
    f.close()

    ary = raw_stat_lines[-1].split("\t")
    last_size = int(ary[-1])

    todays_points = [ x for x in raw_stat_lines if date_match(x, raw_stat_lines[-1]) ]
    todays_min = int(todays_points[0].split("\t")[2])

    hour_delta = my_size - last_size
    header_color = num_to_text_color(hour_delta, goals_and_stretch[0])
    my_string = header_color + "HOURLY BYTE/THOUSANDS NOW/BEFORE COUNT: {} vs {}, {} vs {}, +{}.".format(my_size, last_size, my_size // 1000, last_size // 1000, my_size - last_size) + colorama.Style.RESET_ALL
    mt.center(my_string)
    thousands = my_size // 1000 - last_size // 1000
    until_next = (1000 - (my_size % 1000))
    right_now = pendulum.now()
    minutes_adjusted = (right_now.minute + 57) % 60

    seconds_taken_this_hour = minutes_adjusted * 60 + right_now.second
    seconds_remaining_this_hour = 3600 - seconds_taken_this_hour

    day_start = right_now.set(minute=3, second=0, hour=0)
    if day_start >= right_now:
        day_start = day_start.subtract(days=1)

    seconds_taken_today = (right_now - day_start).in_seconds()

    try:
        projected_hourly = (my_size - last_size) * 3600 / seconds_taken_this_hour
        header_color = num_to_text_color(projected_hourly, goals_and_stretch[0])
        my_string = header_color + "Projected bytes this hour: {:.2f}".format(projected_hourly) + colorama.Style.RESET_ALL
        mt.center(my_string)
        projected_daily = (my_size - todays_min) * 86400 / seconds_taken_today
        header_color = num_to_text_color(projected_daily, goals_and_stretch[0], 'daily')
        my_string = header_color + "Projected bytes today: {} + {:.2f} = {:.2f}".format(todays_min, projected_daily, todays_min + projected_daily) + colorama.Style.RESET_ALL
        mt.center(my_string)
    except:
        print("Oops! Synchronicity. There are no projections to make for this hour.")

    try:
        rate_for_next = until_next * 60 / seconds_remaining_this_hour
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

def check_yearly_pace():
    total_bytes = 0
    pnow = pendulum.now()
    year_start = pendulum.now().set(month=1,day=1,hour=0,minute=0,second=0)
    year_end = year_start.add(years=1)
    cut_off_last_file = year_end.subtract(days=7)
    this_years_last_file = cut_off_last_file.format("YYYYMMDD") + ".txt"
    year_seconds = (year_end-year_start).in_seconds()
    seconds_delta = (pnow - year_start).in_seconds()
    this_year = pnow.year
    last_year = pnow.year - 1
    os.chdir("c:/writing/daily")
    g = glob.glob("{}*.txt".format(this_year))
    for f in g:
        this_file_bytes = os.stat(f).st_size
        total_bytes += this_file_bytes
        if verbose:
            print(f, "adds", this_file_bytes)
    print(total_bytes, "total bytes")
    print(total_bytes * year_seconds // seconds_delta, "projected yearly bytes")
    if g[-1] < this_years_last_file:
        g0 = glob.glob("{}*.txt".format(last_year))
        this_file_bytes = os.stat(g0[-1]).st_size
        print(colorama.Fore.GREEN + "Adding last year's last-file: {}, {} bytes".format(g0[-1], this_file_bytes) + colorama.Style.RESET_ALL)
        total_bytes += this_file_bytes
        print(total_bytes, "total bytes")
        print(total_bytes * year_seconds // seconds_delta, "projected yearly bytes including last file")
    sys.exit()

def dhms(my_int):
    my_int = abs(my_int)
    return '{:02d}d{:02d}h{:02d}m{:02d}s'.format(my_int // 86400, (my_int // 3600) % 24, (my_int // 60) % 60, my_int % 60)

def check_weekly_rate(my_dir = "c:/writing/daily", bail = True, this_file = "", file_index = -1, overwrite = False):
    os.chdir(my_dir)
    hit_all_stretch = False
    if not this_file:
        g = glob.glob(my_dir + "/" + glob_string)
        this_file = os.path.basename(g[file_index])
    current_size = os.stat(this_file).st_size
    gsl = len(goals_and_stretch)
    stretch_metric_goal = basic_goal = goals_and_stretch[0]
    for x in range(0, gsl):
        stretch_metric_goal = goal_per_file = goals_and_stretch[x]
        if current_size >= goals_and_stretch[x]:
            init_bit = colorama.Back.YELLOW + colorama.Fore.BLACK + 'Hooray! You hit'
            mt.center('{} {} of {}!'.format(init_bit, 'your weekly goal' if x == 0 else 'stretch goal # {}{}'.format(x, '' if gsl == 2 else '/{}'.format(gsl-1)), goals_and_stretch[x]) + colorama.Style.RESET_ALL)
        else:
            break
        if x == gsl - 1 and x > 1:
            mt.center(colorama.Back.YELLOW + colorama.Fore.BLACK + "Extra hooray! You hit {} your stretch goals! -x# will add another, or e edits for a temporary goal.".format('all' if x > 2 else 'both') + colorama.Style.RESET_ALL)
            hit_all_stretch = True
    t_base = pendulum.local(int(this_file[:4]), int(this_file[4:6]), int(this_file[6:8])).add(seconds=offset_seconds)
    t_now = pendulum.now()
    t_goal = t_base.add(days=max_days_new)
    weekly_interval_so_far = (t_now - t_base).in_seconds()
    full_weekly_interval = (t_goal - t_base).in_seconds()
    current_goal = stretch_metric_goal * weekly_interval_so_far // full_weekly_interval
    seconds_delta_from_pace = (current_size - current_goal) * full_weekly_interval // basic_goal
    current_pace_seconds_delta = weekly_interval_so_far * basic_goal / current_size
    equivalent_time = t_base.add(seconds = current_size * full_weekly_interval // basic_goal).format("YYYY-MM-DD HH:mm:ss")
    bytes_per_hour_so_far = current_size * 3600 / weekly_interval_so_far
    if hit_all_stretch:
        mt.center(colorama.Fore.CYAN + "Total expected bytes this period: {:.2f}".format(bytes_per_hour_so_far * max_days_new * 24) + colorama.Style.RESET_ALL)
        mt.center(colorama.Fore.CYAN + "If you want to establish a new stretch goal, 2dy -e will do so." + colorama.Style.RESET_ALL)
    else:
        cur_time_readable = t_now.format("YYYY-MM-DD HH:mm:ss")
        time_dir_string = 'behind' if current_size < current_goal else 'ahead'
        print(mt.green_red_comp(current_size, current_goal) + "Right now at {} you have {} bytes. To be on pace for {} before creating a file, you need to be at {}, so you're {} by {} right now.".format(cur_time_readable, current_size, stretch_metric_goal, current_goal, time_dir_string, abs(current_goal - current_size)))
        if time_dir_string == 'ahead':
            time_dir_string += ' of'
        print("That equates to {} second(s) {} the break-even time for your production, which is {}, {} away.".format(abs(seconds_delta_from_pace), time_dir_string, equivalent_time, dhms(seconds_delta_from_pace)) + colorama.Style.RESET_ALL)
        projection = current_size * full_weekly_interval // weekly_interval_so_far
        mt.center(colorama.Fore.YELLOW + "Expected end-of-cycle/week goal: {} bytes, {}{} {} your basic goal.".format(projection, '+' if projection > goals_and_stretch[0] else '', abs(projection - basic_goal), 'ahead of' if projection > goals_and_stretch[0] else 'behind') + colorama.Style.RESET_ALL)
    nexty = 'additional ' if hit_all_stretch else ('' if basic_goal == stretch_metric_goal else 'next ')
    post_stretch_goals = []
    high_stretch_goal = goals_and_stretch[-1]
    if unlimited_stretch_goals:
        current_extra_stretch = ((max(current_size, goals_and_stretch[-1]) - stretch_offset) // super_stretch_delta) * super_stretch_delta + stretch_offset
        current_projected_bytes = (current_size * full_weekly_interval) / weekly_interval_so_far
        stretch_special_mod = [ x for x in stretch_special if x > current_projected_bytes ]
        while current_extra_stretch <= current_projected_bytes:
            try:
                if stretch_special_mod[0] < current_extra_stretch:
                    stretch_special_mod.pop(0)
                if stretch_special_mod[0] < current_extra_stretch + super_stretch_delta:
                    post_stretch_goals.append(stretch_special_mod.pop(0))
                    if post_stretch_goals[-1] > current_projected_bytes:
                        break
                    continue
            except:
                pass
            current_extra_stretch += super_stretch_delta
            post_stretch_goals.append(current_extra_stretch)
    elif current_size > goals_and_stretch[-1]:
        post_stretch_goals = [ ((current_size // super_stretch_delta) + 1) * super_stretch_delta ]
    if not hit_all_stretch and not show_all_goals:
        goal_array = [ basic_goal ] if stretch_metric_goal == basic_goal else [ x for x in goals_and_stretch if x > current_size ]
    else:
        goal_array = [ x for x in goals_and_stretch if x > current_size ]
    if post_stretch_max and len(post_stretch_goals) > post_stretch_max:
        print("Truncating upper bounds to the top {} entr{} of {}.".format(post_stretch_max, mt.plur(post_stretch_max, [ 'ies', 'y' ]), len(post_stretch_goals)))
        post_stretch_goals = post_stretch_goals[-post_stretch_max:]
    goal_array.extend(post_stretch_goals)
    prev_goal = 0
    for this_goal in goal_array:
        if see_silly_max:
            current_size = this_goal - 1
            bytes_per_hour_so_far = current_size * 3600 / weekly_interval_so_far
        if prev_goal > 0 and super_stretch_delta > 0 and this_goal - prev_goal > super_stretch_delta:
            mt.center('=' * 80)
        elif prev_goal == high_stretch_goal:
            mt.center('~' * 80)
        current_pace_seconds_delta = weekly_interval_so_far * this_goal / current_size
        t_eta = t_base.add(seconds = current_pace_seconds_delta)
        seconds_remaining = full_weekly_interval - weekly_interval_so_far
        bytes_remaining = this_goal - current_size
        bytes_per_hour_to_go = bytes_remaining * 3600 / seconds_remaining
        bytes_per_hour_overall = this_goal * 3600 / full_weekly_interval
        t_pace_eta = t_now.add(seconds = (this_goal - current_size) * 3600 / bytes_per_hour_overall)
        mt.center(colorama.Fore.YELLOW + "For the {}goal of {}: ETA (current pace) {}, {} away, ETA (baseline pace) {}, {} away.".format(nexty, this_goal, t_eta.format("YYYY-MM-DD HH:mm:ss"), dhms((t_eta - t_now).in_seconds()), t_pace_eta.format("YYYY-MM-DD HH:mm:ss"), dhms((t_pace_eta - t_now).in_seconds())) + colorama.Style.RESET_ALL)
        so_far_pct = bytes_per_hour_so_far * 100 / bytes_per_hour_overall
        to_go_pct = bytes_per_hour_to_go * 100 / bytes_per_hour_overall
        catchup_ratio = bytes_per_hour_to_go / bytes_per_hour_so_far if bytes_per_hour_to_go > bytes_per_hour_so_far else bytes_per_hour_so_far / bytes_per_hour_to_go
        catchup_inverse = 1 / catchup_ratio
        now_breakeven = this_goal * weekly_interval_so_far / full_weekly_interval
        raw_plus_minus = current_size - now_breakeven
        prev_goal = this_goal
        mt.center(colorama.Fore.CYAN + "Bytes per hour to hit end-of-week goal: {:.2f} {:.2f}%. Bytes for exact pace: {:.2f}. Bytes done so far: {:.2f} {:.2f}% ({}{}{:.2f}{}). Catchup ratio: {}{:.3f}/{:.3f}.".format(bytes_per_hour_to_go, to_go_pct,
          bytes_per_hour_overall,
          bytes_per_hour_so_far, so_far_pct,
          mt.green_red_comp(current_size, now_breakeven), '+' if raw_plus_minus > 0 else '', raw_plus_minus, colorama.Fore.CYAN,
          mt.green_red_comp(bytes_per_hour_so_far, bytes_per_hour_to_go), catchup_ratio, catchup_inverse) + colorama.Style.RESET_ALL)
    if bail:
        sys.exit()

def graph_stats(my_dir = "c:/writing/daily", bail = True, this_file = "", file_index = -1, overwrite = False, launch_present = GRAPH_LAUNCH_NEVER, graph_type = TOTAL_BYTES, weight = .5, floor_hourly = 0, temp_file = False, data_back = 0):
    data_back = abs(data_back)
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

    datetime_strings = []
    times = []
    sizes = []
    color_array = []
    shape_array = []

    current_size = os.stat(this_file).st_size

    if not len(relevant_stats):
        sys.exit("No relevant stats yet. You must have tried to graph things at the start of the week.")
        if bail:
            sys.exit()
        return

    if len(relevant_stats) == 1:
        print("Not enough relevant stats for a graph yet. You must have tried to graph things at the start of the week.")
        if bail:
            sys.exit()
        return

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
        datetime_strings.append(my_time)
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
            print("WARNING line", ' / '.join(ary), "has duplicate hour. Minutes are {} vs {}. You probably ran a test twice. It'd be best to delete it.\n    Run 2dy.py es/ed to do so.".format(last_time.minute, my_time.minute))
        elif my_time.hour - last_time.hour > 1:
            print("WARNING line", ' / '.join(ary), "skipped at least one hour. You probably deleted data. It's not a big deal, but O Lost and all that sort of thing.\n    Run 2dy.py es/ed to see the line.".format(last_time.minute, my_time.minute))
        last_time = my_time

    init_from_epoch = (first_time - pendulum.from_timestamp(0)).total_seconds() / 86400

    if data_back:
        times = times[:-data_back]
        sizes = sizes[:-data_back]
        color_array = color_array[:-data_back]
        shape_array = shape_array[:-data_back]
        datetime_strings = datetime_strings[:-data_back]

    times = np.array(times)
    sizes = np.array(sizes)

    (a, b) = np.polyfit(times, sizes, 1)
    b0 = b + a * init_from_epoch
    #my_label = "{}\nbytes={:.2f}*days({:.2f}*hours){}{:.2f}".format(time_strings[-data_back-1].to_day_datetime_string(), a, a/24, '+' if b0 > 0 else '', b0)

    my_label = "{}\nbytes={:.2f}*days({:.2f}*hours){}{:.2f}".format(datetime_strings[-1].to_day_datetime_string(), a, a/24, '+' if b0 > 0 else '', b0)

    my_graph_graphic = "c:/writing/temp/{}daily-{}{}.png".format('temp-' if temp_file else '', 'past-' if abs(file_index) > 1 else '', datetime_strings[-1].format("YYYY-MM-DD-HH"))

    should_i_launch = False
    final_thousands_delta = sizes[-1] // 1000 - sizes[-2] // 1000

    if not overwrite and os.path.exists(my_graph_graphic):
        print(my_graph_graphic, "already exists. I am not overwriting it. Use the -gso flag or specify files back, e.g. gs1 to override this reject.{}".format("" if launch_present else " -gsl launches."))
        if launch_present and TOTAL_BYTES:
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
        expected_kb = (current_size - first_size) * 86400 * max_days_new / (last_time - first_time).total_seconds() + first_size
        my_label += "\nAverage from last exp bytes: {:.2f}".format(expected_kb)

    if a:
        my_label += "\nBest-fit exp bytes: {:.2f} end/{:.2f} now".format(7 * a + b0, times[-1] * a + b)
        my_label += "\nBest-fit projection: {:.2f}".format((7-(times[-1]-times[0])) * a + current_size)

    my_line_width = 1

    plt.figure(figsize=(15, 12))
    plt.xticks(rotation=45, ha='right')
    plt.xlabel("days")
    plt.ylabel("bytes")

    for g in goals_and_stretch:
        per_day = g // max_days_new
        plt.plot(times, per_day * times - per_day * init_from_epoch, linewidth=my_line_width, linestyle='dashed') # general pacing line assuming consistent output
        my_line_width += 0.2
        if sizes[-1] < g:
            break
        plt.axhline(y=g, linestyle='dotted', zorder=10)

    plt.plot(times, a*times+b, linewidth=my_line_width) # line of best fit

    plt.scatter(times, sizes, color = color_array, s = shape_array, label=my_label, zorder=20) # not sure which zorder is which, but make sure of things. I want the line under the points.

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:00'))
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval = 6 if times[-1] - times[0] < 4 else 12))
    plt.legend(loc='upper left', framealpha=1).set_zorder(300)

    if graph_type & TOTAL_BYTES:
        plt.savefig(my_graph_graphic)
        mt.text_in_browser(my_graph_graphic)

    if not (graph_type & HOURLY_BYTES):
        if bail:
            sys.exit()
        return

    hour_delt = []
    for x in range (0, len(sizes) - 1):
        hour_delt.append(sizes[x+1] - sizes[x])
    hour_delt = np.array(hour_delt)


    diffs = []
    for x in range(0, len(sizes) - 1):
        diffs.append(sizes[x+1] - sizes[x])
    diffs = np.array(diffs)
    times2 = np.array(times[1:])

    plt.cla()
    plt.clf()
    plt.figure(figsize=(15, 12))
    plt.xticks(rotation=45, ha='right')
    plt.xlabel("days")
    plt.ylabel("bytes")

    (a, b) = np.polyfit(times2, hour_delt, 1)
    hourly_average = (sizes[-1] - first_size) * 3600 / (last_time - first_time).total_seconds()

    a1 = a * weight
    b1 = b
    b1 = b * weight - hourly_average * weight + hourly_average
    b2 = b1 + a1 * init_from_epoch

    plt.plot(times2, a1 * times2 + b1, linewidth=my_line_width)

    count = len(times2)
    projection_time = times2[-1]
    more_bytes = 0

    zero_at_end = ( - hourly_average) / (7 * a + a * init_from_epoch + b - hourly_average)
    current_expected = a1 * (count / 24) + b2
    floor_hit_yet = False

    while count < 168:
        projection_time += 1 / 24
        #this_delta = a * projection_time + b
        #this_delta = weight * this_delta + (1 - weight) * hourly_average
        this_delta = a1 * projection_time + b1
        if floor_hourly > 0 and this_delta < floor_hourly:
            this_delta = floor_hourly
            if not floor_hit_yet:
                print("Floor of {} hit at {} of 168.".format(floor_hourly, count + 1))
                floor_hit_yet = True
        elif this_delta <= 0:
            print("Trendline hit zero at {} of 168.".format(count+1))
            break
        more_bytes += this_delta
        print(floor_hourly, this_delta, more_bytes)
        count += 1

    label_2 = "Bytes={:.2f}*days/{:.2f}/hours{}{:.2f}\nTotal expected bytes:{:.2f}+{:.2f}={:.2f}{}".format(a1, a1 / 24, '+' if b2 >= 0 else '-', abs(b2), sizes[-1], more_bytes, sizes[-1] + more_bytes, "\n(trendline hit zero at {})".format(count) if this_delta < 0 else '')

    label_2 += "\nCurrent expected={:.2f}\n".format(current_expected)

    label_2 += "Ratio for zero at end={:.2f}".format(zero_at_end) if zero_at_end > 0 else "Bytes-per-hour has positive uptrend\nNo zero-hour ratio is meaningful"

    #plt.scatter(times2, hour_delt, color = color_array, s = shape_array, label=my_label)
    plt.scatter(times2, hour_delt, label=label_2)

    my_graph_graphic = "c:/writing/temp/daily-delta-{}{}".format('past-' if abs(file_index) > 1 else '', my_time.format("YYYY-MM-DD-HH.png"))

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:00'))
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval = 6 if times[-1] - times[0] < 4 else 12))
    plt.legend(loc='upper left', framealpha=1).set_zorder(300)

    plt.savefig(my_graph_graphic)
    mt.text_in_browser(my_graph_graphic)

    if bail:
        sys.exit()

def put_stats(bail = True, print_on_over = 0, launch_iff_new_k = False, create_graphics = True):
    os.chdir("c:/writing/daily")
    f = open(stats_file, "a")
    ld = mt.last_daily_of()
    pn = pendulum.now()
    if minimum_seconds_between > 0:
        f2 = open(stats_file, "r")
        my_stuff = mt.filelines_no_comments(f2)
        try:
            last_time = pendulum.parse(my_stuff[-1].split("\t")[1])
            cur_diff = pn.diff(last_time).in_seconds()
        except:
            print("No readable data in {}, so I can't check if it's being run too soon. It probably isn't.".format(stats_file))
        if cur_diff < minimum_seconds_between and not force_stats and (ld == my_stuff[-1].split("\t")[1]):
            print("It's been too soon since the last time I looked at the daily file size. {} seconds and minimum is {}. Use -fs to override this.".format(cur_diff, minimum_seconds_between))
            if bail:
                sys.exit()
            return
    out_string = "{}\t{}\t{}".format(ld, pn, os.stat(ld).st_size)
    f.write(out_string + "\n")
    f.close()
    if not create_graphics:
        return

    if launch_iff_new_k:
        f = open(stats_file)
        ary = mt.filelines_no_comments(f)
        f.close()
        before_last_bytes = int(ary[-2].split("\t")[2]) // 1000
        last_bytes = int(ary[-1].split("\t")[2]) // 1000
        byte_delta = last_bytes - before_last_bytes
        if byte_delta:
            print("Thousands-floor increased from {} to {}, so I am opening a new graph".format(before_last_bytes, last_bytes))
            graph_stats(bail = bail)
        else:
            print("Thousands-floor stayed constant at {}, so I am not going to create a new graph".format(last_bytes))
    else:
        print("Forcing launch of graphics file.")
        graph_stats()

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

    threshold = see_back(d, '', max_days_new)
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

def stat_sort():
    f = open(stats_file)
    raw_stat_lines = f.readlines()
    last_bump_up = final_index = 0
    for x in range(0, len(raw_stat_lines)):
        if raw_stat_lines[x].startswith('#'):
            continue
        if raw_stat_lines[x].startswith(';'):
            final_index = x
            break;
        ary = x.split('\t')
    f.close()
    if not last_bump_up:
        print("Nothing to shuffle over.")

def usage(param = 'Cmd line usage'):
    print(param)
    print('=' * 50)
    print("(-?)f (#) = # files back (or # without f)")
    print("(-?)m (#) = # max days back")
    print("single number = wildcard to search e.g. 0726, g=# g# #k sets goals at # thousand")
    print("(-?)mn/n/nm (#) = # max new days back")
    print("(-?)l or ln/nl = latest-daily (or not)")
    print("(-?)v or vn/nv = toggle verbosity")
    print("(-?)p/tp = move to to_proc, tk/kt and dt/td to keep/drive")
    print("(-?)ps = put stats, (-?)gs = get stats, (-?)es/ed = edit stats/data, (-?)ss = sift stats")
    print("(-)e = edit 2dy.txt to add sections or usage or adjust days_new. ec/em = edit code, es/ed = edit stats")
    print("(-)ct(o) checks thousands, (-)wr(o) checks weekly writing goals based on current document size. O = only do this")
    sys.exit()

def poss_thousands(my_int):
    try:
        my_int = int(my_int)
        if my_int < 1000:
            return my_int * 1000
        return my_int
    except:
        print("Uh oh", my_int, "should have been an integer.")
        return 0

def poss_thousands_list(my_string, sort_list = True):
    my_list = [ poss_thousands(x) for x in my_string.split(',') ]
    if sort_list:
        my_list = sorted(my_list)
    return my_list

def read_2dy_cfg():
    global sect_ary
    global file_header
    global goal_per_file
    global max_days_new
    global min_days_new
    global glob_string
    global file_header
    global color_dict
    global minimum_seconds_between
    global goals_and_stretch
    global stretch_offset
    global stretch_special
    this_weeks_goal = []
    temp_glob = []
    adjust_color_dict = False
    with open(my_sections_file) as file:
        for (line_count, line) in enumerate(file, 1):
            if line.startswith("#"): continue
            if line.startswith(";"): break
            (prefix, data) = mt.cfg_data_split(line)
            if prefix == 'color_deltas':
                my_ary = data.split(',')
                try:
                    color_deltas[my_ary[0]] = [int(x) for x in my_ary[1:]]
                except:
                    print("Oops. The color-deltas array {} needs integers after the name.".format(', '.join(my_ary[1:])))
            elif prefix == 'goalperfile':
                goals_and_stretch = poss_thousands_list(data)
            elif prefix == 'maxnew':
                max_days_new = int(data)
            elif prefix == 'maxback':
                min_days_new = int(data)
            elif prefix == 'minimum_seconds_between':
                minimum_seconds_between = int(data)
            elif prefix == 'glob':
                glob_string = data
                if not glob_string.endswith(".txt"):
                    if glob_string.startswith("!"):
                        glob_string = data[1:]
                        print("! at beginning of line blocks adding .txt to file.")
                    else:
                        print("Tacking on .txt to glob in {} at line {}. Run with -e to add .txt.".format(my_sections_file, line_count))
                        glob_string += '.txt'
            elif prefix == 'file_header':
                file_header += data.replace("\\", "\n") + "\n"
            elif prefix in ( 'color', 'colors' ):
                color_dict = mt.quick_dict_from_line(line, use_ints = True)
            elif prefix in ( 'colorrel', 'colorsrel' ):
                color_dict = mt.quick_dict_from_line(line, use_floats = True)
                adjust_color_dict = True
            elif prefix in ( 'defaults', 'sect', 'section', 'sections' ):
                sect_dict = mt.quick_dict_from_line(line)
                if len(sect_ary):
                    print("Adding to non-blank sections array on line {}".format(line_count))
                sect_ary.extend(sect_dict)
            elif prefix in ( 'offset_seconds', 'seconds_offset' ):
                offset_seconds = int(data)
            elif prefix in ( 'stretch_delta', 'super_stretch_delta' ):
                super_stretch_delta = int(data)
            elif prefix in ( 'stretch_offset', 'offset_stretch' ):
                stretch_offset = int(data)
            elif prefix in ( 'stretch_special', 'special_stretch' ):
                stretch_special = poss_thousands_list(data)
            elif prefix in ( 'post_stretch_max' ):
                post_stretch_max = int(data)
            elif prefix.isdigit():
                if len(prefix) != 8:
                    print("WARNING suggested weekly file has wrong # of digits (should be 8) at line {}.".format(line_count))
                    continue
                file_name = prefix + ".txt"
                if not len(temp_glob):
                    temp_glob = glob.glob("c:/writing/daily/20*.txt")
                if file_name != os.path.basename(temp_glob[-1]):
                    print("WARNING line {} has outdated custom goal {}. Comment it out or delete it.".format(line_count, file_name))
                else:
                    this_weeks_goal = poss_thousands_list(data)
            else:
                print("WARNING", my_sections_file, "line", line_count, "unrecognized data", line.strip())
    if adjust_color_dict:
        for x in color_dict:
            if color_dict[x] < 0:
                continue
            color_dict[x] = goals_and_stretch[0] * color_dict[x] / 168
    if len(this_weeks_goal) > 0:
        goals_and_stretch.extend(this_weeks_goal)
        old_goals = list(goals_and_stretch)
        goals_and_stretch = sorted(goals_and_stretch)
        if old_goals != goals_and_stretch:
            print("NOTE: resorted goals array because custom this-week goals made it non-increasing.")
    if len(sect_ary) == 0:
        print("WARNING", my_sections_file, "has no default sections.")

def weekly_compare(files_back = 1):
    if files_back < 1:
        sys.exit("Weekly compare needs 1+ as an index for looking back.")
    x = glob.glob(daily_proc + "/20*.txt")
    if len(x) < files_back:
        sys.exit("Files back is too large. Maximum is {}.".format(len(x)))
    readable = x[-files_back]
    locked = os.path.join(daily, os.path.basename(readable))
    mt.wm(readable, locked)
    sys.exit()

def create_new_file(my_file, launch = True):
    print("Creating new daily file", my_file)
    f = open(my_file, "w")
    if file_header:
        f.write(file_header)
    for s in sect_ary: f.write("\n\\{:s}\n".format(s))
    f.close()
    if write_base_stats and my_daily_dir == daily:
        put_stats(bail = False, create_graphics = False)
    if launch: mt.npo(my_file, bail=False)

#
# main coding block
#
# todo: look on command line

os.chdir("c:/writing/scripts")

cmd_count = 1

read_2dy_cfg()

while cmd_count < len(sys.argv):
    rawarg = sys.argv[cmd_count]
    (arg, num, valid_num) = mt.parnum(sys.argv[cmd_count], allow_float = True)
    if arg == 'f':
        files_back_wanted = num
        latest_daily = False
    elif arg == 'm' and arg[1:].isdigit():
        max_days_back = num
        latest_daily = False
    elif arg in ( 'mn', 'nm' ):
        max_days_new = num
        latest_daily = False
    elif arg[:2] == 'ms':
        minimum_seconds_between = num
    elif arg == 'l': latest_daily = True
    elif arg in ( 'nl', 'ln' ): latest_daily = False
    elif arg == 'v': verbose = True
    elif arg in ( 'nv', 'vn' ): verbose = False
    elif arg in ( 'ag', 'ga' ):
        show_all_goals = True
    elif mt.alfmatch( arg, 'agn' ):
        show_all_goals = False
    elif arg in ( 'e', 'es' ):
        if arg == 'es':
            print(colorama.Fore.GREEN + "NOTE: if you wanted to edit the stats file, try ED instead." + colorama.Style.RESET_ALL)
        mt.npo(my_sections_file)
    elif arg in ( 'em', 'ec', 'ce', 'me' ): mt.npo(__file__)
    elif arg in ( 'ei', 'ie' ): mt.npo(information_file)
    elif mt.alpha_match('eit', arg) or arg in ( 'et', 'te' ):
        mt.eq_print("text of information file (edit with ie/ei)", equals_width = 20, color_info = colorama.Fore.YELLOW)
        os.system("type {}".format(os.path.normpath(information_file)))
        sys.exit()
    elif arg == 'eo': mt.npo(old_stats_file)
    elif arg in ( 'es', 'ed' ):
        mt.npo(stats_file)
    elif arg == 'fs': force_stats = True
    elif arg in ( 'p', 'tp', 'pt', 't'): move_to_proc()
    elif arg == 'x' and valid_num:
        if num < 1000:
            num *= 1000
        goals_and_stretch.append(num)
        if num < goals_and_stretch[-2]:
            mt.centcol("NOTE: I am re-sorting, since the number you supplied was less than the current maximum stretch goal of {}.{}".format(goals_and_stretch[-2], '' if num > goals_and_stretch[0] else ' In fact, it is less than the low-end goal of {}.'.format(goals_and_stretch[0])), color_string = colorama.Fore.YELLOW)
            goals_and_stretch = sorted(goals_and_stretch)
        run_weekly_check = True
        weekly_bail = True
    elif arg == 'wc':
        try:
            weekly_compare(int(arg[2:]))
        except:
            print("No number after wc. Assuming 1.")
            weekly_compare(1)
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
    elif arg.startswith('g=') or (arg.startswith('g') and arg[1:].isdigit()) or (arg.endswith('k') and arg[:-1].isdigit()):
        if 1:
            goal_per_file = 1000 * int(digits_only(arg))
        else:
            sys.exit("You need a number after g/g= or before k.")
    elif arg == 'gs':
        file_index = num
        if file_index == 0:
            if valid_num:
                print("Note: 2dy.py graphing indices are not zero-based. Rather, they stat at 1, or -1, as the most recent (element -1 in an array). So I am setting the index to -1/1.")
            file_index = -1
        graph_stats(file_index = file_index, overwrite = False)
    elif arg == 'gsd': graph_stats(graph_type = HOURLY_BYTES)
    elif arg[:3] == 'gsd':
        my_floor = 0
        if 'w' in arg[3:]:
            my_ary = arg.split('f')
            try:
                my_floor = int(my_ary[1])
            except:
                sys.exit("gsd/f(floor) requires a number after.")
            arg = my_ary[0]
        if isfloat(arg[3:]):
            my_float = float(arg[3:])
            if my_float > 100:
                print("ASSUMING float > 100 is actually an integer for floor hourly production.")
                my_floor = int(my_float)
                my_weight = default_weight
            else:
                my_weight = my_float
            graph_stats(graph_type = HOURLY_BYTES, weight = my_weight, floor_hourly = my_floor)
        else:
            graph_stats(graph_type = HOURLY_BYTES, floor_hourly = my_floor)
    elif arg == 'gsb': graph_stats(graph_type = HOURLY_BYTES)
    elif arg[:3] == 'gsd':
        if isfloat(arg[3:]):
            graph_stats(graph_type = HOURLY_BYTES | TOTAL_BYTES, weight = float(arg[3:]))
        else:
            graph_stats(graph_type = HOURLY_BYTES | TOTAL_BYTES)
    elif arg == 'gsd': graph_stats(overwrite = True, launch_present = GRAPH_LAUNCH_NO_K_JUMP) # this is for daily launches
    elif arg == 'gsh':
        graph_stats(overwrite = False, launch_present = GRAPH_LAUNCH_ALWAYS, data_back = num)
    elif arg == 'gsl': graph_stats(overwrite = True, launch_present = GRAPH_LAUNCH_ALWAYS)
    elif arg == 'gso': graph_stats(overwrite = True)
    elif arg == 'gst': graph_stats(overwrite = True, temp_file = True)
    elif arg == 'gsu': graph_stats(overwrite = False)
    elif arg == 'ps':
        if num:
            put_stats(print_on_over = int(arg[2:]))
        else:
            put_stats()
    elif arg == 'psr': put_stats(launch_iff_new_k = True)
    elif arg == 'psf': put_stats(launch_iff_new_k = False)
    elif arg == 'bs': write_base_stats = False
    elif arg == 'us': unlimited_stretch_goals = True
    elif rawarg[:3] == 'ss=':
        stretch_special = poss_thousands_list(rawarg[3:])
    elif rawarg[:3] == 'ss+':
        stretch_special.extend(poss_thousands_list(rawarg[3:]))
        stretch_special = sorted(stretch_special)
    elif arg == 'ss': stat_sort()
    elif arg in ( 'gk', 'kg' ): my_daily_dir = "c:/coding/perl/proj/from_keep"
    elif arg in ( 'gd', 'dg' ): my_daily_dir = "c:/coding/perl/proj/from_drive"
    elif arg in ( 'tk', 'kt' ): move_to_proc("c:/coding/perl/proj/from_keep")
    elif arg in ( 'td', 'dt' ): move_to_proc("c:/coding/perl/proj/from_drive")
    elif re.match('[0-9]{3}', arg): # if this causes problems, use [0-1][0-9]{3} or [0-9]{5}
        open_latest_daily_from_glob(arg)
    elif arg.isdigit(): # this should be at the end since we have other digit wildcard checks
        files_back_wanted = int(arg)
        latest_daily = False
    elif arg in ( 'py', 'yp' ):
        print_yearly_pace = True
    elif arg == 'so':
        if num < 50:
            num *= 1000
        stretch_offset = num
    elif arg == 'ssm':
        see_silly_max = True
    elif arg == '?': usage()
    else: usage("Bad parameter {:s}".format(arg))
    cmd_count += 1

if print_yearly_pace:
    check_yearly_pace()

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
            sys.exit()
        if os.path.exists(day_done_file): found_done_file = day_done_file
    if found_done_file: sys.exit("Found {:s} in done folder. Not opening new one.")
    print("Looking back", max_days_new, "days, daily file not found.")
    create_new_file(see_back(d, my_daily_dir, 0))
    sys.exit()

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
        open_editable(day_file)
        sys.exit()

print("Failed to get a file in the last", max_days_back, "every 6 hours")

