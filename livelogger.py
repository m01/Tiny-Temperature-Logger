#!/usr/bin/env python
#this code is based on:
# http://www.mattcutts.com/blog/write-google-spreadsheet-from-python/
import serial
import glob
import time
import sys
import gdata.spreadsheet.service
from gdata.service import BadAuthentication, CaptchaRequired, Error
import getpass	#password input library

#connect to the google docs spreadsheet service.
client = gdata.spreadsheet.service.SpreadsheetsService()

# --- configuration below this line ---
client.source='m01-tmp102livelogger-v01'
client.ssl = True		      # Force all API requests through HTTPS
client.http_client.debug = False      # Set to True for debugging HTTP requests
client.email = ''	       	      # email of google account

# which spreadsheet and which worksheet within a spreadsheet should be used?
# use the spreadsheetFinder.py script to get this data.
# (You'll need to create the spreadsheet in google docs first, and add
# the "Temperature" and "Time" columns manually)
spreadsheet_key = ''

worksheet_id = 'od6'

#serial port - can use glob wildcards (e.g. *) - change to suit your OS.
serial_port_search_str = '/dev/tty.usbmodem*'

# --- configuration above this line ---

#check configuration
if (len(spreadsheet_key) <= 0 or len(worksheet_id) <= 0):
    print >> sys.stderr, "Spreadsheet key and/or worksheet id missing: please run spreadsheetFinder.py and copy/paste the key/id into the tmp102livelogger.py file."
    exit(1)

#ask the user for his/her password
client.password = getpass.getpass('Enter the password for '
                                  + client.email + ": ")
try:
    print "Logging in..."
    client.ProgrammaticLogin()
except BadAuthentication:
    print >> sys.stderr, "Incorrect username/password."
    exit(1)
except CaptchaRequired:
    print >> sys.stderr, "Captcha required. (This is currently not supported)"
    exit(1)
except Error:
    print >> sys.stderr, "Other login error."
    exit(1)

print "Authentication successful."

try:
    #open logfile in append mode.
    f = open(time.strftime("temp_%d.%m.%Y.log"), 'a')

# this code could create a google doc - in a future version.
#    doc = client.Create(gdata.docs.data.SPREADSHEET_LABEL,
#                        time.strftime("temp_%d.%m.%Y.log"))

    #find a serial port to use.
    print "Searching for serial port..."

    #the next line searches for an appropriate serial port. see
    #see http://mbed.org/handbook/SerialPC
    ports = glob.glob(serial_port_search_str)	#change if not on OS X.

    port = ""	#the serial port to use.
    if(len(ports) <= 0):
        print >> sys.stderr, "No serial port found!"
        exit(1)
    elif(len(ports) == 1):
        #only 1 choice - let's go for it.
        port = ports[0]
        print "Using serial port ", port
    else:
        print >> sys.stderr, """multiple serial ports found.
This feature hasn't been implemented yet.
Please enter the full path to your serial port, e.g. /dev/tty.usbmodem612 rather than using globbing."""
        exit(1)

    ser = serial.Serial(port)

    while(True):
        ser.write('u')
        temp = ser.readline().strip()
        t = time.strftime("%d.%m.%Y-%H:%M")

        #use american time format for google docs spreadsheet.
        t_american = time.strftime("%m/%d/%Y %H:%M")
        f.write(t + " " + temp + '\n')
        print t, temp
        f.flush()
        #write online, too. - NB: use LOWER CASE column id's
        row = {'time' : t_american, 'temperature': temp}
#        print "writing:",row
        entry = client.InsertRow(row, spreadsheet_key, worksheet_id)
        if (not isinstance(entry, gdata.spreadsheet.SpreadsheetsList)):
            print >>sys.stderr, "Error: Failed to insert:", row 
        time.sleep(60)


except KeyboardInterrupt:
    print "Keyboard interrupt received, quitting..."

finally:
    ser.close()
    f.close()
