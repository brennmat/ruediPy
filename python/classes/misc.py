# Code for the misc class

import time

class misc:
	
	@staticmethod
	def datetimenow():
		# return date-time string
		ans = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + ' (GMT)'
		return ans
	
	@staticmethod
	def warnmessage(unit,msg):
		# print a warning message
		# unit: name of part/unit of the instrument, e.g. unit = 'RGA'
		# msg: warning message
		t = misc.datetimenow()
		# M = '***** WARNING (' + unit + ', ' + t '): ' + msg
		
		M = '***** WARNING from ' + unit + ' at ' + t + ': ' + msg
		print (M)
		
