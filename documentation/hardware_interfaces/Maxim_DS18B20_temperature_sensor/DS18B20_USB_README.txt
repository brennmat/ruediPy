USING THE MAXIM DS18B20 ON USB PORT

MATERIAL
- DS18B20 temperature sensor in water proof probe with cable (e.g., Boxtec: Onewire Temperature Sensor (DS18B20) 2m (47120))
- USB / TTL converter Prolific PL2303TA

CONNECTIONS
- See photos (OVERVIEW.jpg and CLOSEUP.jpg)
- The red wire on the USB converter is not used
- TXD and RXD (green and white) on USB converter joined together, then connected to DATA wire on DS18B20 (blue)
- Connect GND connections of DS18B20 and USB converter (black wires)
- Red wire on DS18B20 is not used (MAYBE CONNECT THIS TO GND TO SUPPRESS NOISE AND IMPROVE COMMUNICATION BETWEEN COMPUTER AND SENSOR!)
- Maybe also see http://www.instructables.com/id/Quick-Digital-Thermometer-Using-Cheap-USB-to-TTL-C/step1/Hardware-connections-between-DS18B20-DS-and-USB-to/

SOFTWARE
- use digitemp on Linux

