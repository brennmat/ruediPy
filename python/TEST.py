from classes.rgams			import rgams
from classes.selectorvalve	import selectorvalve

# initialize instrument:
MS     = rgams('/dev/ttyUSB4') 	 # init RGA / MS
VALVE  = selectorvalve('/dev/ttyUSB3') 	 # init VICI selector valve

# turn filament on (to default current):
MS.param_IO('FL*')
print 'Turned on filement: current = ' + MS.param_IO('FL?') + ' mA'

# turn filament off:
MS.param_IO('FL0')
print 'Turned off filement: current = ' + MS.param_IO('FL?') + ' mA'

# change valve positions:
VALVE.setpos(1)
print 'Valve position is ' + (VALVE.getpos())
VALVE.setpos(2)
print 'Valve position is ' + (VALVE.getpos())
VALVE.setpos(3)
print 'Valve position is ' + (VALVE.getpos())