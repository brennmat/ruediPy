function [X] = rP_rawextract(data,varargin)

% function [...] = rP_rawextract(data,varargin)
% 
% Extract raw data from ruediPy data files (peak heights, sensor data, etc.) and write results to CSV data file.
%
% INPUT:
% data: files to be processed (string with file/path pattern)
% 
% OUTPUT:
% ...
%
% options: optional parameters:
%	- 'no_peak_zero_plot': don't plot PEAK and ZERO values
%	- 'no_sensitivity_plot': don't plot sensitivities
%	- 'no_partialpressure_plot': don't plot partial pressures
%	- 'no_plots','noplots': don't plot anything
%	- 'standardgas_pressure',X,unit: use this gas inlet pressure for all standard analyses (X: number, unit: string)
%	- 'wait_exit': wait for key press by user before exiting this function (useful for interactive use from shell scripts)
%	- 'output_file': file name to use for writing results. If not specified, the code will ask for a file name.
%	- 'use_zenity': use Zenity/GUI to ask stuff from user instead of command-line terminal.
%
% EXAMPLE 1:
% ...
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



% ************************************
% ************************************
% main function:
% ************************************
% ************************************


% option defaults (plotting etc.):4
out_file_name = '';
use_zenity = false;

% parse options:
i = 0;
while i < length(varargin) % parse options
	i = i+1;
	switch tolower(varargin{i})
	
		% plotting options:

		case 'output_file'
			out_file_name = varargin{i+1};
			i = i+1;

		case 'use_zenity'
			% disp ('rP_calibrate_batch: using Zenity/GUI for user interaction.')
			use_zenity = true;

		
		otherwise
			warning (sprintf("rP_rawextract: unknown option '%s'. Ignoring...",varargin{i}))
	end
end



% ************************************
% Load and digest raw data from files:
% ************************************

% load raw data from files:
RAW = rP_read_datafile (data);

% determine RGA names from data set:
disp ('Scanning for RGA objects...')
MS_names = {};
for i = 1:length(RAW)
	if any( k = find(strcmp(RAW{i}.fieldtypes,'RGA_SRS')) )
		MS_names{end+1} = fieldnames (RAW{i}){k};
	end
end
MS_names = unique (MS_names);
if length (MS_names) == 0
	disp ('...no RGA objects found.')
else
	for i = 1:length(MS_names)
		disp (sprintf('Found RGA object: %s',MS_names{i}))
	end
end


% determine SENSOR namees from data set:
disp ('Scanning for SENSOR objects...')
SENSOR_names = {};
for i = 1:length(RAW)
	if any( k = find(strcmp(RAW{i}.fieldtypes,'TEMPERATURESENSOR')) )
		SENSOR_names{end+1} = fieldnames (RAW{i}){k};
	end
	if any( k = find(strcmp(RAW{i}.fieldtypes,'PRESSURESENSOR')) )
		SENSOR_names{end+1} = fieldnames (RAW{i}){k};
	end
end
SENSOR_names = unique (SENSOR_names);
if length (SENSOR_names) == 0
	disp ('...no SENSOR objects found.')
else
	for i = 1:length(SENSOR_names)
		disp (sprintf('Found SENSOR object: %s',SENSOR_names{i}))
	end
end


% digest data and store results in array (X):
X = [];
for i = 1:length(RAW)

	disp (sprintf('rP_rawextract: parsing file %s...',RAW{i}.file))

	info = rP_digest_step_DATAFILEINFO(RAW{i});

	ms = {};
	sens = {};

	% digest MS data (abort if not available):
	for k = 1:length(MS_names)
		u = rP_digest_step_RGA_SRS (RAW{i},MS_names{k}); % digest RGA_SRS data
		if ~isempty(u.mean) % only keep data if digesting was successful
			ms{length(ms)+1} = u;
		end
	end
	if length(ms) > 1
		warning ("rP_rawextract: there are data from different mass spectrometers. Skipping this file...")
		ms = {};
	elseif length(ms) == 0
		warning ("rP_rawextract: found no mass spectrometer data for specified RGA_SRS names. Skipping this file...")
		ms = {};
	else
		ms = ms{1};
	end
	
	% digest SENSORs data:
	for k = 1:length(SENSOR_names)
		sens{k} = rP_digest_step_SENSOR (RAW{i},SENSOR_names{k});
	end
	
	xx.INFO        = info;
	xx.MS          = ms;
	xx.SENSORS     = sens;
	
	% append:
	X = [ X ; xx ];	

