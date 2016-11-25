#!/usr/bin/python

import subprocess, sys

# make tex file with ruediPy Python API:
subprocess.call(["python", "list_python_API.py"])

mainfile = 'ruediPy_manual'

commands = [
    ['pdflatex', mainfile + '.tex'],
    ['bibtex',   mainfile + '.aux'],
    ['pdflatex', mainfile + '.tex'],
    ['pdflatex', mainfile + '.tex']
]

for c in commands:
    subprocess.call(c)