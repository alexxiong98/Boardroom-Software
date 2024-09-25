from __future__ import print_function
from ast import IsNot
import datetime
import os.path
import tkinter as tk
import tkinter.font as tkFont
from tkinter import *
from datetime import timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']


def data():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '', SCOPES)  # Credentials required
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    x = 0
    y = 0
    eventStart = datetime.datetime(2100, 12, 31)
    eventEnd = datetime.datetime(2100, 12, 31)
    eventName = ''

    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        events_result = service.events().list(calendarId='', timeMin=now, maxResults=15,
                                              singleEvents=True, orderBy='startTime').execute()  # Calendar ID required
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return

        allEventStartsToday = []
        allEventEndsToday = []
        allEventNamesToday = []

        # Pulling the upcoming 15 events and append the ones upcoming today
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            eventName = event['summary']
            parseStartToday = start.split("T")
            parseEndToday = end.split("T")
            startTime = parseStartToday[1].split("-")
            endTime = parseEndToday[1].split("-")
            eventStartsTodayCheck = datetime.datetime.strptime(
                parseStartToday[0], "%Y-%m-%d").date()
            if eventStartsTodayCheck == datetime.datetime.today().date():
                allEventStartsToday.append(startTime[0])
                allEventEndsToday.append(endTime[0])
                allEventNamesToday.append(eventName)

        # Find the upcoming event
        while x < len(events):
            tempEventStart = events[x]['start'].get(
                'dateTime', event['start'].get('date'))
            tempEventEnd = events[x]['end'].get(
                'dateTime', event['end'].get('date'))
            tempCreatorEmail = events[x]['creator'].get('email')
            tempEventName = events[x]['summary']

            # Bypass all day events
            if tempEventStart == None or tempEventEnd == None:
                tempEventStart = '2100-12-31T00:00:00-04:00'
                tempEventEnd = '2100-12-31T23:00:00-04:00'

            parseDateStart = tempEventStart.split("T")
            parseHourStart = parseDateStart[1].split("-")
            parseDateEnd = tempEventEnd.split("T")
            parseHourEnd = parseDateEnd[1].split("-")

            tempHourStart = datetime.datetime.strptime(
                parseHourStart[0], "%H:%M:%S")
            tempDateStart = datetime.datetime.strptime(
                parseDateStart[0], "%Y-%m-%d")
            tempHourEnd = datetime.datetime.strptime(
                parseHourEnd[0], "%H:%M:%S")
            tempDateEnd = datetime.datetime.strptime(
                parseDateEnd[0], "%Y-%m-%d")
            tempDateStart2 = tempDateStart.date()
            tempHourStart2 = tempHourStart.time()
            tempDateEnd2 = tempDateEnd.date()
            tempHourEnd2 = tempHourEnd.time()

            nextEventStart = datetime.datetime.combine(
                tempDateStart2, tempHourStart2)
            nextEventEnd = datetime.datetime.combine(
                tempDateEnd2, tempHourEnd2)

            if nextEventStart < eventStart:
                eventStart = nextEventStart
                creatorEmail = tempCreatorEmail
                eventName = tempEventName

            x += 1

            if nextEventEnd < eventEnd:
                eventEnd = nextEventEnd
                creatorEmail = tempCreatorEmail
                eventName = tempEventName

            y += 1

    except HttpError as error:
        print('An error occurred: %s' % error)

    return (eventStart, eventEnd, eventName, creatorEmail, allEventNamesToday, allEventStartsToday, allEventEndsToday)


def occupyCheck(upcomingEvent):
    # Check if the conference room is occupied or about to be occupied
    if upcomingEvent is not None:
        start = upcomingEvent[0]
        end = upcomingEvent[1]
        tempNow = datetime.datetime.now()
        tempNow2 = tempNow.strftime("%Y-%m-%d %H:%M:%S")
        now = datetime.datetime.strptime(tempNow2, '%Y-%m-%d %H:%M:%S')
        occupied = False
        load = False

        if now >= start and now <= end:
            occupied = True

        if now > start - timedelta(minutes=10) and now < start:
            load = True

    else:
        occupied = False
        load = False

    return (occupied, load)


