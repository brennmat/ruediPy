# Code for the misc class
# 
# DISCLAIMER:
# This file is part of ruediPy, a toolbox for operation of RUEDI mass spectrometer systems.
# 
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright 2026, Matthias Brennwald (brennmat@gmail.com)

try:
	import sys
	import warnings
	import time
	import inspect
	import os
	import logging
	from typing import Optional

except ImportError as e:
	print (e)
	raise

# Flag for embedding apps (e.g. miniruedi) to indicate they provide a GUI/display.
# Used for plotting: when True, ruediPy does not create its own matplotlib windows.
_have_external_gui = False

def set_have_external_gui(flag: bool) -> None:
	'''Set whether an external GUI provides the display (for plotting decisions).'''
	global _have_external_gui
	_have_external_gui = flag

def get_logger():
	'''Return the ruedipy logger. Applications can add handlers to route messages.'''
	return logging.getLogger('ruedipy')

# check Python version and print warning if we're running version < 3:
if ( sys.version_info[0] < 3 ):
	warnings.warn("ruediPy / misc class is running on Python version < 3. Version 3.0 or newer is recommended!")


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
	def warnmessage(msg, caller=None, show_caller=True, overwrite_previous_msg = False):
		'''
		misc.warnmessage(msg, caller=None, show_caller=True)
		
		Print a warning message
		
		INPUT:
		msg: warning message
		caller (deprecated!): caller label / name of the calling object (string). The 'caller' argument is depracated and is determined automatically.
				
		OUTPUT:
		(none)
		'''

		if caller is not None:
			# old-style (depracated!) way of warnmessage call!
			# warnmessage( caller, msg )
			print( 'Calling misc.warnmessage(...) with TWO arguments is deprecated!' , file=sys.stderr )
			print('   msg = ' + caller , file=sys.stderr )
			print('   caller (ignored!) = ' + msg , file=sys.stderr )
			msg = caller

		msg = misc.now_string() + ': ' + msg

		if show_caller:
			caller_frame = inspect.stack()[1]
			caller_filename = caller_frame.filename
			caller = os.path.splitext(os.path.basename(caller_filename))[0]
			msg = caller + ' at ' + misc.now_string() + ': ' + msg
			
		# Forward to python logging (applications add handlers for GUI/file/console):
		get_logger().warning(msg, extra={'overwrite_previous_msg': overwrite_previous_msg})
	########################################################################################################
	

	@staticmethod
	def logmessage(msg, caller=None, show_caller=True, overwrite_previous_msg = False):
		'''
		misc.logmessage(msg, caller=None, show_caller=True)
		
		Print a warning message
		
		INPUT:
		msg: warning message
		caller (deprecated!): caller label / name of the calling object (string). The 'caller' argument is depracated and is determined automatically.
				
		OUTPUT:
		(none)
		'''

		if caller is not None:
			# old-style (depracated!) way of logmessage call!
			# logmessage( caller, msg )
			print( 'Calling misc.logmessage(...) with TWO arguments is deprecated!' , file=sys.stderr )
			print('   msg = ' + caller , file=sys.stderr )
			print('   caller (ignored!) = ' + msg , file=sys.stderr )
			msg = caller

		msg = misc.now_string() + ': ' + msg
		
		if show_caller:
			caller_frame = inspect.stack()[1]
			caller_filename = caller_frame.filename
			caller = os.path.splitext(os.path.basename(caller_filename))[0]

			msg = caller + ' at ' + msg

		# Forward to python logging (applications add handlers for GUI/file/console):
		get_logger().info(msg, extra={'overwrite_previous_msg': overwrite_previous_msg})


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
		
		print ('\a') # get user attention using the terminal bell
		# print ('')
		if sys.version_info >= (3,0): # Python 3.0 or newer
			input( msg )
		else:
			raw_input( msg )
		# fprint ('')


	########################################################################################################
	

	@staticmethod
	def ask_for_value(msg='Enter value = '):
		'''
		x = misc.ask_for_value(msg='Enter value = ')
		
		Print a message asking the user to enter something, wait until the user presses the ENTER key, and return the value.
		
		INPUT:
		msg (optional): message
		
		OUTPUT:
		x: user value (string)
		'''
		
		print ('\a') # get user attention using the terminal bell
		# print ('')
		if sys.version_info >= (3,0): # Python 3.0 or newer
			x = input( msg )
		else:
			x = raw_input( msg )
		# print ('')
		return x
		

	########################################################################################################


	@staticmethod
	def sleep( wait , msg='' ):
		'''
		misc.sleep( wait , msg='' )
		
		Wait for a specified time and print a countdown message. The user can skip the countdown by pressing CTRL-C.
		
		INPUT:
		wait: waiting time (seconds)
		msg (optional): message
		
		OUTPUT:
		(none)
		'''
		
		dt = 1

		start = time.time()
		lastmessage = start - dt-1
		finished = 'done'
		
		try:
			while time.time()-start < wait:
				if time.time() > lastmessage + dt:
					d = 'Waiting ' + str(wait) + ' seconds'
					if msg:
						d = d + ' (' + msg + ')'
					l = int(round(wait-(time.time()-start)))
					if l > 1:
						d = d + '. ' + str(l) + ' seconds left...     '
					else:
						d = d + '. ' + str(l) + ' second left...      '
								
					print(d, end = '\r')
					sys.stdout.flush() 
				
					lastmessage = time.time()

				time.sleep(1)
			
		except KeyboardInterrupt:
			finished = 'skipped'
			pass

		print ( d.rstrip() + finished + '.' )



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
		
		print ('\a') # get user attention using the terminal bell
		N = len(menu);
		do_menu = True;
		while do_menu:
			# print ( '' )
			print ( '\n' + title + ':' )
			for i in range(N):
				print ( '   ' + str(i+1) + ': ' + menu[i] )
			if sys.version_info >= (3,0): # Python 3.0 or newer
				ans = input( 'Enter number: ' )
			else:
				ans = raw_input( 'Enter number: ' )
			# print ('')
			
			try:
				ans = int(ans) # try converting from string to integer number
			except ValueError:
				ans = -1
				
			if int(ans) in range(1,N+1):
				do_menu = False

			if do_menu:
				print ('\nInvalid input. Try again...')
		
		return ans					
									

########################################################################################################


	@staticmethod
	def have_external_gui():
		'''
		x = misc.have_external_gui()
		
		Determine if an external GUI system is configured.
		
		INPUT:
		(none)
		
		OUTPUT:
		gui: flag indicating if external GUI is configured
		
		EXAMPLE:
		g = misc.have_external_gui( )
		'''
		
		return _have_external_gui	
									

########################################################################################################


	@staticmethod
	def plotting_setup():
		'''
		x = misc.plotting_setup()
		
		Try to setup plotting environment (matplotlib) and return success flag.
		
		INPUT:
		(none)
		
		OUTPUT:
		x: flag indicating success (x == True if successful)
		'''

		success = False

		if misc.have_external_gui():
			misc.warnmessage ('Will not load and configure matplotlib as there is already an external GUI with a display environment.')
		
		else:
			havedisplay = "DISPLAY" in os.environ
			if havedisplay:
				try:
					import matplotlib
					matplotlib.use('TkAgg')
					matplotlib.rcParams['legend.numpoints'] = 1
					matplotlib.rcParams['axes.formatter.useoffset'] = False
					success = True
				except:
					misc.warnmessage ('Could not load and configure matplotlib, cannot set up display environment.')

		return success
