#!/usr/bin/env python3

import calendar
import getopt
import logging
import os
import re
import subprocess
import sys
import time

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


try:
    opts, args = getopt.getopt(
        sys.argv[1:], "", ["end=", "eventprefix=", "start=", "write"]
    )
except getopt.GetoptError:
    print("fax")
    sys.exit(2)

write = None
for opt, arg in opts:
    if opt == "-h":
        print("No help for you")
        sys.exit(1)
    elif opt in ("--end"):
        end = arg
    elif opt in ("--eventprefix"):
        event_prefix = arg
    elif opt in ("--start"):
        start = arg
    elif opt in ("--write"):
        write = True

# Since Fantastical 3 the name of the binary is simply Fantastical.app
fantastical = "Fantastical"
try:
    fantastical_version = os.listdir("/Applications")
    if "Fantastical 2.app" in fantastical_version:
        fantastical = "Fantastical 2"
except:
    print("Unable to get Fantastical version.")
    sys.exit(1)

if not write:
    logging.warning("Dry-run is in use - no writing to the calendar will be done")


pattern = "%Y-%m-%d"
epoch_start = calendar.timegm(time.strptime(start, pattern))
epoch_end = calendar.timegm(time.strptime(end, pattern))
loop = epoch_start

schedule = {
    "monday": {"drop": "Johan", "pickup": "Johan"},
    "tuesday": {"drop": "Johan", "pickup": "Ellinor"},
    "wednesday": {"drop": "Ellinor", "pickup": "Ellinor"},
    "thursday": {"drop": "Ellinor", "pickup": "Johan"},
    "friday": {"drop": "Ellinor", "pickup": "Johan"},
}

while loop <= epoch_end:
    pretty_date = time.strftime("%Y-%m-%d", time.localtime(loop))
    day_name = time.strftime("%A", time.localtime(loop)).lower()

    if re.search("saturday|sunday", day_name):
        loop = loop + 86400
        continue

    for event in ["drop", "pickup"]:
        if event == "drop":
            event_string = f"Lämnar on {pretty_date} between 08:00 and 08:30"
        elif event == "pickup":
            event_string = f"Hämtar on {pretty_date} between 15:30 and 16:30"

        calendar_names = [schedule[day_name][event]]
        if schedule[day_name][event] == "Johan":
            calendar_names.append("jocar@sunet")
        for calendar_name in calendar_names:
            applescript = f"""
tell application "{fantastical}"
    parse sentence "{event_string}" calendarName "{calendar_name}" with add immediately
end tell"""
            logging.info(applescript)
            if write is True:
                subprocess.call(["osascript", "-e", applescript])

    loop = loop + 86400
