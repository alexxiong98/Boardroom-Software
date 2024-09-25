from __future__ import print_function
from ast import Or
from contextlib import nullcontext
import datetime
from doctest import master
from http.client import REQUESTED_RANGE_NOT_SATISFIABLE
from lib2to3.pgen2.token import GREATER
import os.path
from tracemalloc import start
from turtle import bgcolor
from xmlrpc.client import DateTime
import mysql.connector
import tkinter as tk
import tkinter.font as tkFont
from datetime import datetime, timedelta
from tkinter import *
from tkinter import messagebox
from tkcalendar import Calendar
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

# SQL DB connection
mydb = mysql.connector.connect(
)


class bookRoom(tk.Tk):
    def __init__(self):
        w0, h0 = 1280, 1024
        w1, h1 = 1920, 1080
        tk.Tk.__init__(self)
        tk.Tk.geometry(self, f"{w1}x{h1}+{w0}+0")
        # tk.Tk.attributes(self, '-fullscreen', True)
        tk.Tk.overrideredirect(self, True)
        self._frame = None
        self.switch_frame(loginScreen)

    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()

    tableinsert = []

    def validateLogin(self, employeeid):
        # Check if employeeid is valid and in the db
        mycursor = mydb.cursor()
        tempEmployeeid = employeeid.get()
        checkEmployeeid = "?"
        if checkEmployeeid in tempEmployeeid:
            employeeid.set(tempEmployeeid[-6:])
        query = (
            "SELECT * FROM cfidb.fausers WHERE cardid = '%s'") % (employeeid.get())
        mycursor.execute(query)
        myresults = mycursor.fetchall()
        tableinserts = bookRoom.tableinsert
        if not myresults:
            messagebox.showerror("showerror", "Error: Invalid Employeeid")
        else:
            for x in myresults:
                if len(tableinserts) > 0:
                    tableinserts = []
                tableinserts.append(x[4])
                tableinserts.append(x[12])
            bookRoom.tableinsert = tableinserts
            self.switch_frame(bookScreen)

    start = datetime.now()
    end = datetime.now()

    def validateEvent(self, start, end):
        # Check if the booking is overlapping with another event
        tempEvent = data()
        allEventStart, allEventEnd = tempEvent
        x = 0
        check = False
        while x < len(allEventStart):
            if (start < allEventStart[x] and end <= allEventStart[x]) or (start >= allEventEnd[x]):
                check = True
            else:
                messagebox.showerror(
                    "showerror", "Sorry the time you selected is not available")
                self.switch_frame(bookScreen)
                check = False
                break
            x += 1

        if check == True:
            bookRoom.start = start
            bookRoom.end = end
            self.bookEvent(start, end)

    def bookEvent(self, start, end):
        gglextra = ".000"
        tempStartDateTime = start.strftime('%Y-%m-%d %H:%M:%S')
        tempEndDateTime = end.strftime('%Y-%m-%d %H:%M:%S')
        startDateTime = tempStartDateTime.replace(" ", "T")
        endDateTime = tempEndDateTime.replace(" ", "T")
        start = startDateTime + gglextra
        end = endDateTime + gglextra

        # Data posting to GOOGLE, attendee is treated as a room resouce
        event = {
            'summary': 'Max Advanced Brakes Meeting',
            'location': '280 Hillmount Rd Unit #5, Markham, ON L6C 3A1',
            'description': 'Meeting for Max Advanced Brakes',
            'start': {
                'dateTime': start,
                'timeZone': 'America/New_York',
            },
            'end': {
                'dateTime': end,
                'timeZone': 'America/New_York',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
            'attendees': [
                {'email': '', 'id': '50050318219', 'resource': 'True'},
            ],
        }
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
                    '', SCOPES)  # Credientials.json required
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        service = build('calendar', 'v3', credentials=creds)

        # Execute to book event on GOOGLE Calendar
        event = service.events().insert(
            calendarId="", body=event).execute()  # Calendar ID required
        self.toDatabase()
        messagebox.showinfo("showinfo", "Your meeting has been booked!")
        self.switch_frame(loginScreen)

    # Inserts created events into SQL db
    def toDatabase(self):
        start = bookRoom.start.strftime('%Y-%m-%d %H:%M:%S')
        end = bookRoom.end.strftime('%Y-%m-%d %H:%M:%S')
        cursor = mydb.cursor()
        query = f'INSERT INTO alex.meetings (firstname, lastname, meetingstart, meetingend) VALUES (%s,%s,%s,%s)'
        data = (bookRoom.tableinsert[0], bookRoom.tableinsert[1], start, end)
        cursor.execute(query, data)
        mydb.commit()


class loginScreen(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, pady=100)
        tk.Label(self, text="Enter or Scan Employeeid",
                 font=("Helvetica 35 bold")).pack(pady=50)
        employeeid = StringVar()
        entry = tk.Entry(self, textvariable=employeeid,
                         font='Helvetica 20 bold')
        entry.pack(side="top", fill="x", pady=10)
        entry.focus_set()
        btn = tk.Button(self, text="Enter", font=(
            "Helvetica 20 bold"), command=lambda: master.validateLogin(employeeid))
        btn.pack(pady=20)
        mycursor = mydb.cursor()
        connectionquery = ("SET @@session.wait_timeout=86400")
        mycursor.execute(connectionquery)

        def key_press(e):
            if e.keycode == 13:
                master.validateLogin(employeeid)
        entry.bind('<KeyPress>', key_press)


