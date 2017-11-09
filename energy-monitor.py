#!/usr/bin/python
"""Energy Monitor
Battery energy monitor/discharger
"""
 
import spidev
import time
import datetime

# Define Variables
delay = 1.0

# Voltage Monitoring
voltage_channel = 0
RgndV = 180 #ohms - Resistor from channel 0 to ground
RfeedV = 1000 #ohms - Resistor from channel 0 to positive battery terminal
Vref = 3.3 #volts

# Current Monitoring
current_channel = 1
RgndI = 3900 #ohms - Resistor from channel 1 to ground
RfeedI = 1800 #ohms - Resistor from channel 1 to ACS712 Vout
sensitivity = 185 #mV/A ACS712x05B
zero_current = 2.5 #V

# Battery Discharge
minimum_battery_voltage = 10.8 #V - Lead Acid 12V battery
energy = 0 #Ah

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
    
   
while True:
    # Measure the voltage
    voltage_value = readadc(voltage_channel)
    measured_voltage = voltage_value * Vref / 1024
    voltage = measured_voltage * (RgndV + RfeedV) / RgndV

    # Measure the current
    current_value = readadc(current_channel)
    current_voltage = current_value * Vref / 1024
    ACS = current_voltage * (RgndI + RfeedI) / RgndI
    current_offset = ACS - zero_current
    current = current_offset * 1000 / sensitivity

    # Calculate the cumulative energy
    energy = energy + (current * delay / 3600)
    
    print "---------------------------------------"
    print("Voltage Value: %d" % voltage_value)
    print("Measured voltage: %f" % measured_voltage)
    print("Voltage %f" % voltage)
    print "--"
    print("Current Value: %d" % current_value)
    print("Measured voltage: %f" % current_voltage)
    print("ACS Voltage: %f" % ACS)
    print("Current offset: %f" % current_offset)
    print("Current A: %f" % current)
    print "--"
    print("Energy Ah: %f" % energy)
    
    
    time.sleep(delay)
