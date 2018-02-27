# testing communication with OMEGA pressure transducer ( PX409-USBH Series )

# open and configure serial port for communication with OMEGA sensor (115200 baud, 8 data bits, no parity, 1 stop bit

import serial

serialport = '/dev/cu.usbserial-487740' # Mac OS X

ser = serial.Serial(
	port     = serialport,
	baudrate = 115200,
	parity   = serial.PARITY_NONE,
	stopbits = serial.STOPBITS_ONE,
	bytesize = serial.EIGHTBITS,
	timeout  = 5.0
)

# try to get the serial number from the sensor:
ser.write(('SNR\r').encode('utf-8')) # send command to serial port
ans =  ser.readline() # read response
print (ans)

# try to get a pressure reading from the sensor:
ser.write(('P\r').encode('utf-8')) # send command to serial port
ans =  ser.readline() # read response
ans = ans.decode('utf-8').split(' ')

p = ans[0]
if p[0] == '>':
	p = p[1:]
p = float( p )

unit = ans[1]
if unit != 'bar':
	error ('Expected unit = bar!!!')
else:
	# convert to mbar = hPa:
	p = 1000 * p
	unit = 'hPa'

print(str(p) + unit)
# p = int(ans.decode('utf-8').rstrip().split('=')[1]) # parse response to integer number