class bookScreen(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master, pady=30)
        tk.Label(self, text=f"Welcome Back {bookRoom.tableinsert[0]}!", font=(
            "Helvetica 25 bold")).pack(side="top", fill="x", pady=35)
        tk.Label(self, text="Please select the date and time you would like to book the conference room", font=(
            "Helvetica 25 bold")).pack(side="top", fill="x")
        calendar = Calendar(self, selectmode='day', font="Arial 45")
        calendar.pack(side=tk.LEFT, anchor=tk.N, pady=70)
        Label(self, text="Set Time (HOUR:MINUTE)",
              font=("Helvetica 20 bold")).pack(pady=35)

        arial20 = tkFont.Font(family="Arial", size=20)

        tempHour = StringVar(self)
        hours = ('09', '10', '11', '12', '13', '14', '15', '16', '17', '18')
        tempHour.set("Hour")
        hrs = OptionMenu(self, tempHour, *hours)
        hrs.config(width=10, bg='#b3e5fc', font=arial20)
        hrs.pack(side=tk.TOP, ipadx=50, ipady=20, padx=150)
        hrsmenu = self.nametowidget(hrs.menuname)
        hrsmenu.config(font=arial20)

        tempMinute = StringVar(self)
        minutes = ('00', '05', '10', '15', '20', '25',
                   '30', '35', '40', '45', '50', '55')
        tempMinute.set("Minute")
        mins = OptionMenu(self, tempMinute, *minutes)
        mins.config(width=10, bg='#b3e5fc', font=arial20)
        mins.pack(side=tk.TOP, ipadx=50, ipady=20, padx=30, pady=10)
        minsmenu = self.nametowidget(mins.menuname)
        minsmenu.config(font=arial20)

        tempSecond = StringVar(self)
        seconds = ('00')
        tempSecond.set(seconds[0])

        tk.Label(self, text="Set Meeting Duration (In Minutes)",
                 font=("Helvetica 20 bold")).pack(side=tk.TOP, pady=30)

        tempDuration = StringVar(self)
        durations = ('15', '30', '45', '60', '75', '90',
                     '105', '120', '135', '150', '165', '180')
        tempDuration.set("Duration")
        dur = OptionMenu(self, tempDuration, *durations)
        dur.config(width=10, bg='#b3e5fc', font=arial20)
        dur.pack(side=tk.TOP, ipadx=80, ipady=20)
        durmenu = self.nametowidget(dur.menuname)
        durmenu.config(font=arial20)

        tk.Button(self, text="Cancel", bg='red', fg='white', width=20, height=5, font=("Helvetica 20 bold"),
                  command=lambda:  master.switch_frame(loginScreen)).pack(side=tk.BOTTOM, anchor=tk.CENTER)
        tk.Button(self, text="Book", bg='green', fg='white', width=20, height=5, font=(
            "Helvetica 20 bold"), command=lambda:  getTime()).pack(side=tk.BOTTOM, pady=20, anchor=tk.CENTER)

        # Record user input and checks validity
        def getTime():
            tempStartTime = f"{tempHour.get()}:{tempMinute.get()}:{tempSecond.get()}"
            now = datetime.now()

            if tempStartTime == 'Hour:Minute:0':
                messagebox.showerror(
                    "showerror", "Please select meeting start time")
            else:
                tempStartDate = calendar.get_date()
                startTime = datetime.strptime(tempStartTime, '%H:%M:%S').time()
                startDate = datetime.strptime(tempStartDate, '%m/%d/%y').date()
                start = datetime.combine(startDate, startTime)

            if start < now:
                messagebox.showerror(
                    "showerror", "Please select a future time")
                self.switch_frame(bookScreen)

            if tempDuration.get() == 'Duration in minutes':
                messagebox.showerror(
                    "showerror", "Please select meeting duration")
            else:
                end = start + timedelta(minutes=int(tempDuration.get()))

            print(data())

            master.validateEvent(start, end)


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
        if creds and creds.expiry and creds.refresh_token:
            curTime = datetime.now()
            print(curTime)
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '', SCOPES)  # Credientials.json required
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        events_result = service.events().list(calendarId="", timeMin=now, maxResults=100,
                                              singleEvents=True, orderBy='startTime').execute()  # Calendar ID required
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return

        allEventStart = []
        allEventEnd = []

        # Appends all event start and event end in datetime format
        for event in events:
            tempEventStart = event['start'].get(
                'dateTime', event['start'].get('date'))
            tempEventEnd = event['end'].get(
                'dateTime', event['end'].get('date'))

            parseDateStart = tempEventStart.split("T")
            parseHourStart = parseDateStart[1].split("-")
            parseDateEnd = tempEventEnd.split("T")
            parseHourEnd = parseDateEnd[1].split("-")

            tempHourStart = datetime.strptime(parseHourStart[0], "%H:%M:%S")
            tempDateStart = datetime.strptime(parseDateStart[0], "%Y-%m-%d")
            tempHourEnd = datetime.strptime(parseHourEnd[0], "%H:%M:%S")
            tempDateEnd = datetime.strptime(parseDateEnd[0], "%Y-%m-%d")
            tempDateStart2 = tempDateStart.date()
            tempHourStart2 = tempHourStart.time()
            tempDateEnd2 = tempDateEnd.date()
            tempHourEnd2 = tempHourEnd.time()

            eventStart = datetime.combine(tempDateStart2, tempHourStart2)
            eventEnd = datetime.combine(tempDateEnd2, tempHourEnd2)

            allEventStart.append(eventStart)
            allEventEnd.append(eventEnd)

    except HttpError as error:
        print('An error occurred: %s' % error)

    return allEventStart, allEventEnd


if __name__ == '__main__':
    data()
    app = bookRoom()
    app.mainloop()
