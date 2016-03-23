from classes.rgams import rgams

# initialize instrument:
MS     = rgams('/dev/ttyUSB4') 	 # init RGA / MS

# turn filament on (to default current):
MS.param_IO('FL*')
print MS.param_IO('FL?')

# turn filament off:
MS.param_IO('FL0')
print MS.param_IO('FL?')