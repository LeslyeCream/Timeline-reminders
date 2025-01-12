from icalendar import Calendar, Event
from dateutil import parser
from functools import wraps
from pathlib import Path
import functools
import datetime
import functools
import timeit
import re


# ::::: SETTINGS :::::
default_template = f"```timeline-labeled\n[line-3, body-1]\n"
vault = "/storage/emulated/0/Documents/Obsidian/Calendar"
timeline_file = "/storage/emulated/0/Documents/Obsidian/Calendar/Calendar.md"
ical_file = "/storage/emulated/0/Documents/Obsidian/Calendar/.Calendar.ics"
main_yaml_key = "Reminder"
reverse_sort = False
show_expired_dates = True
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
  "Default": "`", # if you want change but don't delete this value
  "Birthdays": "#",
  "Anniversaries": "##"
}
# ====================================


# ::::: VARIABLES :::::
date_regex = f"(?<={main_yaml_key}\:\s).*" #TO-DO | Improve this
repeat_regex = r"(?<=Repeat\:\s)\d+"
priority_regex = r"(?<=Priority\:\s)[1-6]"
style_regex = r"(?<=Style\:\s).*"
thumb_regex = r"\!\[+?.*(\.jpg|png|heic|webp|jpeg)(\]+|\))"
default_format_date = "%Y-%m-%d"
today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)
this_week = today + datetime.timedelta(days=7)
this_year = datetime.datetime(today.year, 12, 31).date()
dates_dict = {}
ical_events = []
timeline = {
  "Expired": [],
  "Today": [],
  "Tomorrow": [],
  "This week": []
}
logs = []
# ====================================


# ::::::HANDLE ERRORS :::::
def try_log(func):
  @wraps(func)
  def wrapper(*args, **kwargs):
    try:
      args = func(*args, **kwargs)
      return args
    except Exception as e:
      error = f"FUNCTION: {func.__name__}\nERROR: {e}"
      logs.append(error)
  return wrapper
# ====================================


# ::::: HANDLE MESSAGES :::::
def handle_msg(**kwargs):
  print(kwargs["sep"] * 20)
  print(kwargs["msg"])
  print(kwargs["sep"] * 20)
# ====================================


# ::::: CHECK LOG :::::
def run_log(*args) -> None:
  if logs != []:
    for log in set(logs):
      handle_msg(msg=log, sep="-")
  else:
    handle_msg(msg=f"Timeline created! 🎉 | {args[0]} notes added", sep="·")
# ====================================


# ::::: HANDLE MESSAGES :::::
def handle_msg(**kwargs):
  print(kwargs["sep"] * 20)
  print(kwargs["msg"])
  print(kwargs["sep"] * 20)
# ====================================


# ::::: DASHBOARD :::::
@try_log
def init_template(**kwargs) -> None:
  with open(timeline_file, kwargs["mode"]) as f:
    f.write(kwargs["content"])
# ====================================


# ::::: GET FILES :::::
@try_log
def get_note_paths() -> list:
  md_files = filter(yaml_files, [path for path in Path(vault).rglob("*.md") if str(path) != timeline_file and not str(path.parent.name).startswith(".")])
  valid_files = list(map(check_metadata , md_files))
  num_notes = len(valid_files)
  return valid_files, num_notes
# ====================================


# ::::: CHECK FORMAT DATE :::::
@try_log
def check_format_date(input_date: str) -> str:
  try:
    formated_date = parser.parse(input_date).strftime(default_format_date)
    return str(formated_date)

  except ValueError as msg_error: # TO-DO | Check later
    print(f"Error: '{input_date}': {msg_error}")
# ====================================


# ::::: ONLY YAML FILES:::::
@try_log
def yaml_files(md_file) -> str:
  with open(md_file, "r") as f:
    if match := re.search(f"{date_regex}", f.read()):
      return md_file
# ====================================


