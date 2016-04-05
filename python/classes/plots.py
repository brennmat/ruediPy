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

import time
from classes.misc	import misc
import matplotlib
matplotlib.use('GTKAgg') # use this for faster plotting
import matplotlib.pyplot as plt
import numpy as numpy

class plots:


	########################################################################################################
	

	def __init__(self,max_trend_points = 500):
		'''
		PLOTS.__init__(max_trend_points = 500)
		
		Initialize PLOTS object.
		
		INPUT:
		max_trend_points (optional): max. number of data points in the trend plot. Once this limit is reached, old data points will be removed from the plot. Default value: max_trend_points = 500
		
		OUTPUT:
		(none)
		'''
		
		# SCAN figure
		self.scanfig = plt.figure()
		plt.ion()
		plt.show()
		
		# TREND figure:
		self.trendfig = plt.figure()
		plt.ion()
		plt.show()

		self._trenddata_t = numpy.array([])
		self._trenddata_mz = numpy.array([])
		self._trenddata_intens = numpy.array([])
		self._trenddata_max_len = max_trend_points

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
		plt.title('SCAN DATA')

		plt.draw()
		# plt.show()

	########################################################################################################
	

	def trend_add_data(self,t,mz,intens):
		"""
		plots.trend_add_data(t,mz,intens)
		
		Add data to trend plot (but don't update the trend plot)
		
		INPUT:
		t: epoch time
		mz: mz values (x-axis)
		intens: intensity values (y-axis)
		
		OUTPUT:
		(none)
		"""
				
		self._trenddata_t = numpy.append( self._trenddata_t , t )
		self._trenddata_mz = numpy.append( self._trenddata_mz , mz )
		self._trenddata_intens = numpy.append( self._trenddata_intens , intens )
		
		N = self._trenddata_max_len
		if self._trenddata_t.shape[0] > N:
			self._trenddata_t 		= self._trenddata_t[-N:]
			self._trenddata_mz 		= self._trenddata_mz[-N:]
			self._trenddata_intens	= self._trenddata_intens[-N:]


	########################################################################################################
	

	def trend_update_plot(self):
		"""
		plots.trend_update_plot(t,mz,intens)
		
		Update the trend plot (e.g. after adding data)
		NOTE: updating the plot may be slow, and it may therefore be a good idea to keep the update interval low to avoid affecting the duty cycle.
		
		INPUT:
		(none)
		
		OUTPUT:
		(none)
		"""
		
		MZ = numpy.unique(self._trenddata_mz) # unique list of all mz values
		
		colors = ('b', 'g', 'r', 'c', 'm', 'y', 'k')
		
		plt.figure(self.trendfig.number)
		c = 0
		t0 = time.time()

		plt.show(block=False)
		
		for mz in MZ:
			k = numpy.where( self._trenddata_mz == mz )[0]
			col = colors[c%7]
			c = c+1
			plt.plot( self._trenddata_t[k] - t0 , self._trenddata_intens[k] , col + 'o-' )
			plt.hold(True)

		plt.hold(False)
		plt.title('TREND DATA')
		plt.xlabel('Time (s)')
		plt.ylabel('Intensity')
		plt.yscale('log')
		plt.draw()
		
