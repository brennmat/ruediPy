# testing communication with OMEGA pressure transducer ( PX409-USBH Series )

# open and configure serial port for communication with OMEGA sensor (115200 baud, 8 data bits, no parity, 1 stop bit

serialport = '/dev/cu.XXXX' # Mac OS X

ser = serial.Serial(
	port     = serialport,
	baudrate = 115200,
	parity   = serial.PARITY_NONE,
	stopbits = serial.STOPBITS_ONE,
	bytesize = serial.EIGHTBITS,
	timeout  = 5.0
)

# try to get the serial numer from the sensor:
ser.write(('SNR\r').encode('utf-8')) # send command to serial port
ans =  ser.readline() # read response
print (ans)
