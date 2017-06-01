#!/usr/bin/env python

import inspect

from classes.rgams_SRS		       		import rgams_SRS
from classes.selectorvalve_VICI    		import selectorvalve_VICI
from classes.pressuresensor_WIKA   		import pressuresensor_WIKA
from classes.temperaturesensor_MAXIM   		import temperaturesensor_MAXIM
from classes.datafile			   	import datafile
from classes.misc			       	import misc

CLASSES = [ rgams_SRS , selectorvalve_VICI , pressuresensor_WIKA , temperaturesensor_MAXIM , datafile , misc ]

outfile = open('python_API.tex', 'w')

outfile.write( '%% THIS NEEDS THE underscore PACKAGE: \\usepackage[strings]{underscore}\n\n' )

for X in CLASSES:
	outfile.write ( '\subsubsection{Class \\texttt{' + X.__name__ + '}}\n' )
	P = inspect.getsourcefile(X)
	outfile.write ( '\path{' + P[P.find('ruedi'):len(P)] + '}\par\n' )
	doc = inspect.getdoc(X)
	if doc is None:
		outfile.write ( 'No class description available.\par' )
	else:
		# outfile.write ( '\\texttt{' + inspect.getdoc(X) + '+\n' )
		outfile.write ( inspect.getdoc(X) + '\par' )
	outfile.write ( '\n\n' )
	
	for name, data in inspect.getmembers(X):
		if name[0:2] == '__' :
			continue
		if name == '__doc__':
			continue
		if name == '__init__':
			continue
		if name == '__module__':
			continue
		outfile.write ( '\paragraph{Method \\texttt{' + name + '}}\n\\vspace{1ex}\n' )
		exec ( 'doc = ' + X.__name__ + '.' + name + '.__doc__' )

		if doc is None:
		   outfile.write ( 'No method description available.\par' )
		else:
			u = ''
			for line in doc.splitlines():
				u = u + line.lstrip() + '\\newline\n'
			outfile.write ( '\\texttt{' + u + '}' )

		outfile.write ( '\n\n' )

outfile.close()
