#!/usr/bin/python
"""Energy Monitor
Battery energy monitor/discharger
"""
 
import time
from flask import Flask, render_template, request
import datetime
import os
import sys
import csv
import RPi.GPIO as GPIO
import threading

from MCP3208 import MCP3208, MCP3208Error

# Functions to read hardware

def readadc(adcnum):
    # read SPI data from the MCP3208, 8 channels in total
    data = MCP3208_ADC.get(adcnum)
    return data

def voltage():
    # Measure the voltage
    voltage_value = readadc(voltage_channel)
    measured_voltage = voltage_value * Vref / 4096
    voltage = measured_voltage * (RgndV + RfeedV) / RgndV * Vin / Vcalibration
    return voltage

def current():
     # Measure the current
     global zero_current
     current_value = readadc(current_channel)
     current_voltage = current_value * Vref / 4096
     ACS = current_voltage * (RgndI + RfeedI) / RgndI
     if status == "Off":
         zero_current=ACS
     current_offset = ACS - zero_current
     current = current_offset * 1000 / sensitivity * Iin / Icalibration
     return current


# Test the hardware


def hardware_test():
     global status
     global zero_current

     test_wait = 4 # Number of seconds between each state change
     print("Hardware test.")
     print("Both relays open - expect the voltage to be 0V")
     print("Voltage = " + "{:-.2f}".format(voltage()) + "V")
     time.sleep(test_wait)
     print("")
     
     print("Connecting battery...")
     GPIO.output(battery_relay_pin, GPIO.HIGH)
     time.sleep(test_wait)
     print("Battery voltage = " + "{:-.2f}".format(voltage()) + "V")
     time.sleep(test_wait)
     print("")
     
     print("Disconnecting battery...")
     GPIO.output(battery_relay_pin, GPIO.LOW)
     time.sleep(test_wait)
     print("")

     print("Connecting load...")
     GPIO.output(load_relay_pin, GPIO.HIGH)
     time.sleep(test_wait)
     print("Load voltage = " + "{:-.2f}".format(voltage()) + "V")
     time.sleep(test_wait)
     print("")
     
     print("Disconnecting load...")
     GPIO.output(load_relay_pin, GPIO.LOW)
     time.sleep(test_wait)
     print("")

     print("Calibrating zero current...")
     print("The result should be 0.00A!")
     print("Zero current = " + "{:-.2f}".format(current()) + "A")
     time.sleep(test_wait)
     print("")

     print("Connecting battery to load...")
     GPIO.output(battery_relay_pin, GPIO.HIGH)
     GPIO.output(load_relay_pin, GPIO.HIGH)
     status = "On"
     time.sleep(test_wait)
     print("")

     print("Measuring load current...")
     print("Load current = " + "{:-.2f}".format(current()) + "A")
     print("Voltage = " + "{:-.2f}".format(voltage()) + "V")
     time.sleep(test_wait)
     print("")

     print("Disconnecting battery from load...")
     GPIO.output(battery_relay_pin, GPIO.LOW)
     GPIO.output(load_relay_pin, GPIO.LOW)
     status = "Off"
     time.sleep(test_wait)
     print("")


app = Flask(__name__) # Start webpage

# Initialisation
test_hardware = "Disabled"

# Read any command line parameters

total = len(sys.argv)
cmdargs = str(sys.argv)
for i in range(total):
     if (str(sys.argv[i]) == "--test-hardware"):
          test_hardware = "Enabled"


# Define Variables
delay = 1.0

# ADC connections
cs_pin = 31
clock_pin = 23
data_out_pin = 19
data_in_pin = 21

# Voltage Monitoring
voltage_channel = 0
RgndV = 220 #ohms - Resistor from channel 0 to ground
RfeedV = 1000 #ohms - Resistor from channel 0 to positive battery terminal
Vref = 3.0 #volts
Vcalibration = 12.12 #V measured for 12V input. Set same as Vin to remove calibration
Vin = 12 #V for calibration


# Current Monitoring
current_channel = 1
RgndI = 10000 #ohms - Resistor from channel 1 to ground
RfeedI = 4700 #ohms - Resistor from channel 1 to ACS712 Vout
sensitivity = 185 #mV/A ACS712x05B
zero_current = 2.5 #V
Icalibration = 1.5 #V measured for 1.5A load. Set same as Iin to remove calibration
Iin = 1.5 #V for calibration

# Battery Discharge
minimum_battery_voltage = 10.8 #V - Lead Acid 12V battery
energy = 0 #Ah

