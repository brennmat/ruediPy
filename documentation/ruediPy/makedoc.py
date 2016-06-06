#!/usr/bin/python

import subprocess, sys

mainfile = 'ruediPy_manual'

commands = [
    ['pdflatex', mainfile + '.tex'],
    ['bibtex',   mainfile + '.aux'],
    ['pdflatex', mainfile + '.tex'],
    ['pdflatex', mainfile + '.tex']
]

# make tex file with ruediPy Python API:
subprocess.call(["python", "list_python_API.py"])

for c in commands:
    subprocess.call(c)