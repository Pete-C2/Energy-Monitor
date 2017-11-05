#!/usr/bin/python
 
import spidev
import time

#Define Variables
delay = 0.5
voltage_channel = 0
Rgnd = 180 #ohms
Rfeed = 1000 #ohms
Vref = 3.3 #volts

#Create SPI
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
    voltage_value = readadc(voltage_channel)
    measured_voltage = voltage_value * Vref / 1024
    voltage = measured_voltage * (Rgnd + Rfeed) / Rgnd
    
    print "---------------------------------------"
    print("Voltage Value: %d" % voltage_value)
    print("Measured voltage: %f" % measured_voltage)
    print("Voltage %f" % voltage)
    time.sleep(delay)
