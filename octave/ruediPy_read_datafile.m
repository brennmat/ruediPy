function ans = ruediPy_read_datafile(file,keys)

% function ans = ruediPy_read_datafile(keys)
% 
% Read and parse data in ruediPy datafiles.
% (work in progress!)
% 
% INPUT:
% file: file name (including path, if necessary)
% keys: ...to be defined...
% 
% OUPUT:
% ans: ...to be defined...
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
% Copyright 2016, Matthias Brennwald (brennmat@gmail.com) and Yama Tomonaga

% try to get read access to the file:
[fid, msg] = fopen (file, 'rt');

if fid == -1 % could not get read access to file, issue error:
	error (sprintf('ruediPy_read_datafile: could not get read access to file %s (%s)',file,msg))
	
else % read file line by line:
	t = [];	OBJKEY = TYPEKEY = {};
	line = fgetl (fid); k = 1;
	while line != -1
		% parse line (format: "TIMESTAMP OBJECT-KEY TYPE-KEY: ...DATA...")
		disp (sprintf('*** DEBUG INFO: line %i: %s', k, line))
		l = strsplit (line,': '); % split time / data keys from data part
		
		% parse time and data keys:
		time_keys = strsplit (l{1},' ');
		t = [ t ; str2num (time_keys{1}) ]; % append time value
		OBJKEY{k}  = time_keys{2}; % label of the ruediPy object that sent the data to the data file
		TYPEKEY{k} = time_keys{2}; % type of data
		disp (sprintf('*** DEBUG INFO: Time = %g, Object = %s, Type = %s', t(k), OBJKEY{k}, TYPEKEY{k}))		
		
		% parse data (depends on data keys):
		% use SWITCH / CASE on keys, possibly with subroutines
		
		% read next line:
		line = fgetl (fid); k = k + 1;
	end
	
	% close the file after reading it:
	ans = fclose (fid);
	if ans == -1
		error (sprintf('ruediPy_read_datafile: could not close file %s',file))
	end