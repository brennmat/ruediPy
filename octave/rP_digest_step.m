function X = rP_digest_step (datafile, ...)

% function X = rP_digest_step (datafile, ...)
% 
% Load raw data and process ("digest") PEAK, ZERO, etc. data to obatin mean peak heights. This assumes that each datafile corresponds to a single "step" of analysis (i.e., a block of PEAK/ZERO readings corresponding to a given sample, calibration, or blank analyisis.
%
% THIS IS JUST A PLACEHOLDER FILE, IT DOES NOT CONTAIN ANY USEFUL CODE YET!!!
% 
% INPUT:
% datafile: file name (see also rP_read_datafile).
% ... (other inputs necessary?)
% 
% OUPUT:
% X: struct object with "digested" data from file:
%	X.type: analysis type (string; S, C, B, or X)
%	X.mz: MZ values of the digested PEAK-ZERO data
%	X.intens.val: means of PEAK-ZERO values (for each X.mz value)
%	X.intens.err: errors of X.inens.val data (errors of the means)
%	X.intens.unit: unit of X.intens.val and X.intens.err (string)
% 	X.std.val: partial pressure of the standard gas at each X.mz value
% 	X.std.unit: unit of X.std.val (string)
%
% DISCLAIMER:
% This file is part of ruediPy, a toolbox for operation of RUEDI mass spectrometer systems.
% 
% ruediPy is free software: you can redistribute it and/or modify
% it under the terms of the GNU General Public License as published by
% the Free Software Foundation, either version 3 of the License, or
% (at your option) any later version.
% 
% ruediPy is distributed in the hope that it will be useful,
% but WITHOUT ANY WARRANTY; without even the implied warranty of
% MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
% GNU General Public License for more details.
% 
% You should have received a copy of the GNU General Public License
% along with ruediPy.  If not, see <http://www.gnu.org/licenses/>.
% 
% ruediPy: toolbox for operation of RUEDI mass spectrometer systems
% Copyright (C) 2016  Matthias Brennwald
% 
% This program is free software: you can redistribute it and/or modify
% it under the terms of the GNU General Public License as published by
% the Free Software Foundation, either version 3 of the License, or
% (at your option) any later version.
% 
% This program is distributed in the hope that it will be useful,
% but WITHOUT ANY WARRANTY; without even the implied warranty of
% MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
% GNU General Public License for more details.
% 
% You should have received a copy of the GNU General Public License
% along with this program.  If not, see <http://www.gnu.org/licenses/>.
% 
% Copyright 2016, Matthias Brennwald (brennmat@gmail.com)

% load raw data:
RAW = rP_read_datafile (datafile)

% determine analysis type (SAMPLE, CALIBRATION, BLANK)
...

% determine PEAK and ZERO values, for each mz value
...

% determine PEAK-ZERO (net peak heights) and calculate mean and error-of-the-mean, for each mz value
...

% determine DATE/TIME of the analysis (mean of the timestamps of the PEAK-ZERO values?)
...

% if sample: determine sample name / ID
...

% if calibration: determine partial pressures of standard gas
...