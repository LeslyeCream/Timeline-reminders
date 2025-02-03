from icalendar import Calendar, Event
from dateutil import parser
from functools import wraps
from pathlib import Path
import functools
import datetime
import timeit
import time
import re

# ::::: SETTINGS :::::
default_template = f"```timeline-labeled\n[line-3, body-1]\n"
vault = "/storage/emulated/0/Documents/Obsidian/Calendar"
timeline_file = "/storage/emulated/0/Documents/Obsidian/Calendar/Calendar.md"
ical_file = "/storage/emulated/0/Documents/Obsidian/Calendar/.Calendar.ics"
enable_timeline = True
main_yaml_key = "Reminder"
reverse_sorted = False
expired_dates = True
default_format_date = "%Y-%m-%d"
show_dirnames = True
show_images = True
ical_enable = True
simple_mode = False
limited_dates = False
dates_rules = {
  "Start": "2018-01-01",
  "End": "2018-12-31",
  "Others": ["2024-12-01", "2023-12-31"]
  }
folder_rules = {
  "Default": "`",
  "Birthdays": "#",
  "Anniversaries": "##"
  }
excluded_paths = [timeline_file, ".obsidian", ".trash"]
# ====================================


# ::::: VARIABLES :::::
date_regex = f"(?<={main_yaml_key}\\:\\s).*"
repeat_regex = r"(?<=Repeat\:\s)\d+"
priority_regex = r"(?<=Priority\:\s)[1-6]"
style_regex = r"(?<=Style\:\s).*"
thumb_regex = r"\!\[+?.*(\.jpg|png|heic|webp|jpeg)(\]+|\))"
today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)
this_week = today + datetime.timedelta(days=7)
this_year = datetime.datetime(today.year, 12, 31).date()
dates_dict = {}
ical_events = []
logs = []
num_notes = [0]
# ====================================


# :::::: DECORATOR - HANDLE ERRORS :::::
def watchdog(func):
  @wraps(func)
  def wrapper(*args, **kwargs):
    if func.__name__ != "main":
      try:
        args = func(*args, **kwargs)
        if func.__name__ == "get_notes":
          num_notes[0] = args
        return args
      except Exception as e:
        logs.append(f"FUNCTION: {func.__name__}\nERROR: {e}")
    else:
      start = time.perf_counter()
      args = func(*args, **kwargs)
      end = time.perf_counter()
      if logs:
        output_log = "\n".join(log for log in set(logs))
        handle_msg(msg=output_log, sep="-")
      else:
        sucessful_msg = f"Timeline created! 🎉 | {num_notes[0]} notes added in {end - start:.2f} seconds"
        handle_msg(msg=sucessful_msg, sep="-")
  return wrapper
# ====================================


# ::::: HANDLE MESSAGES :::::
def handle_msg(**kwargs):
  msg = kwargs["msg"]
  sep = kwargs["sep"]
  length = int(len(msg) + 1)
  print(sep * length)
  print(msg)
  print(sep * length)
# ====================================


# ::::: DASHBOARD :::::
@watchdog
def init_template(**kwargs) -> None:
  with open(str(kwargs["file"]), kwargs["mode"]) as f:
    f.write(kwargs["content"])
# ====================================


# ::::: GET FILES & METADATA :::::
@watchdog
def get_notes() -> int:
  handle_msg(msg=f"Searching notes with '{main_yaml_key}' key, please wait...", sep='')
  note_files = (only_yaml_files(path) for path in Path(vault).rglob("*.md") if path.parent.name not in excluded_paths)
  return len([build_yaml_info(note_path) for note_path in note_files if note_path])
# ====================================


# ::::: ONLY YAML FILES:::::
@watchdog
def only_yaml_files(md_file) -> list:
  with open(md_file, "r") as f:
    file_content = f.read()
    if date_key := re.search(f"{date_regex}", file_content):
      return extract_metadata(date_key, file_content, md_file)
# ====================================


# ::::: CHECK REMINDER :::::
@watchdog
def extract_metadata (date_key: str, content: str, md_file: str) -> list:
  date_key = formated_date = str(parser.parse(date_key.group()).strftime(default_format_date))

  if repeat_key := re.search(repeat_regex, content):
    repeat_key = int(repeat_key.group())

  if priority_key := re.search(priority_regex, content):
    priority_key = int(priority_key.group())

  if show_images:
    if thumb_key := re.search(thumb_regex, content):
      thumb_key = thumb_key.group()
    else:
      thumb_key = ""
  else:
    thumb_key = ""

  if style_key := re.search(style_regex, content):
    style_key = str(style_key.group()).replace('"','').strip()
  else:
    style_key = ""

  return [md_file, date_key, repeat_key, priority_key, thumb_key, style_key]
# ====================================


# ::::: SEARCH & GET REMINDERS FROM PROPERTIES :::::
@watchdog
def build_yaml_info(metadata: list) -> None:
  path_file, date_key, repeat_key, priority_key, thumb_key, style_key = metadata[0:7]
  dir_name = path_file.parent.name
  name_file = path_file.stem

  head_dir_name = set_priority_dir(dir_name, show_dirnames, priority_key)

  reminder_date = schedule_old_dates(date_key, repeat_key)
  backlink_name = f"{head_dir_name} - {style_key}[[{name_file}]]{style_key} {thumb_key}"

  if reminder_date in dates_dict:
    dates_dict[reminder_date].append(backlink_name)
  else:
    dates_dict[reminder_date] = [backlink_name]

  if ical_enable:
    ical_events.append([name_file, reminder_date, repeat_key, dir_name])
