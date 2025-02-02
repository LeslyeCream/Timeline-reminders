

Timeline Reminders is a Python script that allows you to automatically organize your notes on a timeline using Obsidian’s awesome [Timeline](https://github.com/George-debug/obsidian-timeline) plugin. Also create an ical file to sync all your reminders in any calendar!

![IMG_20241223_073647](https://github.com/user-attachments/assets/31c8523a-0087-4085-9873-9f09aa0e94d4)

***

# History

I basically sought to put into practice my recent knowledge in Python while solving a problem of my day to day. Although the timeline plugin is fantastic, in a real scenario I found it really "complicated" to add, modify or delete items manually on a daily basis, especially if they are hundreds or have a lot of details (and even worse if I do it from my phone) So this script tries to simplify the whole process behind it.



Instead of writing all this down to create the timeline: 

```markdown
Timeline
[line-3, body-1]

date: Today
content: `Reminders `
- [[Havoc payment]] 

Reminders 
- Tidal Free Trial 
Date: Tomorrow
content: ` Archived`
- Deisy. 
Date: Wednesday
content: `Reminders `
- [Whatsapp login] 

Birthdays
- Nathi. 
Date: Friday
Content: #Watching 
- Logo: http://www.newscom.com/cgi-bin/prnh/20080901/CLTU001LOGO

` Reminders
- [Backup apps]] 
Date: Jan 11 2022
Content: `Watching`
- Logo: http://www.newscom.com/cgi-bin/prnh/20080926/LA7E7.jpg
```

using the python script i would just have to add this inside my notes to get the same result! 

```yaml
Reminder: 2024-12-31
Repetition: 365
Priority: 1
Style: 
```




***

# Features

- Add reminders simply adding (or reusing) metadata in your notes
- Option to add priorities
- Option to choose repeat cycles
- Show thumbnails (images or GIFS)
- Reminders organized in ascending or descending order, with certain extra categories (expired events, today, this week)
- Set preset priorities for specific folders
- Option to give style (bold, italic, crossed, highlight, etc.) to each event or reminder
- A simple mode to add your notes according to their date. Useful if you study universal history, art, etc and want to see in a single timeline all events chronologically
***

# How to use it

Before running the script make sure to change the required values in the settings. Once configured just run`pip install -r requirements.txt` and then `python timeline_main.py` on the terminal.

***

# Adjustments

Inside the script you will find the following settings:

```python
default_template = f"```timeline-labeled\n[line-3, body-1]\n"
vault = "/storage/emulated/0/Documents/Obsidian/Calendar"
timeline_file = "/storage/emulated/0/Documents/Obsidian/Calendar/Calendar.md"
ical_file = "/storage/emulated/0/Documents/Obsidian/Calendar/.Calendar.ics"
enable_timeline = True
main_yaml_key = "Created"
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
	"Default": "`",
	"Birthdays": "#",
	"Anniversaries": "##"
}
excluded_paths = [timeline_file, ".obsidian", ".trash"]
```

***
`default_template` It's the code needed to create the timeline inside the note, no need to change it unless you're looking to change the appearance of the timeline. More information [here](https://github.com/George-debug/obsidian-timeline)
***

`Vault` is the path where the script should search for notes to be included in the timeline (as long as it explicitly contains a date metadata). If you don't want to alter the structure of your notes you can use the absolute path of your vault but I recommend creating a specific folder for it to avoid a constant mass scan.

***

`timeline_file` must be the path where you will create the file with the timeline. 

***
`enable_timeline` Enables the creation of a timeline. It can be used alongside `ical_enable` to ignore the timeline and add directly as calendar events.
***
`ical_file` should be the path where the ical file will be saved to sync with your calendar.

***
`main_yaml_key` This is the main metadata key that the script will use to extract the date of each note. By default is Reminder but I can be any other: Created, Updated, Date, etc.
***
`reverse_sort` Reverses the order of the timeline (more distant reminders first or vice versa). By default the closest ones to the current date is displayed.

***

`show_expired_dates` Displays reminders that have already expired and do not have a repeat cycle set at the beginning of the timeline.

![Screenshot_20241228-183119_cropped](https://github.com/user-attachments/assets/8b393915-218b-475b-b23d-8950bcb2d024)

***

`show_dirnames` Enables in the timeline the name of the folder from which the reminder came from. If you just want to have all your reminders no matter where they come from, turn off this option.

![Screenshot_20241228-181839_cropped](https://github.com/user-attachments/assets/31c86cc6-32f1-45f5-9761-681aac0d6715)

***

`show_images` Enable timeline thumbnails

![Screenshot_20241228-181403_cropped](https://github.com/user-attachments/assets/bf579ba0-79e0-451e-b537-67e13aec6e8f)


***

`simple_mode` Organize your notes by their respective dates

***
`limited_dates` Enables limits on the date range of notes to be added to the timeline.

***

`dates_rules` Is the set of rules regarding the dates in the metadata within the notes to be added to the timeline. It consists of three values:

`Start` and `End` Represents from and to what date the notes should be added to the timeline.

`Others` Is a list with specific dates that should be included in the timeline and is not within the range of `Start` and `End`. It must follow the following structure:

```python
["DATE1", "DATE2", "DATE3"]

