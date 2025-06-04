🏡 How to get your Airbnb iCal URL

	1.	Open your Airbnb Hosting Dashboard
	2.	Click on a listing to enter the individual calendar view (not the multi-calendar)
	3.	Click the “Settings” (⚙️) icon or the three-dot menu in the calendar view
	4.	Choose “Export calendar”
	5.	Copy the iCal URL, which should look like this:
 
https://www.airbnb.com/calendar/ical/xxxxxxxx.ics?s=YYYYYYYY

	6.	Paste it into the script like this (removing the #):
 ical_urls = [
    "https://www.airbnb.com/calendar/ical/xxxxxxxx.ics?s=YYYYYYYY",
    "https://www.airbnb.com/calendar/ical/zzzzzzzz.ics?s=WWWWWWWW",
]

	7.	Repeat for each of your listings.

 🌐 Get your exchange rate API key

	1.	Sign up for a free plan at
https://openexchangerates.org
	2.	Get your App ID
	3.	In your terminal, set the key like this before running the script:

 export OXR_APP_ID="your_api_key_here"

 ▶️ How to run

Once you’ve updated the URLs and exported your API key:
python pricing_suggestion.py

A CSV file will be generated in the current directory, for example:
pricing_suggestion_202507.csv
