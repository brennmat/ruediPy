function X = ruediPy_read_datafile(file,obj)

% function X = ruediPy_read_datafile(keys)
% 
% Read and parse data in ruediPy datafiles.
% (work in progress!)
% 
% INPUT:
% file: file name (including path, if necessary)
% obj: cellstring with names / types of objects for which objects data should be read from the file:
%		obj ={ LABEL-NAME-1 OBJECT-TYPE-1 ; LABEL-NAME-2 , OBJECT-TYPE-2 ; ... }
% 
% OUPUT:
% X: struct object with data from file. Stuct fields correspond to OBJECT and TYPE keys found in the data file.
% 
% EXAMPLE:
% DAT = ruediPy_read_datafile('~/ruedi_data/2016-03-30_13-27-02.txt',{'RGA-MS' 'SRSRGA' ; 'INLETSELECTVALVE' 'SELECTORVALVE'})
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
	t = [];	OBJKEY = TYPEKEY = DATA = {};
	line = fgetl (fid); k = 1;
	while line != -1
		% parse line (format: "TIMESTAMP OBJECT-KEY TYPE-KEY: ...DATA...")
		%% disp (sprintf('*** DEBUG INFO: line %i: %s', k, line))
		l = strsplit (line,': '); % split time / data keys from data part
		
		% get TIME, OBJECT, and TYPE parts:
		time_keys = strsplit (l{1},' ');
		t = [ t ; str2num(time_keys{1}) ]; % append time value
		OBJKEY{k}  = time_keys{2}; % label of the ruediPy object that sent the data to the data file
		TYPEKEY{k} = time_keys{3}; % type of data
		
		% get DATA part:
		DATA{k} = l{2};
		
		
		%% disp (sprintf('*** DEBUG INFO: Time = %g, Object = %s, Type = %s, Data = %s', t(k), OBJKEY{k}, TYPEKEY{k}, DATA{k}))
		
		
		% read next line:
		line = fgetl (fid); k = k + 1;
	end % while line != -1
	
	% close the file after reading it:
	ans = fclose (fid);
	if ans == -1
		error (sprintf('ruediPy_read_datafile: could not close file %s',file))
	end % ans = fclose(...)

	% parse file data into struct object, parse data for each object type
	X.file = file;
	
	Nobj = size(obj,1); % number of object types for which data is requested
		
	for i = 1:Nobj % get data for each of the requested object types
		% is there any data for an object with the label obj{i,1}, and on which lines?
		j = find (strcmp(OBJKEY,obj{i,1}));
		if any(j)
			% parse lines j, which have object-label = obj{i,} and object-type=obj{i,2}
			
			disp (sprintf('*** DEBUG INFO: parsing object-label=%s *** object-type=%s...',obj{i,1},obj{i,2}))
		
			switch toupper(obj{i,2})
				
				case 'SRSRGA'
					X = setfield (X,obj{i,1},[]); % add struct field
					disp ('Parse SRSRGA data here...')
					
				otherwise
					disp (sprintf('Unknown object type %s, skipping...',obj{i,2}))
			
			end % switch
				
		end
	end
	
	
	

end % if / else