from icalendar import Calendar, Event
from dateutil import parser
from functools import wraps
from pathlib import Path
import subprocess
import functools
import datetime
import time
import re


# ::::: SETTINGS :::::
default_timeline = f"```timeline-labeled\n[line-3, body-1]\n"
vault = "/storage/emulated/0/Documents/.Obsidian/Calendar"
timeline_file = "/storage/emulated/0/Documents/.Obsidian/Calendar/Calendar.md"
ical_file = "/storage/emulated/0/Documents/.Obsidian/Calendar/.Calendar.ics"
enable_timeline = True
main_yaml_key = "Reminder"
descending_sort = False
expired_dates = True
default_format_date = "%Y-%m-%d"
show_dirnames = True
show_images = True
ical_enable = True
simple_mode = False
limited_dates = False
dates_rules = {
  "Start": "2025-02-01",
  "End": "2025-02-28",
  "Others": []
  }
folder_rules = {
  "Default": "`",
  "Birthdays": "#",
  "Anniversaries": "##"
  }
excluded_paths = [timeline_file, ".obsidian", ".trash"]
# ====================================


# ::::: CONSTANTS :::::
TODAY = datetime.date.today()
TOMORROW = TODAY + datetime.timedelta(days=1)
THIS_WEEK = TODAY + datetime.timedelta(days=7)
THIS_YEAR = datetime.datetime(TODAY.year, 12, 31).date()
DATE_REGEX = re.compile(f"(?<={main_yaml_key}\\:\\s)\\d+\\-\\d+\\-\\d+")
REPEAT_REGEX = re.compile(r"(?<=Repeat\:\s)\d+")
PRIORITY_REGEX = re.compile(r"(?<=Priority\:\s)[1-6]")
STYLE_REGEX = re.compile(r'(?<=Style\:\s).+(?=\")')
THUMB_REGEX = re.compile(r"\!\[+?.*(\.jpg|png|heic|webp|jpeg)(\]+|\))")

# ====================================


# :::::: DECORATOR :::::
def watchdog(func):
  @wraps(func)
  def wrapper(*args, **kwargs):
    try:
      logs = []
      start = time.perf_counter()
      num_notes = func(*args, **kwargs)
      end = time.perf_counter()
    except Exception as e:
      logs.append(f"ERROR: {e}")
    subprocess.run("clear")
    if not logs:
      sucessful_msg = f"Timeline created! 🎉 | {num_notes} {"notes" if simple_mode else "reminders"} added in {end - start:.1f} seconds"
      show_message(msg=sucessful_msg)
    else:
      show_message(msg="\n".join([log for log in logs]), sep="/")
  return wrapper
# ====================================


# ::::: SHOW MESSAGES :::::
def show_message(msg: str, sep="-") -> None:
  line = f"{sep * int(len(msg) + 1)}"
  print(f"{line}\n{msg}\n{line}")
# ====================================


# ::::: INIT TEMPLATE :::::
def init_template(**kwargs) -> None:
  with open(str(kwargs["file"]), kwargs["mode"]) as f:
    f.write(kwargs["content"])
# ====================================


# ::::: GET INFO FILES :::::
def get_info_files() -> dict:
  return format_reminders(filter(None, (filter_yaml_files(path) for path in Path(vault).rglob("*.md") if not path.parent.name in excluded_paths)))
# ====================================


# ::::: ONLY YAML FILES:::::
def filter_yaml_files(path_file) -> object:  # TO-DO | Find the right term
  with open(path_file, "r") as file:
    yaml_block = "".join(line for line in file.readlines()[1:10])

    if main_date := DATE_REGEX.search(yaml_block):
      date_key = parser.parse(main_date.group()).strftime(default_format_date)

      repeat_key = 0 if not (repeat_match := REPEAT_REGEX.search(yaml_block)) else int(repeat_match.group())
      priority_key = None if not (priority_match := PRIORITY_REGEX.search(yaml_block)) else int(priority_match.group())
      style_key = "" if not (style_match := STYLE_REGEX.search(yaml_block)) else style_match.group()

      content = (lambda f: f.seek(0) or f.read())(file) if show_images else ""  # TO-DO | Fix this
      thumb_key = thumb_match.group() if (thumb_match := THUMB_REGEX.search(content)) and show_images else ""

      return [path_file, date_key, repeat_key, priority_key, thumb_key, style_key]
# ====================================


# ::::: FORMAT REMINDERS :::::
def format_reminders(valid_reminders: list) -> list: # TO-DO | maybe map for this(?)
  num_reminders = 0
  group_dates = {}
  ical_events = []

  for path_file, date_key, repeat_key, priority_key, thumb_key, style_key in valid_reminders:

    dir_name = path_file.parent.name
    name_file = path_file.stem
    num_reminders += 1

    header_dir_name = set_prio_header(dir_name, priority_key) if show_dirnames else ""
    content_event = f"{header_dir_name} - {style_key}[[{name_file}]]{style_key} {thumb_key}"
    reminder_date = schedule_old_dates(date_key, repeat_key)

    if reminder_date in group_dates:
      group_dates[reminder_date].append(content_event)

    else:
      group_dates[reminder_date] = [content_event]

    if ical_enable:
      ical_events.append([name_file, reminder_date, repeat_key, dir_name])

  return num_reminders, group_dates, ical_events