# ::::: STRPTIME :::::
@try_log
def striptime(input_date) -> datetime.date:
  output_date = datetime.datetime.strptime(input_date, default_format_date).date()
  return output_date
# ====================================


# ::::: CHECK REMINDER :::::
@try_log
def check_metadata (path_file: str) -> list:
  with open(path_file, "r") as f:
    content = f.read()
    date_key = re.search(f"{date_regex}", content)
    date_key = check_format_date(date_key.group())

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

  return [path_file, date_key, repeat_key, priority_key, thumb_key, style_key]
# ====================================


# ::::: SEARCH & GET REMINDERS FROM PROPERTIES :::::
@try_log
def get_reminder_details(metadata: list) -> None:
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


# ::::: CHECK PRIORITY AND SET DIR NAMES :::::
@try_log
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
@try_log
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


# ::::: CONCATENATE LIST OF REMINDERS :::::
@try_log
def concatenate_files(files: list) -> list:
  each_day = (i for i in files)
  format_content = "\n\n".join(str(i) for i in each_day)
  return format_content
# ====================================


# ::::: BUILD TIMELINE :::::
@try_log
def build_timeline() -> None: 
  for each_event in sorted(dates_dict, reverse=reverse_sort):
    content_week = [] # needed for to group week dates
    reminder_date = striptime(each_event.strip())

    if simple_mode:
      run_simple_mode(reminder_date, each_event)
      continue

    if reminder_date < today and show_expired_dates:
      timeline["Expired"] = dates_dict[each_event]

    if reminder_date == today:
      timeline["Today"] = dates_dict[each_event]

    elif reminder_date == tomorrow:
      timeline["Tomorrow"] = dates_dict[each_event]

    elif reminder_date < this_week and reminder_date > today:
      day = reminder_date.strftime("%A")
      timeline[day] = dates_dict[each_event]

    elif reminder_date < this_year and reminder_date > this_week:
      day = reminder_date.strftime("%b %d")
      timeline[day] = dates_dict[each_event]

    elif reminder_date > this_year:
      day = reminder_date.strftime("%b %d %Y")
      timeline[day] = dates_dict[each_event]
# ====================================


# ::::: SIMPLE MODE :::::
@try_log
def run_simple_mode(reminder_date: str, each_event: str) -> None:
  if limited_dates == False:
    day = reminder_date.strftime("%b %d %Y")
    timeline[day] = dates_dict[each_event]
 
  else:
    start_date = striptime(dates_rules["Start"])
    end_date = striptime(dates_rules["End"])
    
    specific_dates = []
    if dates_rules.get("Others") != []:
      specific_dates = [datetime.datetime.strptime(i, default_format_date).date() for i in dates_rules.get("Others")]

    if reminder_date >= start_date and reminder_date <= end_date or reminder_date in specific_dates:
      day = reminder_date.strftime("%b %d %Y")
      timeline[day] = dates_dict[each_event]
# ====================================


# ::::: ADD EVENTS - CALENDAR :::::
@try_log
def add_to_ical(ical_events: list) -> None:
  with open(ical_file, "wb+") as f:
    f.write(b"")
  
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

  with open(ical_file, 'ab') as f: # TO-DO | Avoid this twice
    f.write(cal.to_ical())
# ====================================


# ::::: SAVE CHANGES :::::
@try_log
def save_timeline() -> None:
  for date_event, lst_events in timeline.items():
    
    if timeline.get(date_event) != []: # TO-DO | find the right way for this line
      content_date = concatenate_files(lst_events)
      init_template(mode="a", content=f"date: {date_event}\ncontent: {content_date}\n")
# ====================================


# ::::: MAIN :::::
def main() -> None:
  init_template(mode="w", content=default_template)
  
  notes, num_notes = get_note_paths()
  for path_file in notes:
    get_reminder_details(path_file)
  
  build_timeline()
  save_timeline()
  
  if ical_enable:
    add_to_ical(ical_events)

  run_log(num_notes)
# ====================================


if __name__ == "__main__":
  main()