# Code for the plots class
# 
# DISCLAIMER:
# This file is part of ruediPy, a toolbox for operation of RUEDI mass spectrometer systems.
# 
# ruediPy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# ruediPy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with ruediPy.  If not, see <http://www.gnu.org/licenses/>.
# 
# ruediPy: toolbox for operation of RUEDI mass spectrometer systems
# Copyright (C) 2016  Matthias Brennwald
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2016, Matthias Brennwald (brennmat@gmail.com) and Yama Tomonaga

### # import time
### import os
### from os.path 		import expanduser
### 

from classes.misc	import misc
import matplotlib.pyplot as plt
import numpy as numpy

class plots:


	########################################################################################################
	

	def __init__(self):
		'''
		PLOTS.__init__()
		
		Initialize PLOTS object.
		
		INPUT:
		(none)
		
		OUTPUT:
		(none)
		'''
		
		self.scanfig = plt.figure()
		plt.ion()
		# plt.plot([1.6, 2.7])
		plt.title('SCAN DATA')
		plt.xlabel('m/z')
		plt.ylabel('Intensity')
		plt.hold(False)
		plt.show()
		plt.draw()

		self.trendfig = plt.figure()
		plt.ion()
		# plt.plot([1.6, 2.7])
		plt.title('TREND DATA')
		plt.xlabel('Time')
		plt.ylabel('Intensity')
		plt.hold(False)
		plt.yscale('log')
		plt.show()
		plt.draw()
		
		self._trenddata_t = numpy.array([])
		self._trenddata_mz = numpy.array([])
		self._trenddata_intens = numpy.array([])


		misc.warnmessage('PLOTS','Scan figure initialized!')


	########################################################################################################
	

	def scan(self,mz,intens,unit):
		"""
		plots.scan(mz,intens,unit)
		
		Plot scan data
		
		INPUT:
		mz: mz values (x-axis)
		intens: intensity values (y-axis)
		unit: intensity unit (string)
		
		OUTPUT:
		(none)
		"""
		
		plt.figure(self.scanfig.number)
		plt.plot(mz,intens)
		plt.xlabel('m/z')
		plt.ylabel('Intensity (' + unit +')')
		plt.show()
		plt.draw()
		

	########################################################################################################
	

	def trend(self,t,mz,intens,unit):
		"""
		plots.trend(mz,intens,unit)
		
		Plot trend data
		
		INPUT:
		t: epoch time
		mz: mz values (x-axis)
		intens: intensity values (y-axis)
		unit: intensity unit (string)
		
		OUTPUT:
		(none)
		"""
		
		self._trenddata_t = numpy.append( self._trenddata_t , t )
		self._trenddata_mz = numpy.append( self._trenddata_mz , mz )
		self._trenddata_intens = numpy.append( self._trenddata_intens , intens )
		#self._trenddata_mz.append( mz );
		#self._trenddata_intens.append( intens );
		
		MZ = numpy.unique(self._trenddata_mz) # unique list of all mz values
		
		colors = ('b', 'g', 'r', 'c', 'm', 'y', 'k')
		
		plt.figure(self.trendfig.number)
		plt.hold(True)
		c = 0
		for mz in MZ:
			k = numpy.where( self._trenddata_mz == mz )[0]
			col = colors[c%7]
			c = c+1
			plt.plot(self._trenddata_t[k],self._trenddata_intens[k],col + 'o-')
		plt.hold(False)
						
		plt.ylabel('Intensity (' + unit +')')
		plt.show()
		plt.draw()
