# Code for the misc class
# 
#
# Copyright 2016, Matthias Brennwald (brennmat@gmail.com) and Yama Tomonaga
# 
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

import time

class misc:

	
	########################################################################################################
	

	@staticmethod
	def nowString():
		# return string with current date and time
		return time.strftime("%Y-%m-%d %H:%M:%S")

	
	########################################################################################################
	

	@staticmethod
	def nowUNIX():
		# return date/time as UNIX time / epoch (seconds after Jan 01 1970 UTC)
		return time.time()

	
	########################################################################################################
	

	@staticmethod
	def warnmessage(unit,msg):
		# print a warning message
		# unit: name of part/unit of the instrument, e.g. unit = 'RGA'
		# msg: warning message
		M = '***** WARNING from ' + unit + ' at ' + misc.nowString() + ': ' + msg
		print (M)
		