# ====================================


# ::::: GET DATETIME OBJECT :::::
def get_datetime(input_date: str) -> object:  # TO-DO | Find the right term
  format_date = datetime.datetime.strptime(input_date, default_format_date).date()
  return format_date
# ====================================


# ::::: SET PRIO HEADER :::::
def set_prio_header(dir_name: str, priority_key: int) -> str:
  if priority_key:
    head_dir_name = (f"{'#' * priority_key} {dir_name}\n")

  elif dir_name in folder_rules.keys():
    head_dir_name = (f"{folder_rules.get(dir_name)} {dir_name}\n")

  else:
    default_style = folder_rules.get("Default")
    head_dir_name = (f"{default_style} {dir_name} {default_style}\n")

  return head_dir_name
# ====================================


# ::::: SCHEDULE OLD DATES :::::
def schedule_old_dates(input_date: str, repeat_key: int) -> str:
  reminder = get_datetime(input_date)

  if repeat_key and not reminder >= TODAY:

    while reminder < TODAY:
      reminder += datetime.timedelta(days=repeat_key)
    return str(reminder)

  else:
    return input_date
# ====================================


# ::::: BUILD TIMELINE :::::
def build_timeline(group_dates: dict) -> dict:
  dates_collection = sorted(group_dates.items(), reverse=descending_sort)
  expired_group = []
  timeline = {}
  

  for key_date, events_group in dates_collection:
    reminder_date = get_datetime(key_date)

  # ::::: Calendar mode :::::

    if reminder_date < THIS_YEAR and reminder_date < TODAY and expired_dates:
      expired_group.append("".join(events_group))
      timeline["Expired"] = expired_group

    elif reminder_date == TODAY:
      timeline["Today"] = events_group

    elif reminder_date == TOMORROW:
      timeline["Tomorrow"] = events_group

    elif reminder_date < THIS_WEEK and reminder_date > TODAY:
      day = reminder_date.strftime("%A")
      timeline[day] = events_group

    elif reminder_date < THIS_YEAR and reminder_date > THIS_WEEK:
      day = reminder_date.strftime("%b %d")
      timeline[day] = events_group

    elif reminder_date > THIS_YEAR:
      day = reminder_date.strftime("%b %d %Y")
      timeline[day] = events_group

    else:

  # ::::: Simple mode :::::

      if not limited_dates:
        day = reminder_date.strftime("%b %d %Y")
        timeline[day] = events_group

      else:
        start_date = get_datetime(dates_rules["Start"])
        end_date = get_datetime(dates_rules["End"])

        if dates_rules.get("Others"):
          custom_dates = []
          custom_dates = [datetime.datetime.strptime(i, default_format_date).date() for i in dates_rules.get("Others")]


        if key_date >= start_date and key_date <= end_date or key_date in custom_dates:
          day = key_date.strftime("%b %d %Y")
          timeline[day] = events_group


  return timeline
# ====================================


# ::::: ADD TO ICAL :::::
def add_to_ical(ical_events: list) -> None:
  init_template(file=ical_file, mode="wb+", content=(empty := b""))

  cal = Calendar()

  for file_name, date, repeat_value, dir_name in ical_events:
    event = Event()
    date_reminder = get_datetime(date)

    event.add('summary', file_name)
    event.add('dtstart', date_reminder)
    event.add('dtend', date_reminder)
    event.add('description', dir_name)

    if repeat_value:
      event.add('rrule', {'FREQ': 'DAILY', 'INTERVAL': repeat_value})

    cal.add_component(event)

  init_template(file=ical_file, mode="ab", content=cal.to_ical())
# ====================================


# ::::: SAVE CHANGES :::::
def save_timeline(timeline: dict) -> None:
  structured_timeline = "\n\n".join(f"date: {date_event}\ncontent: {"\n\n".join(str(i) for i in lst_events)}" for date_event, lst_events in timeline.items()) + "\n\n"  #TO-DO | fix this
  init_template(file=timeline_file, mode="a", content=structured_timeline)
# ====================================


# ::::: MAIN :::::
@watchdog
def main() -> None:
  show_message(msg=f"Searching {"notes" if simple_mode else "reminders"} with '{main_yaml_key}' key, please wait...", sep='')

  num_reminders, group_dates, ical_events = get_info_files()

  if enable_timeline:
    init_template(file=timeline_file, mode="w", content=default_timeline)
    save_timeline(build_timeline(group_dates))
  
  add_to_ical(ical_events) if ical_enable and not simple_mode else None

  return num_reminders
# ====================================


if __name__ == "__main__":
  main()  
