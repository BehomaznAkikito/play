#!/usr/bin/env python3
"""Calculate pricing suggestions based on Airbnb iCal calendars.

This script fetches occupancy information for each room listed in
`ical_urls` for the next calendar month and outputs a CSV file in the
format:

    YYYY-MM,total_nights,vacant_nights,recommended_price_JPY

Requirements: `ics`, `pandas`, `requests`.
If they are not installed, the script tries to install them
automatically. The Open Exchange Rates App ID must be supplied via the
`OXR_APP_ID` environment variable.
"""

import calendar
import datetime
import importlib.util
import os
import subprocess
import sys

REQUIRED_LIBS = ["ics", "pandas", "requests"]

# Install missing libraries if necessary
missing = [lib for lib in REQUIRED_LIBS if importlib.util.find_spec(lib) is None]
if missing:
    print("Installing missing libraries: ", ", ".join(missing))
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", *REQUIRED_LIBS])
    except subprocess.CalledProcessError:
        print("Failed to install required libraries. Please install 'ics pandas requests' manually.")
        sys.exit(1)

from ics import Calendar
import pandas as pd
import requests

# iCal URLs for each room
ical_urls = [
    # "https://www.airbnb.com/calendar/ical/ROOM_ID.ics?s=...",
]

if not ical_urls:
    print("No iCal URLs specified. Edit the 'ical_urls' list in the script and rerun.")
    sys.exit(1)

app_id = os.getenv("OXR_APP_ID")
if not app_id:
    print("Environment variable OXR_APP_ID is missing. Set your Open Exchange Rates App ID and rerun.")
    sys.exit(1)

# Fetch USD/JPY rate
try:
    resp = requests.get(
        "https://openexchangerates.org/api/latest.json",
        params={"app_id": app_id, "symbols": "JPY"},
        timeout=10,
    )
    resp.raise_for_status()
    usd_jpy_rate = resp.json()["rates"]["JPY"]
except Exception as exc:
    print(f"Failed to fetch USD/JPY rate: {exc}")
    sys.exit(1)

# Determine next month
today = datetime.date.today()
if today.month == 12:
    year = today.year + 1
    month = 1
else:
    year = today.year
    month = today.month + 1

month_start = datetime.date(year, month, 1)
month_end = datetime.date(year, month, calendar.monthrange(year, month)[1])
month_str = f"{year:04d}-{month:02d}"
filename = f"pricing_suggestion_{year:04d}{month:02d}.csv"

def booked_days_for_calendar(cal: Calendar) -> set[datetime.date]:
    booked = set()
    for event in cal.events:
        start = event.begin.date()
        end = event.end.date()
        day = start
        while day < end:
            if month_start <= day <= month_end:
                booked.add(day)
            day += datetime.timedelta(days=1)
    return booked

rows = []
for url in ical_urls:
    try:
        text = requests.get(url, timeout=10).text
        cal = Calendar(text)
    except Exception as exc:
        print(f"Failed to fetch or parse iCal from {url}: {exc}")
        sys.exit(1)

    booked = booked_days_for_calendar(cal)
    total_nights = (month_end - month_start).days + 1
    vacant_nights = total_nights - len(booked)
    vacancy_rate = vacant_nights / total_nights
    occupancy_coef = 0.9 + 0.2 * vacancy_rate
    recommended_price = 120 * usd_jpy_rate * occupancy_coef

    rows.append(
        {
            "YYYY-MM": month_str,
            "total_nights": total_nights,
            "vacant_nights": vacant_nights,
            "recommended_price_JPY": round(recommended_price, 2),
        }
    )

# Write CSV without headers
pd.DataFrame(rows)[
    ["YYYY-MM", "total_nights", "vacant_nights", "recommended_price_JPY"]
].to_csv(filename, index=False, header=False)
print(f"Output written to {filename}")
