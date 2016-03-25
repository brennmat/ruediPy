# Code for the misc class

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
		