```

You can ignore the inclusion of specific dates by leaving the list empty:

```python
"Others": []
```

So for example if I want to create a timeline with all my notes from the year 2024 but in addition I want it to include the notes I saved on Valentine's Day 2013 the configuration for `date_rules` should be:

```python
dates_rules = {
	"Start": "2024-01-01", 
	"End": "2024-12-31",
	"Others": ["2013-02-14"]
	}
```

**Important:** the date format for `dates_rules` must be the same as used in `default_format_dates`.

***

`ical_enable` Enables the creation of an ics file containing ready-to-use reminders in any calendar service or app (offline or online). That way you can have notifications about your notes!

***

`folder_rules` Is a dictionary that stores the priority rules that should be applied to a certain folder containing reminders. For example: if my main folder is `Calendar` and contains a subfolder called `Birthdays` I can add a level 1 priority (i.e. a header H1) for all reminders within `Birthdays'. The default value is a code line style.

![Screenshot_20241228-180247_cropped](https://github.com/user-attachments/assets/cab50dc5-0848-4ea3-8107-4123a0ca2b04)
***

`excluded_paths` A list with the names of the directories that should be omitted when creating the timeline. By default, it includes the file that will contain the timeline itself, as well as Obsidian's hidden folders.
***

# Metadata available

```Yaml
---
Reminder: 2024-12-26
Repeat: 7
Priorities: 1
Style: 
---
```

`Reminder` The date of reminder

`Repeat` Every few days the reminder should be repeated

`Priority` the priority from 1 to 6 assigned to the folder containing the reminder.

`Style` A custom markdown style for each reminder in the timeline (in this case the reminder will be highlighted)

![Screenshot_20241228-180951_cropped](https://github.com/user-attachments/assets/67fb97d2-51da-43c3-8ca6-661604fb2166)

The code line style unfortunately cannot be used for reminders.

***

# Priorities

They are nothing more than markdown headers to give a visual emphasis within the timeline. For example: An anniversary or work meeting might be a very important date that you don’t want to miss on a day full of to-dos, so adding an H1 header (priority 1) would give you more visibility over the rest of your reminders.

***

# Important note

In the near future I plan to separate the settings in a separate file for greater convenience. If you're wondering why the script doesn't have a CLI mode, work on it! The same goes for the absence of using the `pyaml` module instead of regular expressions within the script.

***

# What's new

**V 1.2**
- Added option to exclude subfolders
- Minor code changes

**V 1.1**

- Fixed the issue that prevented images from being displayed on the timeline despite being enabled in settings.

- From now on the script ignores hidden folders

- Now capture images whether they are local or external links

- Added the option to limit to a certain date frame notes that are added to the timeline, additionally you can choose specific dates that should be added but that are outside the given timeframe. Especially useful if you’re looking to keep track of everything you’ve captured/read in the previous year or even scroll through all your notes in a single note without using folders! 

- In case of error now the terminal shows more information about the problem that causes it.

- Code improvements.

***

# Contribution

If this script has been very useful to you in your workflow or you are looking for a slightly customized version that best suits your needs, please consider leaving me a small tip. I would really appreciate it!

<a href='https://ko-fi.com/W7W349H97' target='_blank'><img height='36' style='border:0px;height:36px;' src='https://storage.ko-fi.com/cdn/kofi1.png?v=6' border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>


Don’t forget to report bugs or contribute new ideas! (:

***

Created in Acode, written with Fleksy and made with ❤
