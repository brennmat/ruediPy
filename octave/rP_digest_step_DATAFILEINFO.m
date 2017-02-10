function X = rP_digest_step_DATAFILEINFO (RAW)

% function X = rP_digest_step_DATAFILEINFO (RAW)
% 
% Determine meta information from RAW data.
% 
% INPUT:
% RAW: raw data struct (see also OUTPUT of rP_read_datafile)
% 
% OUTPUT:
% X: struct object with meta data:
%	X.type: analysis type (string; S, C, B, or X)
% 	X.std: partial pressure(s) of the standard gas corresponding to each X.mz_det entry
% 	X.std_unit: unit of X.std (string)
%	X.time: timestamp of data file (epoch time corresponding to ANALYSISTIME entry)
%	X.name: name/descriptor of data (string)
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
	error ('rP_digest_step_DATAFILEINFO: cannot process an array of multiple steps! Please try again with a single step struct...')
end

% init empty data containers:
X.type = '?';
X.std = [];
X.std_unit = {};

% determine analysis type (SAMPLE, STANDARD, BLANK, UNKNOWN)
switch toupper(RAW.DATAFILE.ANALYSISTYPE.type)
	case { 'SAMPLE' 'S' }
		X.type = 'SAMPLE';
	case { 'STANDARD' 'STD' }
		X.type = 'STANDARD';
	case { 'BLANK' 'B' }
		X.type = 'BLANK';
	case { 'MISC' }
		X.type = 'MISC';
	otherwise
		X.type = 'UNKNOWN';
end % switch

% determine analysis time/date:
X.time = RAW.DATAFILE.ANALYSISTYPE.epochtime;

% determine sample description / ID
[p,f,e] = fileparts(RAW.file);
X.file = [ f e ];
switch X.type
	case 'SAMPLE'
		if isfield (RAW.DATAFILE,'SAMPLENAME')
			X.name = RAW.DATAFILE.SAMPLENAME;
		else
			X.name = 'UNKNOWN SAMPLE';
		end
	case { 'STANDARD' 'BLANK' }
		X.name = datestr(rP_epochtime2datenum(X.time),'yyyy-mm-dd_HH:MM:SS');
	otherwise
		X.name = 'UNKNOWN'
end % switch

% parse standard gas information (for calibrations)
X.standard.species = {};
X.standard.conc    = [];
X.standard.mz      = [];
if strcmp (X.type,'STANDARD')
	for i = 1:length(RAW.DATAFILE.STANDARD)
		X.standard.species{i} = RAW.DATAFILE.STANDARD(i).species;
		X.standard.conc       = [ X.standard.conc ; RAW.DATAFILE.STANDARD(i).concentration ];
		X.standard.mz         = [ X.standard.mz   ; RAW.DATAFILE.STANDARD(i).mz ];
	end
end