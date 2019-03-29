USING THE MAXIM DS18B20 ON USB PORT

MATERIAL
- DS18B20 temperature sensor in water proof probe with cable (e.g., Boxtec: Onewire Temperature Sensor (DS18B20) 2m (47120))
- USB / TTL converter such as FTDI TTL-232R-RPI (Distrelec Nr. 110-51-732). Prolific PL2303TA also works ok, but does not have unique USB ID, so multiple USB interfaces can be hard to distinguish.

CONNECTIONS (color codes as with PROLIFIC PL2303TA, FTDI or other may have different color coding. Black is usually black, and that's enough to get the connections right)
- See photos (OVERVIEW.jpg and CLOSEUP.jpg)
- The red wire (5V) on the USB converter is not used. The DS18B20 "steals" power from the data line (so-called parasitic mode)
- TXD and RXD (green and white) on USB converter joined together, then connected to DATA wire on DS18B20 (blue)
- Connect GND connections of DS18B20 and USB converter (black wires)
- To prevent the supply pin of the DS18B20 from flating, the red wire on DS18B20 is must be connected to GND (black wires). The DS18B20 may work with the red wire unconnected/flotating, but it won't be reliable, and it will produce communication errors or false temperature readings (+85 deg.C values).
- See also see http://www.instructables.com/id/Quick-Digital-Thermometer-Using-Cheap-USB-to-TTL-C/step1/Hardware-connections-between-DS18B20-DS-and-USB-to/

	**** USB converter ****			   **** DS18B20 ****
	5V (red) -- not connected
	TXD + RXD (green + white) joined   <--->   data pin (blue)
	GND (black)                        <--->   GND (black) and supply pin (red) joined together



SOFTWARE
- use digitemp on Linux; example:
	>> digitemp_DS9097 -i -s /dev/ttyUSB3             <-- configure sensor (attached via /dev/ttyUSB3)
	>>  digitemp_DS9097 -a -n 100 /dev/ttyUSB3        <-- get a bunch of temperature readings
- use Python package "pydigitemp" with the >> DS18B20 << class (the DS1820 class does not work with the DS18B20!)

