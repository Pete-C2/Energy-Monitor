#!/usr/bin/python
"""Energy Monitor
Battery energy monitor/discharger
"""
 
import spidev
import time
from flask import Flask, render_template, request
import datetime

app = Flask(__name__)

# Define Variables
delay = 1.0

# Voltage Monitoring
voltage_channel = 0
RgndV = 180 #ohms - Resistor from channel 0 to ground
RfeedV = 1000 #ohms - Resistor from channel 0 to positive battery terminal
Vref = 3.3 #volts
Vcalibration = 12.65 #V measured for 12V input
Vin = 12 #V for calibration


# Current Monitoring
current_channel = 1
RgndI = 3900 #ohms - Resistor from channel 1 to ground
RfeedI = 1800 #ohms - Resistor from channel 1 to ACS712 Vout
sensitivity = 185 #mV/A ACS712x05B
zero_current = 2.5 #V
Icalibration = 1.3 #V measured for 1.5A load
Iin = 1.5 #V for calibration

# Battery Discharge
minimum_battery_voltage = 10.8 #V - Lead Acid 12V battery
energy = 0 #Ah

# Display
title = "Battery energy monitor"
status = "Off"

# Create SPI
spi = spidev.SpiDev()
spi.open(0, 0)

def readadc(adcnum):
    # read SPI data from the MCP3008, 8 channels in total
    if adcnum > 7 or adcnum < 0:
        return -1
    r = spi.xfer2([1, 8 + adcnum << 4, 0])
    data = ((r[1] & 3) << 8) + r[2]
    return data


# Flask web page code

@app.route('/')
def index():
     global title
     global status
     global zero_current
    
     now = datetime.datetime.now()
     timeString = now.strftime("%H:%M on %d-%m-%Y")
     
     # Measure the voltage
     voltage_value = readadc(voltage_channel)
     measured_voltage = voltage_value * Vref / 1024
     voltage = measured_voltage * (RgndV + RfeedV) / RgndV * Vin / Vcalibration

     # Measure the current
     current_value = readadc(current_channel)
     current_voltage = current_value * Vref / 1024
     ACS = current_voltage * (RgndI + RfeedI) / RgndI
     if status == "Off":
         zero_current=ACS
     current_offset = ACS - zero_current
     current = current_offset * 1000 / sensitivity * Iin / Icalibration
    
     if status == "On":
          state = "Discharging"
     else:
          state = "Inactive"
     templateData = {
                     'title' : title,
                     'time': timeString,
                     'state' : state,
                     'voltage' : '{:-.2f}'.format(voltage),
                     'current' : '{:-.2f}'.format(current)
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
                    status = "On"
                     
          if submitted_value =="Stop":   
               if (status == "On"):
                    status = "Off"
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

if __name__ == '__main__':
     app.run(debug=True, host='0.0.0.0')
     
