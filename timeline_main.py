from icalendar import Calendar, Event
from dateutil import parser
from pathlib import Path
import functools
import datetime
import re


# ::::: SETTINGS :::::
default_template = f"```timeline-labeled\n[line-3, body-1]\n"
vault = "/storage/emulated/0/Documents/Obsidian/Calendar"
timeline_file = "/storage/emulated/0/Documents/Obsidian/Calendar/Calendar.md"
ical_file = "/storage/emulated/0/Documents/Obsidian/Calendar/.Calendar.ics"
reverse_sort = False
show_expired_dates = True
show_dirnames = True
show_images = True
ical_enable = True
simple_mode = False
folder_rules = {
  "Default": "`", # don't delete this value
  "Birthdays": "#",
  "Anniversaries": "##"
}
# ====================================


# ::::: VARIABLES :::::
date_regex = r"(?<=Reminder\:\s)\d{4}\-\d{2}\-\d{2}(T\d{2}\:\d{2}\:\d{2})?"
repeat_regex = r"(?<=Repeat\:\s)\d+"
priority_regex = r"(?<=Priority\:\s)[1-6]"
style_regex = r"(?<=Style\:\s).*"
thumb_regex = r"\!\[{2}.*(\.jpg|png|heic|webp|jpeg)\]{2}"
default_format_date = "%Y-%m-%d"
today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)
this_week = today + datetime.timedelta(days=7)
this_year = datetime.datetime(today.year, 12, 31).date()
dates_dict = {}
ical_events = []
timeline = {
  "Expire": [],
  "Today": [],
  "Tomorrow": [],
  "This week": []
}
# ====================================


# ::::: DASHBOARD :::::
def init_template(**kwargs) -> None:
  with open(timeline_file, kwargs["mode"]) as f:
    f.write(kwargs["content"])
# ====================================


# ::::: CHECK FORMAT DATE :::::
def check_format_date(input_date: str) -> str:
  try:
    formated_date = parser.parse(input_date).strftime(default_format_date)
    return str(formated_date)

  except ValueError as msg_error: # TO-DO | Check later
    print(f"Error: '{input_date}': {msg_error}")
# ====================================


# ::::: ONLY YAML FILES:::::
def yaml_files(md_file) -> str:
  with open(md_file, "r") as f:
    if match := re.search(date_regex, f.read()):
      return md_file
# ====================================


# ::::: CHECK REMINDER :::::
def check_metadata (path_file: str) -> list:
  with open(path_file, "r") as f:
    content = f.read()
    date_key = re.search(date_regex, content)
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
def set_priority_dir(dir_name, show_dirnames, priority_key):
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
def schedule_old_dates(input_date: str, repeat_key: int) -> object:
  reminder = datetime.datetime.strptime(input_date, default_format_date).date()

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
def concatenate_files(files: list) -> list:
  each_day = (i for i in files)
  format_content = "\n\n".join(str(i) for i in each_day)
  return format_content
# ====================================


# ::::: BUILD TIMELINE :::::
def build_timeline() -> None:
  for each_event in sorted(dates_dict, reverse=reverse_sort):
    content_week = [] # needed for to group week dates
    reminder_date = datetime.datetime.strptime(each_event.strip(), default_format_date).date()

    if simple_mode:
      day = reminder_date.strftime("%b %d %Y")
      timeline[day] = dates_dict[each_event]
      continue

    if reminder_date < today and show_expired_dates:
      timeline["Expire"] = dates_dict[each_event]

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


# ::::: ADD EVENTS - CALENDAR :::::
def add_to_ical(ical_events: list) -> None:
  with open(ical_file, "wb+") as f:
    f.write(b"")
  
  cal = Calendar()

  for file_name, date, repeat, dir_name in ical_events:
    event = Event()
    date_reminder = datetime.datetime.strptime(date, default_format_date).date()

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
def save_timeline() -> None:
  for time_date, lst_events in timeline.items():
    if timeline.get(time_date) != []: # TO-DO | find the right way for this line
      content_date = concatenate_files(lst_events)
      init_template(mode="a", content=f"date: {time_date}\ncontent: {content_date}\n")
# ====================================


# ::::: MAIN :::::
def main() -> None:
  init_template(mode="w", content=default_template)
  md_files = list(filter(yaml_files, [item for item in Path(vault).rglob("*.md") if str(item) != timeline_file]))
  valid_files = (map(check_metadata , md_files))

  for path_file in valid_files:
    get_reminder_details(path_file)

  build_timeline()
  save_timeline()

  if ical_enable:
    add_to_ical(ical_events)

  print("Done!")
# ====================================


if __name__ == "__main__":
  main()
