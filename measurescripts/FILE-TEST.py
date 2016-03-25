# make shure Python knows where to look for the RUEDI Python code
# http://stackoverflow.com/questions/4580101/python-add-pythonpath-during-command-line-module-run
# Example (bash): export PYTHONPATH=~/ruedi/python

from classes.datafile	import datafile
from classes.misc		import misc
import random

# initialize instrument objects:
DATAFILE  = datafile('~/ruedi/data') # init object for data files

k = 0
while k < 10:
	DATAFILE.next() # start a new data file
	j = 0
	while j < 100:
		DATAFILE.writePeak(40,random.random(),'A',0.135,misc.nowUNIX())
		j = j+1	
	k = k + 1
	
DATAFILE.close() # close last datafile