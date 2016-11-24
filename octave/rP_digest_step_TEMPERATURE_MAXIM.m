function X = rP_digest_step_TEMPERATURE_MAXIM (RAW,sensor_name,opt)

% function X = rP_digest_step_TEMPERATURE_MAXIM (RAW,sensor_name,opt)
% 
% Load raw data and process ("digest") TEMPERATURE data from TEMPERATURESENSOR_MAXIM temperature sensor to obatin mean temperature value. This assumes that each datafile corresponds to a single "step" of analysis (i.e., a block of PRESSURE readings corresponding to a given sample, calibration, or blank analyisis). Results can be printed on the terminal and plotted on screen.
% 
% INPUT:
% RAW: raw data struct (see also OUTPUT of rP_read_datafile)
% sensor_name: name / label of TEMPERATURESENSOR_MAXIM pressure sensor for which data should be digested (string)
% opt (optional): string or cellstring with keyword(s) to control various behaviours (use defauls if opt is empty). Multiple keywords can be combined in a cellstring.
%	opt = 'showplot' --> show plot(s) of the data (default: no plots are shown)
%	opt = 'printsummary' --> print results to STDOUT (default: don't print anything)
%	opt = 'userwait' --> same as 'printsummary', but wait for user to press a key after printing the results
% 
% OUTPUT:
% X: struct object with "digested" data from file:
%	X.mean: mean of TEMPERATURE values
%	X.mean_err: error of X.mean value (error of the mean)
%	X.mean_unit: unit of X.mean and X.mean_err (cell string)
%	X.mean_time: epoch time corresponding to X.mean (mean of TEMPERATURE timestamps)
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

if length(RAW) > 1
	error ('rP_digest_step_TEMPERATURE_MAXIM: cannot process an array of multiple steps! Please try again with a single step struct...')
end


warning ('rP_digest_step_TEMPERATURE_MAXIM: this function is not yet implemented! Returning N/A data...')

X.mean      = [];
X.mean_err  = [];
X.mean_unit = '';
X.mean_time = [];

%%%%%%%%%%%%%%
% implement the rP_digest_step_PRESSURESENSOR_WIKA function first; then use this as a template for rP_digest_step_TEMPERATURE_MAXIM
%%%%%%%%%%%%%%