end % for





% *************************************************
% Write SAMPLE results to data file
% *************************************************

if isempty (out_file_name)
	out_file_name = rP_get_output_filename (use_zenity,'Data file for raw data','CSV');
end

if isempty(out_file_name)
	disp ('rP_rawextract: no file name given, not writing data to file.')
else
	
	% open ASCII file for writing:
	[fid,msg] = fopen (out_file_name, 'wt');
	if fid == -1
		error (sprintf('rP_rawextract: could not open file for writing (%s).',msg))
	else
		disp (sprintf('Writing data to %s...',out_file_name))
		

		% write header:

		fprintf (fid,'FILE;TYPE;SAMPLE')

		items = {};
		sens  = {};
		for i = 1:length(X)
			if isstruct (X(i).MS)
				items = unique ( { items{:}  X(i).MS.mz_det{:} } ) ;
			end
			if isfield (X(i),'SENSORS')
				for j = 1:length(X(i).SENSORS)
					sens = unique ( { sens{:} X(i).SENSORS{j}.sensor } );
				end
			end
		end

		for i = 1:length(items)
			fprintf (fid,';%s TIME (EPOCH);%s (MEAN);%s (MEAN-ERR)',items{i},items{i},items{i})	
		end

		for i = 1:length(sens)
			fprintf (fid,';%s TIME (EPOCH);%s (MEAN);%s (MEAN-ERR)',sens{i},sens{i},sens{i})	
		end


		% write data:

		for i = 1:length(X)
			fprintf (fid,'\n')

			% get MS numbers:
			item_EPOCH = item_MEAN = item_MEANERR = repmat (NA,size(items));
			if isstruct (X(i).MS)
				for j = 1:length(items)
					k = strmatch (items{j},X(i).MS.mz_det,"exact");
					if ~isempty(k)
						item_EPOCH(j) = X(i).MS.mean_time(k);
						item_MEAN(j) = X(i).MS.mean(k);
						item_MEANERR(j) = X(i).MS.mean_err(k);
					end
				end
			end

			% get SENSORS numbers:
			sens_EPOCH = sens_MEAN = sens_MEANERR = repmat (NA,size(sens));
			if isfield (X(i),'SENSORS')
				for j = 1:length(X(i).SENSORS)
					k = strmatch (X(i).SENSORS{j}.sensor,sens,"exact");
					if ~isempty(k)
						sens_EPOCH(k) = X(i).SENSORS{j}.mean_time;
						sens_MEAN(k) = X(i).SENSORS{j}.mean;
						sens_MEANERR(k) = X(i).SENSORS{j}.mean_err;
					end
				end
			end

			% write info columns:
			if strcmp(toupper(X(i).INFO.type),'SAMPLE')
				label = X(i).INFO.name.name;
			else
				label = '';
			end
			fprintf (fid,'%s;%s;%s',X(i).INFO.file,X(i).INFO.type,label);
			
			% write MS data columns:
			for j = 1:length(item_EPOCH)
				fprintf (fid,';%.2f;%g;%g',item_EPOCH(j),item_MEAN(j),item_MEANERR(j));
			end

			% write SENSORS data columns:
			for j = 1:length(sens_EPOCH)
				fprintf (fid,';%.2f;%g;%g',sens_EPOCH(j),sens_MEAN(j),sens_MEANERR(j));
			end

		end


		fclose (fid);
	end
end
