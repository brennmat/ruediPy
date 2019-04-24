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



disp ('**** rP_rawextract is under construction ****')
disp ('**** rP_rawextract is under construction ****')
disp ('**** rP_rawextract is under construction ****')
disp ('**** rP_rawextract is under construction ****')



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

...WRITE RESULTS DO DATAIFLE HERE...

...BELOW CODE MAY BE USEFUL AS A TEMPLATE...







PARTIALPRESSURES.species = SPECIES;
PARTIALPRESSURES.val     = P_val;
PARTIALPRESSURES.err     = P_err;
PARTIALPRESSURES.time    = TIME;
PARTIALPRESSURES.unit    = unit;

% SENSORS data from samples:
SENSORS = {};
for i = 1:length(iSAMPLE)
	SENSORS{i} = X(iSAMPLE(i)).SENSORS; 
end


__write_datafile (...
	SAMPLES,...
	PARTIALPRESSURES,...
	SENSORS,...
	fileparts(data),...
	out_file_name,...
	use_zenity
	)

if wait_exit
	input ("Processing complete! Press ENTER to exit...", "s");
else
	disp ("Processing complete!")
end



endfunction % main function




% ************************************************************************************************************************************************




% ************************************
% ************************************
% helper functions:
% ************************************
% ************************************

function __write_datafile (samples,partialpressures,sensors,path,name,use_zenity)
% write processed data to CSV data file

	species = partialpressures.species;
	p_val   = partialpressures.val;
	p_err   = partialpressures.err;
	time    = partialpressures.time;
	p_unit  = partialpressures.unit;

	if isempty (name)
		if use_zenity
			disp ('Select new file for processed data...');
			[status, name] = system ("zenity --file-selection --title='Output file' --save --confirm-overwrite 2> /dev/null");
		else
			name = input ('Enter file name for processed data (or leave empty to skip): ','s');
		end
	end

	if isempty(name)
		disp ('rP_calibrate_batch: no file name given, not writing data to file.')
	
	else
	
		% open ASCII file for writing:
		if length(path) == 0
			path = pwd;
		end
		if strcmp(path(end),filesep)
			path = path(1:end-1);
		end
		[p,n,e] = fileparts (name);
		e = tolower(e);
		if ~strcmp(e,'.csv')
			e = '.csv';
		end
		if isempty(p)
			p = path;
		end

		path = [p filesep n e];
		path = strrep(path,"\n",""); % just in case: remove newlines

		[fid,msg] = fopen (path, 'wt');
		if fid == -1
			error (sprintf('rP_calibrate_batch: could not open file for writing (%s).',msg))
		else
		
			disp (sprintf('Writing data to %s...',path))
			
			% write header:
			fprintf (fid,'SAMPLE')
			for j = 1:length(species)
				fprintf (fid,';%s TIME (EPOCH);%s PARTIALPRESSURE (%s);%s PARTIALPRESSURE ERR (%s)',species{j},species{j},p_unit,species{j},p_unit)
			end	
			if ~isempty(sensors)			
				nsens = length(sensors{1});
				for j = 1:nsens

					sns_unit = '???';
					k = 1;
					while k <= length(samples)
						if ischar(sensors{k}{j}.mean_unit)
							if ~strcmp(sensors{k}{j}.mean_unit,'NA')
								sns_unit = sensors{k}{j}.mean_unit;
								k = length(samples) + 1;
							end
						end
						k = k+1;
					end
					if strcmp (sns_unit,'???')
						warning (sprintf('rP_calibrate_batch: could not determine units of %s sensor data.',sensors{1}{j}.sensor))
					end
					fprintf (fid,';%s TIME (EPOCH);%s (%s);%s ERR (%s)',sensors{1}{j}.sensor,sensors{1}{j}.sensor,sns_unit,sensors{1}{j}.sensor,sns_unit)

				end
			end
			
						
			% write data:
			for i = 1:length(samples)
				fprintf (fid,'\n');
				
				% sample name:
				fprintf (fid,'%s',samples{i});
				
				% gas partial pressures:
				for j = 1:length(species)				
					fprintf (fid,';%.2f;%g;%g',time(j,i),p_val(j,i),abs(p_err(j,i)))
				end

				% sensor data (if any):
				if ~isempty(sensors)				
					for j = 1:nsens						
						fprintf (fid,';%.2f;%g;%g',sensors{i}{j}.mean_time,sensors{i}{j}.mean,sensors{i}{j}.mean_err)
					end
				end

			end % for i = 

			fclose (fid);

		end % if fid == -1
	end % if isempty(name)
	
endfunction
