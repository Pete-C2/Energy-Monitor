# Energy-Monitor
Energy monitor to determine DC energy. This will be used to calculate the capacity of a battery and stop discharge at the end of battery life.

Requires:
- The [GPIO Library](https://code.google.com/p/raspberry-gpio-python/) (Already on most Raspberry Pi OS builds).
- The [MCP3208 Library](https://github.com/Pete-C2/MCP3208).
- The [Flask web server](https://www.raspberrypi.org/learning/python-web-server-with-flask/worksheet/). Install command:
  - sudo apt-get install python3-flask
- A [Raspberry Pi](http://www.raspberrypi.org/).
- Hardware:
  - [MCP3208 ADC](http://www.microchip.com/wwwproducts/en/mcp3208), connected as per [Raspberry Pi ADC: MCP3008 Analog to Digital Converter](https://pimylifeup.com/raspberry-pi-adc/). Resistive divider (1k/220 ohm) to enable a maximum voltage of 20V to be applied to channel 0. 
  - [ACS712ELCTR-05B-T Current sensor](http://www.allegromicro.com/en/Products/Current-Sensor-ICs/Zero-To-Fifty-Amp-Integrated-Conductor-Sensor-ICs/ACS712.aspx) connected to channel 1. Resistive divider on Vout (4k7/10k) plus buffer op-amp to interface the 5V output to the 3.3V ADC input. Suggest a load for a car battery of 12V/55W car halogen bulb to provide a load (4.6A, just within the maximum for the current sensor). The current sensor is a high current device (noise on the output is about 100mA). The noise will probably get averaged out over the duration of a battery discharge but the current probably needs to be kept above 1A or so.
  - [3.3V switched relay](https://www.amazon.co.uk/raspberry-pi-relay/s?ie=UTF8&page=1&rh=i%3Aaps%2Ck%3Araspberry%20pi%20relay). There are many sources. Ensure that it can switch at least 5A. Active high output connects power input to load. Ensure that the switched load is on the output side of the monitoring - voltage monitoring must always take place. This can be achieved using a transistor to drive the relay board, which may be required anyway. An example is https://www.raspberrypi.org/forums/viewtopic.php?t=36225(https://www.raspberrypi.org/forums/viewtopic.php?t=36225)

Installation:
- Copy files to a folder on the Raspberry Pi.
- Enable SPI in Raspberry Pi Configuration
- Edit /etc/rc.local to autorun application:
   - sudo nano /etc/rc.local
   - Add: python /home/pi/.../energy-monitor.py where ... is the location of your file.
- Edit connections and/or resistor values and/or component settings to define your system hardware. The defaults match my hardware.
- Edit calibration values to ensure that your system is accurate. I used an adjustable 12V PSU and 21W car bulb to set the calibration points.
    
Recommendations (to make life easier):
- Set a [static IP address](https://www.modmypi.com/blog/tutorial-how-to-give-your-raspberry-pi-a-static-ip-address).
- Define a [hostname](http://www.simonthepiman.com/how_to_rename_my_raspberry_pi.php).
- Create a [fileshare](http://raspberrypihq.com/how-to-share-a-folder-with-a-windows-computer-from-a-raspberry-pi/).
- Install [VNC](https://www.raspberrypi.org/documentation/remote-access/vnc/) for full headless access.

## Use

See wiki.

## Changelog

### V2.0

Modified for new hardware.

### V1.0

Added CSV logging of results.

### V0.4

Added control of relay.

Added energy measurement until battery discharged.

### V0.3

Added web display of voltage and current.

Added zero current setting.

Added calibration of voltage and current.

### V0.2

Added measurement of current.

### V0.1

Initial trial code.

Measures voltage of input
