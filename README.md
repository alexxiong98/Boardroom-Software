# Boardroom Software

## Overview

The Boardroom software is designed to manage booking systems and display related information for a boardroom environment. The project includes both backend and frontend components, handling booking functionalities and display interfaces.

## Features

Booking Management: Enables users to book boardrooms and manage schedules.
Display Interface: Shows booking information and other relevant details on the screen.
Automation Scripts: Includes scripts for refreshing and killing processes for system management/automation.
SQL Database Integration: The system utilizes an SQL database to store booking information, user details, and other relevant data, ensuring quick and reliable access to records.

## Folder Structure

Booking/: Contains code and resources related to the booking system.
Display/: Display of booking data. Meant for displays outside of boardroom and around the office.
index.html: One time use interface to setup Google API connection and authorization.
kill.bat: A batch script that can stop or kill any related running processes.
refresh.bat: A batch script that refreshes the software, used only by the main boardroom machine.
requirements.txt: Dependencies needed to run the system.
token.json: Authenication tokens from Google.

## Installation

1. Clone or download the repository.
2. Ensure Python is installed on your machine.
3. Install the required dependencies by running:
   pip install -r requirements.txt
4. Create a Google Resource Calendar, enable Google Workspace API and setup OAUTH to access token and credientials.
   For more information:https://developers.google.com/workspace/guides/get-started
5. Create SQL database to store booking information, user details, and other relevant data.

## Recommendations

1. Set up Window Task Scheduler for all bat files and configure to your own requirements.
   refresh.bat, kill.bat, booking.bat, display.bat will not be the solution for everyone.
2. BoardroomBooking.py contains the UI and logic for manual boardroom booking.
   User can create a module in the company's employee portal using the same logic.

## Contributions

Feel free to contribute by submitting pull requests or opening issues. Please follow the standard coding conventions when contributing.

## License

This software is licensed under Alex Xiong.
