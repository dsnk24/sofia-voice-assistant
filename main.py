from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import time
import pyttsx3
import speech_recognition as sr
import pytz
from time import sleep
import sys
from random import choice


engine = pyttsx3.init()

voices =  engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

engine.setProperty('volume', 0.5)


SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

DAYS = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday"
]

MONTHS = [
    "january",
    "february",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december"
]

DAY_EXTENSIONS = [
    "rd",
    "th",
    "st"
]


CALENDAR_TRIGGERS = [
    "am i busy",
    "do i have plans",
    "am i free",
    "what plans do i have",
    "what do i have"
]


NOT_UNDERSTOOD_RESPONSES = [
    "I'm sorry, I didn't catch that?",
    "I did't quite understand what you said?",
    "I don't understand, can you try again?"
]



def speak(text):
    engine.say(text)
    engine.runAndWait()


def recognize_speech():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        audio = r.listen(source)
        rec_text = ""

        try:
            rec_text = r.recognize_google(audio_data=audio)

        except Exception as e:
            print(f"Exception: {e}")
            rec_text = ""

        return rec_text




def auth_google_calendar():
    creds = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    return service



def get_events(day, service):

    date = datetime.datetime.combine(day, datetime.datetime.min.time())
    end_date = datetime.datetime.combine(day, datetime.datetime.max.time())

    utc = pytz.UTC

    date = date.astimezone(utc)
    end_date = end_date.astimezone(utc)

    events_result = service.events().list(
        calendarId='primary',
        timeMin=date.isoformat(),
        timeMax=end_date.isoformat(),
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])

    if not events:
        speak('Nothing in sight')

    else:
        if len(events) != 1: 
            speak(f"You have {len(events)} events on that day.")
        
        else:
            speak(f"You have {len(events)} event on that day.")

        sleep(1.0)

        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))

            print(start, event['summary'])

            try:
                start_time_list = start.split("T")[1].split("-")[0].split(":")

                start_time = str(start_time_list[0]) + ":" + str(start_time_list[1])

                if int(start_time.split(":")[0]) < 12:
                    start_time += " A.M."
                
                else:
                    start_time = str((int(start_time_list[0]) - 12)) + ":" + str(start_time_list[1])
                    start_time += " P.M."
            
            except Exception as e:
                start_time = None

            if start_time != None:
                speak(f"{event['summary']} at {start_time}")
            
            else:
                speak(f"{event['summary']}")

            sleep(0.7)



def get_date(text):
    text = text.lower()

    today = datetime.date.today()

    if text.count("today") > 0:
        return today
    

    _day = -1
    _day_of_week = -1
    _month = -1
    _year = today.year


    words = text.split()


    for word in words:
        if word in MONTHS:
            _month = MONTHS.index(word) + 1

        elif word in DAYS:
            _day_of_week = DAYS.index(word)

        elif word.isdigit():
            _day = int(word)
        
        else:
            for ext in DAY_EXTENSIONS:
                found_ext = word.find(ext)

                if found_ext > 0:
                    try:
                        _day = int(word[:found_ext])

                    except Exception as e:
                        print(f"Exception: {e}")


    if _month < today.month and _month != -1:
        _year += 1
    
    if _month == -1 and _day != -1:
        if _day < today.day:
            _month = today.month + 1
        
        else:
            _month = today.month

    if _month == -1 and _day == -1 and _day_of_week != -1:
        current_day_of_week = today.weekday()

        dif = _day_of_week - current_day_of_week

        if dif < 0:
            dif += 7
            if text.count("next") >= 1:
                dif += 7

        return today + datetime.timedelta(dif)

    if _month == -1 or _day == -1:
        return None

    if _day != -1:
        return datetime.date(month=_month, day=_day, year=_year)


service = auth_google_calendar()


if __name__ == "__main__":
    while True:
        print(">>>")

        text = recognize_speech()

        for keyword in CALENDAR_TRIGGERS:
            if keyword in text.lower():
                date = get_date(text)

                if date:
                    get_events(get_date(text), service)
                
                else:
                    speak(choice(NOT_UNDERSTOOD_RESPONSES))
            
            else:
                pass
        
        if "quit program" in text:
            sys.exit()
            break