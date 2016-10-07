# Code for the misc class
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
import sys

class misc:
	"""
	ruediPy class with helper functions.
	"""
	
	########################################################################################################
	

	@staticmethod
	def now_string():
		'''
		dt = misc.now_string()

		Return string with current date and time
		
		INPUT:
		(none)
		
		OUTPUT:
		dt: date-time (string) in YYYY-MM-DD hh:mm:ss format
		'''
		
		return time.strftime("%Y-%m-%d %H:%M:%S")

	
	########################################################################################################
	

	@staticmethod
	def now_UNIX():
		'''
		dt = misc.now_UNIX()
		
		Return date/time as UNIX time / epoch (seconds after Jan 01 1970 UTC)
		
		INPUT:
		(none)
		
		OUTPUT:
		dt: date-time (UNIX / epoch time)
		'''
		
		return time.time()

	
	########################################################################################################
	

	@staticmethod
	def warnmessage(unit,msg):
		'''
		misc.warnmessage(caller,msg)
		
		Print a warning message
		
		INPUT:
		caller: caller label / name of the calling object (string)
		msg: warning message
		
		OUTPUT:
		(none)
		'''
		
		M = '***** WARNING from ' + unit + ' at ' + misc.now_string() + ': ' + msg
		print (M)
		

	########################################################################################################
	

	@staticmethod
	def wait_for_enter(msg='Press ENTER to continue.'):
		'''
		misc.wait_for_enter(msg='Press ENTER to continue.')
		
		Print a message and wait until the user presses the ENTER key.
		
		INPUT:
		msg (optional): message
		
		OUTPUT:
		(none)
		'''
		
		if sys.version_info >= (3,0): # Python 3.0 or newer
			input( msg )
		else:
			raw_input( msg )
