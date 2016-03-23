from classes.rgams			import rgams
from classes.selectorvalve	import selectorvalve

# initialize instrument objects:
MS     = rgams('/dev/ttyUSB4') 	 			# init RGA / MS
VALVE  = selectorvalve('/dev/ttyUSB3')		# init VICI selector valve

print 'MS has electron multiplier: ' + MS.hasMultiplier()
print 'MS max m/z range: ' + MS.mzMax()

MS.setElectronEnergy(60)
print 'Ionizer electron energy: ' + MS.getElectronEnergy() + ' eV'

print 'Set ion beam to Faraday detector...'
MS.setDetector('F')

MS.filamentOn() # turn on with default current
print 'Filament current: ' + MS.getFilamentCurrent() + ' mA'
MS.setFilamentCurrent(0.8)
print 'Filament current: ' + MS.getFilamentCurrent() + ' mA'

print 'Scanning... '
print MS.scan(20,40,15)

MS.filamentOff()
print 'Filament current: ' + MS.getFilamentCurrent() + ' mA'

# change valve positions:
VALVE.setpos(1)
print 'Valve position is ' + (VALVE.getpos())
VALVE.setpos(2)
print 'Valve position is ' + (VALVE.getpos())
VALVE.setpos(3)
print 'Valve position is ' + (VALVE.getpos())