# ====================================


# ::::: STRPTIME :::::
@watchdog
def striptime(input_date) -> datetime.date:
  output_date = datetime.datetime.strptime(input_date, default_format_date).date()
  return output_date
# ====================================


# ::::: CHECK PRIORITY AND SET DIR NAMES :::::
@watchdog
def set_priority_dir(dir_name, show_dirnames, priority_key) -> str:
  if show_dirnames:
    if priority_key:
      head_dir_name = (f"{'#' * priority_key} {dir_name} \n")
    else:
      if dir_name in folder_rules.keys():
        head_dir_name = f"{folder_rules.get(dir_name)} {dir_name}\n"
      else:
        default = folder_rules.get("Default")
        head_dir_name = (f"{default} {dir_name} {default}\n")

  else: # disabled dir names
    head_dir_name = ""

  return head_dir_name
# ====================================


# ::::: SCHEDULE OLD DATES :::::
@watchdog
def schedule_old_dates(input_date: str, repeat_key: int) -> str:
  reminder = striptime(input_date)

  if reminder >= today:
    return input_date

  elif repeat_key != None:
    while reminder < today:
      reminder += datetime.timedelta(days=repeat_key)
    return str(reminder)

  else:
    return input_date
# ====================================


# ::::: CONCATENATE LIST REMINDERS :::::
@watchdog
def concatenate_files(files: list) -> list:
  each_day = (i for i in files)
  format_content = "\n\n".join(str(i) for i in each_day)
  return format_content
# ====================================


# ::::: BUILD TIMELINE :::::
@watchdog
def build_timeline() -> None:
  global timeline
  timeline = {}
  for each_event in sorted(dates_dict, reverse=reverse_sorted):
    content_week = [] # needed for to group week dates
    reminder_date = striptime(each_event.strip())

    if simple_mode:
      run_simple_mode(reminder_date, each_event)
      continue

    if reminder_date < this_year and reminder_date < today and expired_dates:
      day = reminder_date.strftime("%b %d %Y")
      timeline["Expired"] = dates_dict[each_event] # TO-DO | Fix this
      continue

    elif reminder_date == today:
      timeline["Today"] = dates_dict[each_event]
      continue

    elif reminder_date == tomorrow:
      timeline["Tomorrow"] = dates_dict[each_event]
      continue

    elif reminder_date < this_week and reminder_date > today:
      day = reminder_date.strftime("%A")
      timeline[day] = dates_dict[each_event]
      continue
    
    
    if reminder_date < this_year and reminder_date > this_week:
      day = reminder_date.strftime("%b %d")
      timeline[day] = dates_dict[each_event]
      continue

    if reminder_date > this_year:
      day = reminder_date.strftime("%b %d %Y")
      timeline[day] = dates_dict[each_event]
      continue
    
# ====================================


# ::::: SIMPLE MODE :::::
@watchdog
def run_simple_mode(reminder_date: str, each_event: str) -> None:
  if not limited_dates:
    day = reminder_date.strftime("%b %d %Y")
    timeline[day] = dates_dict[each_event]

  else:
    start_date = striptime(dates_rules["Start"])
    end_date = striptime(dates_rules["End"])

    specific_dates = []
    if dates_rules.get("Others"):
      specific_dates = [datetime.datetime.strptime(i, default_format_date).date() for i in dates_rules.get("Others")]

    if reminder_date >= start_date and reminder_date <= end_date or reminder_date in specific_dates:
      day = reminder_date.strftime("%b %d %Y")
      timeline[day] = dates_dict[each_event]
# ====================================


# ::::: ADD EVENTS - CALENDAR :::::
@watchdog
def add_to_ical(ical_events: list) -> None:
  init_template(file=ical_file, mode="wb+", content=(empty := b""))

  cal = Calendar()

  for file_name, date, repeat, dir_name in ical_events:
    event = Event()
    date_reminder = striptime(date)

    event.add('summary', file_name)
    event.add('dtstart', date_reminder)
    event.add('dtend', date_reminder)
    event.add('description', dir_name)

    if repeat != None:
      event.add('rrule', {'FREQ': 'DAILY', 'INTERVAL': repeat})

    cal.add_component(event)

  init_template(file=ical_file, mode="ab", content=cal.to_ical())
# ====================================


# ::::: SAVE CHANGES :::::
@watchdog
def save_timeline() -> None:
  timeline_complete = ""
  for date_event, lst_events in timeline.items():
    content_date = concatenate_files(lst_events)
    timeline_complete += f"date: {date_event}\ncontent: {content_date}\n"

  init_template(file=timeline_file, mode="a", content=timeline_complete)
# ====================================


# ::::: MAIN :::::
@watchdog
def main() -> None:
  init_template(file=timeline_file, mode="w", content=default_template)

  get_notes()
  build_timeline()
  if enable_timeline:
  	save_timeline()

  if ical_enable and not simple_mode:
     add_to_ical(ical_events)
# ====================================


if __name__ == "__main__":
  main()