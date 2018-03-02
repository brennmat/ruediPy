function X = rP_digest_step_SENSOR(RAW,sensor_name,opt)

% function X = rP_digest_step_SENSOR (RAW,sensor_name,opt)
% 
% Load raw data and process ("digest") SENSOR data from to obatin mean sensor value. This assumes that each datafile corresponds to a single "step" of analysis (i.e., a block of SENSOR readings corresponding to a given sample, calibration, or blank analysis). Results can be printed on the terminal and plotted on screen.
% The sensor data is stored in a struct field of the RAW object, where the field name corresponds to the sensor_name. This SENSOR field is a struct (or an array of structs) with the following fields:
%	epochtime: Unix epoch time (time stamp of the sensor reading)
%	val: data value (scalar)
%	unit: unit of the value (string)
%
% INPUT:
% RAW: raw data struct (see also OUTPUT of rP_read_datafile)
% sensor_name: name / label of the SENSOR (fieldname) for which data should be digested (string).
% opt (optional): string or cellstring with keyword(s) to control various behaviours (use defauls if opt is empty). Multiple keywords can be combined in a cellstring.
%	opt = 'printsummary' --> print results to STDOUT (default: don't print anything)
% 
% OUTPUT:
% X: struct object with "digested" SENSOR data:
%	X.mean: mean of SENSOR values
%	X.mean_err: error of X.mean value (error of the mean)
%	X.mean_unit: unit of X.mean and X.mean_err (cell string)
%	X.mean_time: epoch time corresponding to X.mean (mean of SENSOR timestamps)
%	X.sensor: sensor name (string, copy of sensor_name)
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
% Copyright (C) 2016, 2017, Matthias Brennwald (brennmat@gmail.com)
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
	error ('rP_digest_step_SENSOR: cannot process an array of multiple steps! Please try again with a single step struct...')
end


% init empty data containers for digested data:
X.mean = [];
X.mean_err = [];
X.mean_time = [];
X.mean_unit = {};
X.sensor = sensor_name;

% default behaviour:
printsummary = false;

if exist('opt','var') % change defaults
	if ~iscellstr(opt)
		opt = {opt};
	end
	if any(strcmp (tolower(opt),'printsummary'))
		printsummary = true;
	end
end


% make sure hyphens are treaded correctly:
sensor_name = strrep (sensor_name,'-','_');

figr = 1;


% get data corresponding to sensor_name:
if ~isfield (RAW,sensor_name)
	disp (sprintf('rP_digest_step_SENSOR: found no SENSOR data for ''%s''.',sensor_name))
	X.mean = NA;
	X.mean_err = NA;
	X.mean_time = NA;
	X.mean_unit = 'NA';

	
else
	% get SENSOR data:
	SENS  = getfield (RAW,sensor_name);	% SENSOR data
	
	N = length (SENS);
	
	% determine SENSOR values with associated timestamp and unit
	SENSOR_val = SENSOR_time = [];
	SENSOR_unit = {};
	for i = 1:N
	    SENSOR_time    = [ SENSOR_time ; SENS(i).epochtime ];
	    SENSOR_val     = [ SENSOR_val ;  SENS(i).val ];
	    SENSOR_unit{i} = SENS(i).unit;
	end
		
	%%%% % determine mean and error-of-the-mean of PRESSURE values
	X.mean 		= mean (SENSOR_val);
	if length(SENSOR_val) > 1
		X.mean_err	= std (SENSOR_val) / sqrt(length(SENSOR_val)-1);
	else
		if ~isnan(X.mean)
			warning (sprintf('rP_digest_step_SENSOR: not enough data from SENSOR ''%s'' to determine error of the mean!',sensor_name))
		end		
		X.mean_err	= NaN;
	end
	
	u = unique (SENSOR_unit);
	if length(u) > 1
		warning (sprintf('rP_digest_step_SENSOR: found different units of SENSOR values for ''%s''; cannot determine unit of the mean (and values used to calculate the mean may be inconsistent)!',sensor_name))
		X.mean_unit	= '?';
	else 
		if iscellstr(u)
			u = u{1};
		end
		X.mean_unit = u;
	end
	
	X.mean_time = mean (SENSOR_time);
	
	% clean up NaN vs NA (if any):
	if isnan(X.mean) X.mean = NA; end
	if isnan(X.mean_err) X.mean_err = NA; end
	if isnan(X.mean_time) X.mean_time = NA; end

	if printsummary % print digest summary			
	    disp (sprintf('Mean %s value = %g +/- %g %s (%s UTC)',...
	   		sensor_name,...
	   		X.mean,...
	   		X.mean_err,...
	   		X.mean_unit,...
	   		datestr(datenum (1970,1,1,0,0) + X.mean_time/86400)))
	end
		
end