# Relay
load_relay_pin = 38 # Header pin number for load control relay
battery_relay_pin = 40 # Header pin number for battery control relay
GPIO.setmode(GPIO.BOARD)
GPIO.setup(load_relay_pin, GPIO.OUT)
GPIO.output(load_relay_pin, GPIO.LOW)
GPIO.setup(battery_relay_pin, GPIO.OUT)
GPIO.output(battery_relay_pin, GPIO.LOW)

# Display
title = "Battery energy monitor"
status = "Off"
duration = 0

# Logging
log_file = "Yes" # Yes to log to a CSV file. Any other value to not log
# Find directory of the program
dir = os.path.dirname(os.path.abspath(__file__))

# Create SPI
MCP3208_ADC = MCP3208(cs_pin, clock_pin, data_in_pin, data_out_pin, GPIO.BOARD)

if (test_hardware == "Enabled"):
     hardware_test()

     GPIO.cleanup()
     exit()



# Flask web page code

@app.route('/')
def index():
     global title
     global status
     global zero_current
    
     now = datetime.datetime.now()
     timeString = now.strftime("%H:%M on %d-%m-%Y")
         
     if status == "On":
          state = "Discharging"
     else:
          state = "Inactive"
     templateData = {
                     'title' : title,
                     'time': timeString,
                     'state' : state,
                     'voltage' : '{:-.2f}'.format(voltage()),
                     'current' : '{:-.2f}'.format(current()),
                     'energy' : '{:-.4f}'.format(energy),
                     'duration' : (duration)   # '{:%Y-%m-%d %H:%M:%S}'.format
                     }
     return render_template('main.html', **templateData)

@app.route("/", methods=['POST'])   # Seems to be run regardless of which page the post comes from
def log_button():
     global status
     if request.method == 'POST':
          # Get the value from the submitted form  
          submitted_value = request.form['State']
          if submitted_value == "Start":
               if (status == "Off"):
                    if voltage() > minimum_battery_voltage:
                        status = "On"
                        GPIO.output(load_relay_pin, GPIO.HIGH)
                        EnergyThread().start()
                     
          if submitted_value =="Stop":   
               if (status == "On"):
                    status = "Off"
                    GPIO.output(load_relay_pin, GPIO.LOW)
     return index()

@app.route('/confirm')
def confirm():
     templateData = {
                'title' : title
                }
     return render_template('confirm.html', **templateData)

@app.route('/shutdown')
def shutdown():
     command = "/usr/bin/sudo /sbin/shutdown +1"
     import subprocess
     process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
     output = process.communicate()[0]
     print output
     templateData = {
                'title' : title
                }
     return render_template('shutdown.html', **templateData)

@app.route('/cancel')
def cancel():
     command = "/usr/bin/sudo /sbin/shutdown -c"
     import subprocess
     process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
     output = process.communicate()[0]
     print output

     return index()

class EnergyThread ( threading.Thread ):

     def run ( self ):
          global status
          global energy
          global duration
          
          # Work out how much energy until the battery is discharged
          
          start = datetime.datetime.now()
          if log_file == "Yes":
              filetime = start.strftime("%Y-%m-%d-%H-%M")
              filename=dir+'/logging/'+filetime+'_energy_log.csv'
              with open(filename, 'ab') as csvfile:
                   # Create a header row in a CSV file
                   logfile = csv.writer(csvfile, delimiter=',', quotechar='"')
                   row = ["Date-Time"] # Key parameters from web display
                   row.append("Voltage")
                   row.append("Current")
                   row.append("Energy")
                   row.append("Interval") # Diagnostics
                   row.append("Interval Energy")
                   logfile.writerow(row)

          energy = 0 # Reset the energy count each time
          last = start # Start the interval time count
          time.sleep(delay)

          while status == "On":
              # Calculate the cumulative energy
              now = datetime.datetime.now()
              interval = now-last
              interval_secs = interval.total_seconds() # Work out how long since the last measurement
              current_now = current()
              interval_energy = current_now * interval_secs / 3600
              energy = energy + interval_energy # Add the energy (ampere-hours) since in the last interval

              duration = now-start # Work out how long the discharge has been going
              last = now
              voltage_now = voltage()
              if voltage_now < minimum_battery_voltage:
                  status = "Off"
                  GPIO.output(load_relay_pin, GPIO.LOW)
              if log_file == "Yes":
                  with open(filename, 'ab') as csvfile:
                        logfile = csv.writer(csvfile, delimiter=',', quotechar='"')
                        row = [now.strftime("%d/%m/%Y %H:%M:%S.%f")]
                        row.append(voltage_now)
                        row.append(current_now)
                        row.append(energy)
                        row.append(interval_secs)
                        row.append(interval_energy)
                        logfile.writerow(row)


              time.sleep(delay)


if __name__ == '__main__':
     app.run(debug=True, host='0.0.0.0')
     