def displayData():
    # Retrieves all values for display
    eventName = "None"
    creatorEmail = "None"
    eventStart = "None"
    eventEnd = "None"
    upcomingEvent = data()

    if upcomingEvent is not None:
        eventStart = str(upcomingEvent[0])
        eventEnd = str(upcomingEvent[1])
        creatorEmail = str(upcomingEvent[3])
        eventName = str(upcomingEvent[2])
        tempEndTime = eventEnd.split(" ")
        tempStartTime = eventStart.split(" ")
        startTime = tempStartTime[1]
        endTime = tempEndTime[1]

    if creatorEmail == "boardroom@maxbrakes.com":
        creator = "Conference Room Booking System"
    else:
        creator = creatorEmail

    return (startTime, endTime, creator, eventName)


class displayScreen(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        tk.Tk.geometry(self, f"1024x768")
        tk.Tk.configure(self, background="#3CB043")
        tk.Tk.attributes(self, '-fullscreen', True)
        self._frame = None
        self.switch_frame(availableScreen)

    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()
        self.after(50, self.mainScreen)

    def mainScreen(self):
        upcomingEvent = data()
        occupy = occupyCheck(upcomingEvent)
        if occupy[0] == True:
            self.switch_frame(occupiedScreen)
            tk.Tk.configure(self, background="#FF0000")
        else:
            if occupy[1] == True:
                self.switch_frame(loadingScreen)
                tk.Tk.configure(self, background="#E6CC00")
            else:
                self.switch_frame(availableScreen)
                tk.Tk.configure(self, background="#3CB043")


class availableScreen(tk.Frame):
    def __init__(self, master):
        eventNamesToday = data()
        x = 0
        tk.Frame.__init__(self, master)
        tk.Label(self, bg="#3CB043", fg="white", text="Available",
                 font=("Helvetica 180 bold")).pack(pady=120)
        tk.Label(self, bg="#3CB043", fg="white", text="Upcoming Events Today:", font=(
            "any 40 bold")).pack(pady=20)
        while x < len(eventNamesToday[4]):
            tk.Label(self, bg="#3CB043", fg="white",
                     text=f"{eventNamesToday[4][x]} : {eventNamesToday[5][x]} - {eventNamesToday[6][x]}", font=("any 25 bold")).pack(pady=10)
            x += 1
        tk.Tk.config(self, bg="#3CB043")


class loadingScreen(tk.Frame):
    def __init__(self, master):
        displaydata = displayData()
        tk.Frame.__init__(self, master)
        tk.Label(self, bg="#E6CC00", text="Meeting Starting Soon...",
                 font=("Helvetica 65 bold")).pack(pady=170)
        tk.Label(self, bg="#E6CC00", text=displaydata[3], font=(
            "any 25 bold")).pack(pady=20)
        tk.Label(self, bg="#E6CC00", text=f'Created By: {displaydata[2]}', font=(
            "any 20 bold")).pack(pady=20)
        tk.Label(self, bg="#E6CC00",
                 text=f'Scheduled For: {displaydata[0]} - {displaydata[1]}', font=("any 20 bold")).pack(pady=20)
        tk.Tk.config(self, bg="#E6CC00")


class occupiedScreen(tk.Frame):
    def __init__(self, master):
        displaydata = displayData()
        tk.Frame.__init__(self, master)
        tk.Label(self, bg="#FF0000", fg="white", text="Occupied!",
                 font=("Helvetica 140 bold")).pack(pady=150)
        tk.Label(self, bg="#FF0000", fg="white",
                 text=displaydata[3], font=("any 25 bold")).pack(pady=20)
        tk.Label(self, bg="#FF0000", fg="white", text=f'Created By: {displaydata[2]}', font=(
            "any 20 bold")).pack(pady=20)
        tk.Label(self, bg="#FF0000", fg="white",
                 text=f'Scheduled For: {displaydata[0]} - {displaydata[1]}', font=("any 20 bold")).pack(pady=20)
        tk.Tk.config(self,  bg="#FF0000")


if __name__ == '__main__':
    data()
    displayData()
    app = displayScreen()
    app.mainloop()
