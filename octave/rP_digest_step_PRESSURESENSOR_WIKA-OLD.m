function X = rP_digest_step_PRESSURESENSOR_WIKA (RAW,sensor_name,opt)

% function X = rP_digest_step_PRESSURESENSOR_WIKA (RAW,sensor_name,opt)
% 
% Load raw data and process ("digest") PRESSURE data from PRESSURESENSOR_WIKA pressure sensor to obatin mean pressure value. This assumes that each datafile corresponds to a single "step" of analysis (i.e., a block of PRESSURE readings corresponding to a given sample, calibration, or blank analyisis). Results can be printed on the terminal and plotted on screen.
% 
% INPUT:
% RAW: raw data struct (see also OUTPUT of rP_read_datafile)
% sensor_name: name / label of PRESSURESENSOR_WIKA pressure sensor for which data should be digested (string).
% opt (optional): string or cellstring with keyword(s) to control various behaviours (use defauls if opt is empty). Multiple keywords can be combined in a cellstring.
%	opt = 'printsummary' --> print results to STDOUT (default: don't print anything)
% 
% OUTPUT:
% X: struct object with "digested" data from file:
%	X.mean: mean of PRESSURE values
%	X.mean_err: error of X.mean value (error of the mean)
%	X.mean_unit: unit of X.mean and X.mean_err (cell string)
%	X.mean_time: epoch time corresponding to X.mean (mean of PRESSURE timestamps)
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
	error ('rP_digest_step_PRESSURESENSOR_WIKA: cannot process an array of multiple steps! Please try again with a single step struct...')
end


% init empty data containers for digested data:
X.mean = [];
X.mean_err = [];
X.mean_time = [];
X.mean_unit = {};

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
	disp (sprintf('rP_digest_step_PRESSURESENSOR_WIKA: found no PRESSURE data for ''%s''.',sensor_name))
	
else
	% get PRESSURE data:
	PRESS  = getfield (RAW,sensor_name);	% PRESSURE data
	if isfield (PRESS,'PRESSURE')
		P = PRESS.PRESSURE; NP = length (P);
	else
		P = []; NP = 0;
		warning ('rP_digest_step_PRESSURESENSOR_WIKA: no PRESSURE values found!')
	end
	
	% determine PRESSURE values with associated timestamp and unit
	PRESS_val = PRESS_time = [];
	PRESS_unit = {};
	for i = 1:NP
	    PRESS_time    = [ PRESS_time ; P(i).epochtime ];
	    PRESS_val     = [ PRESS_val ; P(i).val ];
	    PRESS_unit{i} = P(i).unit;
	end
	
	%%%% % determine mean and error-of-the-mean of PRESSURE values
	X.mean 		= mean (PRESS_val);
	if length(PRESS_val) > 1
		X.mean_err	= std (PRESS_val) / sqrt(length(PRESS_val)-1);
	else
		warning (sprintf('rP_digest_step_PRESSURESENSOR_WIKA: found only single PRESSURE value for ''%s''; cannot determine error of the mean!',sensor_name))
		X.mean_err	= NaN;
	end
	
	u = unique (PRESS_unit);
	if length(u) > 1
		warning (sprintf('rP_digest_step_PRESSURESENSOR_WIKA: found different units of PRESSURE values for ''%s''; cannot determine unit of the mean (and values used to calculate the mean may be inconsistent)!',sensor_name))
		X.mean_unit	= '?';
	else 
		if iscellstr(u)
			u = u{1};
		end
		X.mean_unit = u;
	end
	
	X.mean_time = mean (PRESS_time);
	
	if printsummary % print digest summary			
	    disp (sprintf('MEAN PRESSURE = %g +/- %g %s (%s UTC)',...
	   		X.mean,...
	   		X.mean_err,...
	   		X.mean_unit,...
	   		datestr(datenum (1970,1,1,0,0) + X.mean_time/86400)))
	end
end

