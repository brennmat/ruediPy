function X = rP_calibrate_steps (data,MS_name)

% function X = rP_calibrate_steps (data,MS_name)
% 
% Calibrate ruediPy data by combining data from samples, calibrations, and blanks.
%
% *** THIS IS JUST A PLACEHOLDER FILE, WHICH DOES NOT YET CONTAIN ANY USEFUL CODE ****
% 
% APROACH:
% * GET RAW DATA:
% 	- Load raw data from all files / analysis steps
% 	- DIGEST RAW DATA: Determine mean peak heights for all steps, at all mz-detector combinations in the data set
% 	- Determine all combinations of mz values and detector types in the data set
% * PROCESS CALIBRATION DATA (STANDARDS, BLANKS):
% 	- Plot peak heights for steps of type STANDARD and BLANK (to identify potential outliers etc.)
% 	- Subtract mean BLANK peak heights for all peak heights for all mz-detector combinations
% 	- Determine gas partial pressures in STANDARD gas analyses from standard gas concentrations (as given in the data file) and the total gas pressure at the gas inlet (use TOTALGASPRESSURE value if available, or ask user for a total gas pressure value)
% 	- Determine sensitivities for all steps of type 'STANDARD', at all mz-detector combinations in the data set
% 	  (sensitivity = blank-corrected detector signal / partial pressure at gas inlet)
% * PROCESS SAMPLE DATA:
% 	- Interpolate sensitivities to SAMPLE analysis times (to compensate sensitivity drifts)
% 	- Determine SAMPLE partial pressures by multiplying SAMPLE peak heights (blank-corrected) with sensitivites
% 	- (optional?) Normalise SAMPLE partial pressures such that sum of all partial pressures is equal to TOTALGASPRESSURE reading taken from sample
% 
% 
% INPUT:
% data: vector of raw data structures or data file names, or pattern matching list of data files (see also rP_read_datafile)
% MS_name: name / label of mass spectrometer for which data should be digested (string)
% 
% OUPUT:
% ...(not yet defined)...
% ...(will likely be a time series of calibrated data / partial pressures at different mz values)...
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

warning('rP_calibrate_steps: NOT YET IMPLEMENTED!')