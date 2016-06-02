#!/usr/bin/env python

import inspect

from classes.rgams_SRS.py		      import rgams_SRS
from classes.selectorvalve_VICI.py    import selectorvalve_VICI
from classes.pressuresensor_WIKA.py   import pressuresensor_WIKA
from classes.datafile			      import datafile
from classes.misc.py			      import misc

CLASSES = [ rgams_SRS , selectorvalve_VICI , pressuresensor_WIKA , datafile , misc ]
CLASSES = [ selectorvalve_VICI , pressuresensor_WIKA , datafile , misc ]

for X in CLASSES:
	print 'Class "' + X.__name__ + '"'
	P = inspect.getsourcefile(X)
	print 'File: ' + P[P.find('ruedi'):0]
	print inspect.getdoc(X)
	
	for name, data in inspect.getmembers(X):
		if name == '__builtins__':
			continue
		if name == '__doc__':
			continue
		if name == '__init__':
			continue
		if name == '__module__':
			continue
		print name

	print "\n ****** \n"