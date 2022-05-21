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
import subprocess
import wikipedia
import detector
import wolframalpha
import requests
from playsound import playsound
from time import ctime



apikey = 'XXXXX'

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
MONTHS = ['january' , 'february' , 'march' , 'april' , 'may' , 'june' , 'july' , 'august' , 'september' , 'october' , 'november' , 'december']
DAYS = ['monday' , 'tuesday' , 'wednesday' , 'thursday' , 'friday' , 'saturday' , 'sunday']
DAY_EXTENSIONS = ['rd' , 'th' , 'st' , 'nd']

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        said = ""

        try:
            said = r.recognize_google(audio)
            print(said)
        except Exception as e:
            print("Exception: " + str(e))

    return said.lower()

def authenticate_google():
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

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    return service

def get_events(day, service):
    # Call the Calendar API

    date = datetime.datetime.combine(day, datetime.datetime.min.time())
    end_date = datetime.datetime.combine(day, datetime.datetime.max.time())

    utc=pytz.UTC
    date = date.astimezone(utc)
    end_date = end_date.astimezone(utc)

    events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(), timeMax = end_date.isoformat(),
                                         singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        speak('No upcoming events found.')

    else:
        speak(f'You have {len(events)} events on this day')

        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
            start_time = str(start.split("T")[1].split("+")[0])
            if int(start_time.split(":")[0]) < 12:
                start_time = start_time + 'am'
            else:
                start_time = str(int(start_time.split(":")[0])-12) + start_time.split(":")[1]
                start_time = start_time + 'pm'

            speak(event['summary'] + " at " + start_time)

def  get_date(text):
    text = text.lower()
    today = datetime.date.today()

    if text.count("today") > 0:
        return today

    day = -1
    day_of_week = -1
    month = -1
    year = today.year

    for word in text.split():
        if word in MONTHS:
            month = MONTHS.index(word) + 1
        elif word in DAYS:
            day_of_week = DAYS.index(word)
        elif word.isdigit():
            day = int(word)
        else:
            for ext in DAY_EXTENSIONS:
                found = word.find(ext)
                if found > 0:
                    try:
                        day = int(word[:found])
                    except:
                        pass

    if month < today.month and month != -1:
        year = year + 1
    if day < today.day and day != -1 and month == -1:
        month = month + 1
    if month == -1 and day == -1 and day_of_week != -1:
        current_day_of_week = today.weekday()
        dif = day_of_week - current_day_of_week

        if dif < 0:
            dif += 7
            if text.count("next") >= 1:
                dif +=7

        return today + datetime.timedelta(dif)
    if month == -1 or day == -1:
        return None

    return datetime.date(month = month, day = day, year = year)

def note(text):
    date = datetime.datetime.now()
    file_name = str(date).replace(":","-") + "-note.txt"
    with open(file_name , "w") as f:
        f.write(text)
    subprocess.Popen(["notepad.exe",file_name])

def wolfram_alpha(question=''):
    try:
        client = wolframalpha.Client(apikey)
        res = client.query(question)
        answer = next(res.results).text
        return answer
    except:
      searchResults = wikipedia.search(question)
  
      if not searchResults:
        print("No results found from Wikipedia")
        return "No results found"

      try:
        page = wikipedia.page(searchResults[0])
      except wikipedia.DisambiguationError as err:
        page = wikipedia.page(err.options[0])
    
      return [str(page.title.encode('utf-8')), str(page.summary.encode('utf-8'))]

def about_me():
    text = "I am a personal assistant named Tom, created by Sanjai , Mayur and Kishan."
    return text

def NewsFromBBC(): 
    
    main_url = " https://newsapi.org/v1/articles?source=bbc-news&sortBy=top&apiKey=4dbc17e007ab436fb66416009dfb59a8"
    open_bbc_page = requests.get(main_url).json()  
    article = open_bbc_page["articles"] 
    results = [] 
    
    for ar in article: 
        results.append(ar["title"]) 
    
    for i in range(len(results)):  
        speak(results[i]) 
        time.sleep(0.8)

def login():
    if (detector.faceReg() == True):
        return True
    else: 
        return False

def bot():
    WAKE = 'tom'
    SERVICE = authenticate_google()
    print('Start')
    while True:
        print("Listening")
        text = get_audio()

        if text.count(WAKE) > 0:
            playsound('forward.mp3')
            text = get_audio()
                
            if ('what do i have' or 'do i have plans' or 'am i busy') in text:
                date = get_date(text)
                if date:
                    get_events(date, SERVICE)
                else:
                    speak("i don't understand")

            elif ('what is your name' or 'name') in text:
                speak('My name is Tom')

            elif ('make a note' or 'write this down' or 'remember this') in text:
                speak('What would you like me to write down')
                note_text = get_audio()
                note(note_text)
                speak("I've made a note of it")

            elif ('tell me about yourself' or 'who are you' or 'what are you') in text:
                speak(about_me())

            elif ('what is the latest news' or 'tell me the news' or 'headlines' or 'news' or 'latest news') in text:
                speak("Here is the latest news from BBC")
                NewsFromBBC()

            elif ('shutdown' or 'shut down') in text:
                speak("Good Bye, Shutting down")
                break;

            else:
                try: 
                    speak(wolfram_alpha(text))
                except:
                    speak("Sorry i didn't understand")


def main():
    auth = login()
    if auth == True:
        speak("I have recognized your face. You are now successfully logged in.")
        bot()
    else:
        speak("Sorry, you are not authenticated. You can register and then you can use me")
        main()

speak("Hi i am your personal assistant Tom. Please wait while i authenticate you.")
main()
