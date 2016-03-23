from classes.rgams import rgams

# initialize instrument:
MS     = rgams('/dev/ttyUSB4') 	 # init RGA / MS

# turn filament on (to default current):
MS.param_IO('FL*')
print 'Turned on filement: current = ' + MS.param_IO('FL?') + ' mA'

# turn filament off:
MS.param_IO('FL0')
print 'Turned off filement: current = ' + MS.param_IO('FL?') + ' mA'