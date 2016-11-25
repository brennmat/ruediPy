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
		
		print ('')
		if sys.version_info >= (3,0): # Python 3.0 or newer
			input( msg )
		else:
			raw_input( msg )
		print ('')


	########################################################################################################
	
	

	@staticmethod
	def sleep( wait , msg='' ):
		'''
		misc.sleep( wait , msg='' )
		
		Wait for a specified time and print a message.
		
		INPUT:
		wait: waiting time (seconds)
		msg (optional): message
		
		OUTPUT:
		(none)
		'''
		
		# dt = wait/10
		# dt = round(dt/5)*5
		# if dt < 1:
		# 	dt = 1
		# if dt > 30:
		# 	dt = 30
		dt = 1

		start = time.time()
		lastmessage = start - dt-1
		bs  = '\b' * 1000   # backspaces
		do_bs = False
		
		while time.time()-start < wait:
			if time.time() > lastmessage + dt:
				d = 'Waiting ' + str(wait) + ' seconds'
				if msg:
					d = d + ' (' + msg + ')'
				l = int(round(wait-(time.time()-start)))
				if l > 1:
					d = d + '. ' + str(l) + ' seconds left...'
				else:
					d = d + '. ' + str(l) + ' second left...'
				
				if do_bs: # print backspaces to delete previous wait message:
					print bs,
				
				print '\b' + d ,
				sys.stdout.flush() 
				do_bs = True
				
				lastmessage = time.time()

			time.sleep(1)
			
		print 'done.'



########################################################################################################
	

	@staticmethod
	def user_menu(menu,title='Choose an option'):
		'''
		x = misc.user_menu(menu,title='Choose an option')
		
		Show a "menu" for selection of different user options, return user choice based on key pressed by user.
		
		INPUT:
		menu: menu entries (tuple of strings)
		title (optional): title of the menu (default='Choose an option')
		
		OUTPUT:
		x: number of menu choice
		
		EXAMPLE:
		k = misc.user_menu( title='Choose dinner' , menu=('Chicken','Burger','Veggies') )
		'''
		
		N = len(menu);
		do_menu = True;
		while do_menu:
			print ''
			print title + ':'
			for i in range(N):
				print '   ' + str(i+1) + ': ' + menu[i]
			if sys.version_info >= (3,0): # Python 3.0 or newer
				ans = input( 'Enter number: ' )
			else:
				ans = raw_input( 'Enter number: ' )
			print ('')
			
			try:
				ans = int(ans) # try converting from string to integer number
			except ValueError:
				ans = -1
				
			if int(ans) in range(1,N+1):
				do_menu = False

			if do_menu:
				print ('Invalid input. Try again...')
		
		return ans					
									

########################################################################################################
