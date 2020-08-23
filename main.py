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

        except sr.UnknownValueError as e:
            print(f"Exception: {e}")
            rec_text = None

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

    
    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')

    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])



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

    if _day != -1:
        return datetime.date(month=_month, day=_day, year=_year)

