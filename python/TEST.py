from classes.rgams		import rgams
from classes.selectorvalve	import selectorvalve
import matplotlib.pyplot as plt

# initialize instrument objects:
MS     = rgams('/dev/ttyUSB4') 	 			# init RGA / MS
VALVE  = selectorvalve('/dev/ttyUSB3')		# init VICI selector valve

# print some MS information:
print 'MS has electron multiplier: ' + MS.hasMultiplier()
print 'MS max m/z range: ' + MS.mzMax()

# change MS configuraton:
MS.setElectronEnergy(60)
print 'Ionizer electron energy: ' + MS.getElectronEnergy() + ' eV'
print 'Set ion beam to Faraday detector...'
MS.setDetector('F')
MS.filamentOn() # turn on with default current
print 'Filament current: ' + MS.getFilamentCurrent() + ' mA'
MS.setFilamentCurrent(0.8)
print 'Filament current: ' + MS.getFilamentCurrent() + ' mA'

# get scan data:
print 'Scanning... '
m,s,unit = MS.scan(38,42,15)

# turn off filament:
MS.filamentOff()
print 'Filament current: ' + MS.getFilamentCurrent() + ' mA'

# plot scan data:
plt.plot(m,s)
plt.xlabel('m/z')
plt.ylabel('Ion current (' + unit +')')
plt.show()

# change valve positions:
VALVE.setpos(1)
print 'Valve position is ' + (VALVE.getpos())
VALVE.setpos(2)
print 'Valve position is ' + (VALVE.getpos())
VALVE.setpos(3)
print 'Valve position is ' + (VALVE.getpos())
