function X = rP_read_datafile (file)

% function X = rP_read_datafile (file)
% 
% Read and parse data in ruediPy datafiles.
%
% Datafile lines are formatted as follows:
%   EPOCHTIME DATASOURCE[LABEL/NAME] TYPE: DATAFIELD-1; DATAFIELD-2; DATAFIELD-3; ...
% where:
% 	EPOCH TIME: UNIX time (seconds after Jan 01 1970 UTC)
%	DATASOURCE: data origin (with optional LABEL of origin object)
%	TYPE: type of data
%	DATAFIELD-i: data fields, separated by colons. The field format and number of fields depends on the DATASOURCE and TYPE of data.
% 
% INPUT:
% file: file name. Either the full path to the file must be specified or the file name only. If only the filename is given, then the first file in the search path matching this file name is used. If file contains a wildcard, all files matching the pattern are loaded.
% 
% OUPUT:
% X: struct object with data from file (or cell array of data objects if multiple files are processed). Stuct fields correspond to OBJECT and TYPE keys found in the data file. All OBJECT structs have an extra field called 'FIELDTYPE' that indicates the field type (useful to determine type of data stored in the field).
% 
% EXAMPLE (read datafile ~/ruedi_data/2016-03-30_13-27-02.txt:
% DAT = rP_read_datafile('~/ruedi_data/2016-03-30_13-27-02.txt')
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


% check for wildcards in file, determine file(s) to be loaded:
files = glob (tilde_expand(file)); % cell string containing all file names matching 'file'
if length(files) > 1 % more than one file, so loop through all files
    for i = 1:length(files)
        u = rP_read_datafile (files{i});
        if ~isempty(u) % only append if loading data file was successful
            X{i} = u;
        else
        	X{i} = [];
        end
    end
    return % return to caller, don't execute code below, which is for single files only
end

% try to get read access to the file:
[fid, msg] = fopen (file, 'rt');

if fid == -1 % could not get read access to file, issue error:
	error (sprintf('ruediPy_read_datafile: could not get read access to file %s (%s)',file,msg))
	
else % read file line by line:
	disp (sprintf('rP_read_datafile: reading file %s...',file)); fflush (stdout);
	
	t = OBJ = LABEL = TYPE = DATA = FIELDTYPES = {};
	line = fgetl (fid); k = 1;
	
	while line != -1
		
		% parse line (format: "TIMESTAMP OBJECT-KEY TYPE-KEY: ...DATA...")
		j = index (line,': '); % find FIRST occurrence of ': ' delimiter (there may be additional ': ' delimiters in the "DATA" part of the line)
		time_keys = line(1:j-1);
		DATA{k} = line(j+2:end);
		
		% TIME:
		time_keys = __my_strsplit (time_keys,' ');
		t{k} = time_keys{1};
		
		% DATASOURCE[LABEL]:
		u = __my_strsplit (time_keys{2},'[');
		if length(u) == 1 % there was no LABEL part
			OBJ{k}   = __my_strtrim (time_keys{2});
			LABEL{k} = OBJ{k};
		else
			OBJ{k}   = __my_strtrim (u{1});
			LABEL{k} = u{2}(1:end-1);
		end	
		
		% data TYPE:
		TYPE{k}  = time_keys{3}; % type of data
		
		% read next line:
		line = fgetl (fid); k = k + 1;
				
	end % while line != -1
	
	% close the file after reading it:
	ans = fclose (fid);
	if ans == -1
		error (sprintf('ruediPy_read_datafile: could not close file %s',file))
	end % ans = fclose(...)

	t = sscanf(sprintf('%s\n',t{:}),'%f');

	% parse file data into struct object, parse data for each object type	
	X  = [];
	O  = unique (OBJ);
	NO = length (O); % number of object types in the data file
			
	for i = 1:NO % get data for each of the requested object types
		j = find (strcmp(OBJ,O{i})); % find index to lines with object-type = O{i}

	    	% try to assure Octave compatible label names:
	    	LABEL = strrep (LABEL,'--','_');
	    	LABEL = strrep (LABEL,'-','_');
	    	LABEL = strrep (LABEL,'*','_');
	    	LABEL = strrep (LABEL,'/','_');
	    	
	    	L = unique (LABEL(j)); % list of labels available for the objects of type OBJ(j)
	    	
	    	for k = 1:length(L)

	    		l = find ( index(LABEL(j),L(k)) );
	    		
				switch toupper(O{i})
					
					case 'DATAFILE'
						u = __parse_DATAFILE (TYPE(j(l)),DATA(j(l)),t(j(l)));
						FIELDTYPES{end+1} = 'DATAFILE';
						X = setfield (X,L{k},u); % add DATAFILE[LABEL-k] data
					
					case 'RGA_SRS'
						u = __parse_SRSRGA (TYPE(j(l)),DATA(j(l)),t(j(l)));
						FIELDTYPES{end+1} = 'RGA_SRS';
						X = setfield (X,L{k},u); % add SRSRGA[LABEL-k] data
						
					case 'SELECTORVALVE_VICI'
						u = __parse_SELECTORVALVE (TYPE(j(l)),DATA(j(l)),t(j(l)));
						FIELDTYPES{end+1} = 'SELECTORVALVE';
						X = setfield (X,L{k},u); % add SELECTORVALVE[LABEL-k] data
					
					case {'TEMPERATURESENSOR_MAXIM', 'TEMPERATURESENSOR_VIRTUAL'}
						u = __parse_TEMPERATURESENSOR (TYPE(j(l)),DATA(j(l)),t(j(l)));
						FIELDTYPES{end+1} = 'TEMPERATURESENSOR';
						X = setfield (X,L{k},u); % add TEMPERATURESENSOR[LABEL-k] data
					
					case {'PRESSURESENSOR_WIKA', 'PRESSURESENSOR_OMEGA', 'PRESSURESENSOR_ARDUINO', 'PRESSURESENSOR_VIRTUAL'}
						u = __parse_PRESSURESENSOR (TYPE(j(l)),DATA(j(l)),t(j(l)));
						FIELDTYPES{end+1} = 'PRESSURESENSOR';
						X = setfield (X,L{k},u); % add PRESSURESENSOR[LABEL-k] data

					case 'RUEDI_MEASURE'
						% Do nothing

					%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% OTHERWISE %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
					otherwise
						warning (sprintf('rP_read_datafile: Unknown object type %s, skipping...',O{i}))
					
				end % switch
			end % for k = ...			
		end % for i = ...

		X.file = file;
		X.fieldtypes = FIELDTYPES;

	end % for ...
end % function


%%%%%%%%%%% HELPER FUNCTIONS (DATA PARSING) %%%%%%%%%%%

function X = __parse_DATAFILE (TYPE,DATA,t) % parse DATAFILE object data
	X = [];
	T  = unique (TYPE);

	for i = 1:length(T)
		j = find (strcmp(TYPE,T{i})); % index to lines with type = T{i}
		tt = t(j); TT = TYPE(j); DD = DATA(j);
		p = [];

		% parse line by line
		switch toupper(T{i})
			
			%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% COMMENT %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
			case 'COMMENT'
				for k = 1:length(TT)
					
					% timestamp:
					p.epochtime = tt(k);
					
					% comment text:
					p.comment = __my_strtrim (DD{k}); % remove leading and trailing whitespace from s

					% append to COMMENTs:
					if k == 1 % first iteration
						X.COMMENT = p;
					else
						X.COMMENT = [ X.COMMENT p ];
					end
					
				end % for k = ...

			case 'ANALYSISTYPE'
				for k = 1:length(TT)
					
					% timestamp:
					p.epochtime = tt(k);
					
					% analysistype text:
					p.type = __my_strtrim (DD{k}); % remove leading and trailing whitespace

					% append to ANALYSISTYPEs (although there should be only one):
					if k == 1 % first iteration
						X.ANALYSISTYPE = p;
					else
						X.ANALYSISTYPE = [ X.ANALYSISTYPE p ];
					end
					
				end % for k = ...

			case 'STANDARD'
				for k = 1:length(TT)
					
					% timestamp:
					p.epochtime = tt(k);

					% split data line entries:
					u = __my_strtrim (__my_strsplit(DD{k},';')); % split fields and remove leading and trailing whitespace

					% species value:
					l = find (index(u,'species') == 1);
					if isempty(l)
						error ('rP_read_datafile: could not find ''species'' field in STANDARD data of DATAFILE object data. Aborting...')
					else
						p.species = __my_strsplit(u{l},'='){2};
					end
									
					% concentration value:
					l = find (index(u,'concentration') == 1);
					if isempty(l)
						error ('rP_read_datafile: could not find ''concentration'' field in STANDARD data of DATAFILE object data. Aborting...')
					else
						p.concentration = str2num (__my_strsplit(__my_strsplit(u{l},'='){2},' '){1});
					end

					% mz value:
					l = find (index(u,'mz') == 1);
					if isempty(l)
						error ('rP_read_datafile: could not find ''mz'' field in STANDARD data of DATAFILE object data. Aborting...')
					else
						p.mz = str2num (__my_strsplit(u{l},'='){2});
					end

					% append to STANDARD:
					if k == 1 % first iteration
						X.STANDARD = p;
					else
						X.STANDARD = [ X.STANDARD p ];
					end
					
				end % for k = ...

			case 'SAMPLENAME'
				for k = 1:length(TT)
					
					% timestamp:
					p.epochtime = tt(k);

					% sampletype text:
					p.name = __my_strtrim (DD{k}); % remove leading and trailing whitespace

					% append to SAMPLENAMEs (although there should be only one):
					if k == 1 % first iteration
						X.SAMPLENAME = p;
					else
						X.SAMPLENAME = [ X.SAMPLENAME p ];
					end
					
				end % for k = ...

			%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% OTHERWISE %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
			otherwise
				warning (sprintf('rP_read_datafile: type = %s unknown for DATAFILE object, skipping this entry...',T{i}))

		end % switch
	end % for i = ...
end % function




function X = __parse_SRSRGA (TYPE,DATA,t) % parse SRSRGA object data
	X = [];
	T  = unique (TYPE);

	for i = 1:length(T)
		j = find (strcmp(TYPE,T{i})); % index to lines with type = T{i}
		tt = t(j); TT = TYPE(j); DD = DATA(j);
		
		% parse line by line
		switch toupper(T{i})
			
			%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% PEAK %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
			case 'PEAK'
			
				a = sscanf ( sprintf('%s\n',DD{:}) ,'mz=%d ; intensity=%f %s ; detector=%s ; gate=%f %s\n' , [6,Inf] );

				for j = 1:length(tt)
							
					X.PEAK(j).epochtime      = tt(j);
					X.PEAK(j).mz             = a(1,j);
					X.PEAK(j).intensity.val  = a(2,j);
					X.PEAK(j).gate.val       = a(5,j);

					u = char([a(3,j) a(4,j) a(6,j)]);
					X.PEAK(j).intensity.unit = u(1);
					X.PEAK(j).detector       = u(2);
					X.PEAK(j).gate.unit      = u(3);
									
				end % for j = ..
								
			%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% ZERO %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
			case 'ZERO'

				a = sscanf ( sprintf('%s\n',DD{:}) ,'mz=%d ; mz-offset=%d ; intensity=%f %s ; detector=%s ; gate=%f %s\n' , [7,Inf] );

				for j = 1:length(tt)
					X.ZERO(j).epochtime      = tt(j);
					X.ZERO(j).mz             = a(1,j);
					X.ZERO(j).mz_offset      = a(2,j);
					X.ZERO(j).intensity.val  = a(3,j);
					X.ZERO(j).gate.val       = a(6,j);

					u = char([a(4,j) a(5,j) a(7,j)]);
					X.ZERO(j).intensity.unit = u(1);
					X.ZERO(j).detector       = u(2);
					X.ZERO(j).gate.unit      = u(3);
					
				end % for j = ..

			%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% PEAK_DECONV %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
			case 'PEAK_DECONV'
			
				a = sscanf ( sprintf('%s\n',DD{:}) ,'mz=%d ; intensity=%f %s ; detector=%s ; gate=%f %s\n' , [6,Inf] );

				for j = 1:length(tt)
							
					X.PEAK_DECONV(j).epochtime      = tt(j);
					X.PEAK_DECONV(j).mz             = a(1,j);
					X.PEAK_DECONV(j).intensity.val  = a(2,j);
					X.PEAK_DECONV(j).gate.val       = a(5,j);

					u = char([a(3,j) a(4,j) a(6,j)]);
					X.PEAK_DECONV(j).intensity.unit = u(1);
					X.PEAK_DECONV(j).detector       = u(2);
					X.PEAK_DECONV(j).gate.unit      = u(3);
									
				end % for j = ..
								
			%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% ZERO_DECONV %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
			case 'ZERO_DECONV'

				a = sscanf ( sprintf('%s\n',DD{:}) ,'mz=%d ; mz-offset=%d ; intensity=%f %s ; detector=%s ; gate=%f %s\n' , [7,Inf] );

				for j = 1:length(tt)
					X.ZERO_DECONV(j).epochtime      = tt(j);
					X.ZERO_DECONV(j).mz             = a(1,j);
					X.ZERO_DECONV(j).mz_offset      = a(2,j);
					X.ZERO_DECONV(j).intensity.val  = a(3,j);
					X.ZERO_DECONV(j).gate.val       = a(6,j);

					u = char([a(4,j) a(5,j) a(7,j)]);
					X.ZERO_DECONV(j).intensity.unit = u(1);
					X.ZERO_DECONV(j).detector       = u(2);
					X.ZERO_DECONV(j).gate.unit      = u(3);
					
				end % for j = ..

			%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% SCAN %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
			case 'SCAN'
			
				for k = 1:length(TT)
					
					% timestamp:
					p.epochtime = tt(k);
					
					% split data line entries:
					u = __my_strtrim (__my_strsplit(DD{k},';')); % remove leading and trailing whitespace from s
										
					% mz values:
					l = find (index(u,'mz=') == 1);
					if isempty(l)
						warning ('rP_read_datafile: could not find ''mz'' field in SCAN data of SRSRGA object data. Using mz = NA...')
						p.mz = NA;
					else
						p.mz = str2num (__my_strsplit(u{l},'='){2});
					end
					
					% intensity values:
					l = find (index(u,'intensity') == 1);
					if isempty(l)
						warning ('rP_read_datafile: could not find ''intensity'' field in SCAN data of SRSRGA object data. Using intensity.val = NA and intensity.unit = ''?''...')
						p.intensity.val = NA;
						p.intensity.unit = '?';
					else
						uu = strrep (__my_strtrim(u{l}),', ',',');
						uu = __my_strsplit ( __my_strsplit(uu,'='){2} , ' ' );						
						p.intensity.val  = str2num (uu{1});
						p.intensity.unit = __my_strtrim (uu{2});
					end

					% gate value:
					l = find (index(u,'gate') == 1);
					if isempty(l)
						warning ('rP_read_datafile: could not find ''gate'' field in SCAN data of SRSRGA object data. Using gate.val = NA and gate.unit = ''?''...')
						p.gate.val = NA;
						p.gate.unit = '?';
					else
						uu = __my_strsplit ( __my_strsplit(__my_strtrim(u{l}),'='){2} , ' ' );
						p.gate.val  = str2num (uu{1});
						p.gate.unit = __my_strtrim(uu{2});
					end
					
					% detector:
					l = find (index(u,'detector') == 1);
					if isempty(l)
						warning ('rP_read_datafile: could not find ''detector'' field in SCAN data of SRSRGA object data. Using detector = ''?''...')
						p.detector = '?';
					else
						p.detector = __my_strtrim (__my_strsplit(u{l},'='){2});
					end
					
					% append to SCANs:
					if k == 1 % first iteration
						X.SCAN = p;
					else
						X.SCAN = [ X.SCAN p ];
					end
													
				end % for k = ...


			%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% SCAN %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
			case 'DECONVOLUTION'
			
				for k = 1:length(TT)
					
					% timestamp:
					p.epochtime = tt(k);
					
					% split data line entries:
					u = __my_strtrim (__my_strsplit(DD{k},';')); % remove leading and trailing whitespace from s
					
					for kk=1:length(u)
						uu = __my_strtrim (__my_strsplit(u{kk},'='));
						switch toupper(uu{1})
							case 'TARGET_MZ'
								p.target_mz=str2num(uu{2});
							case 'TARGET_SPECIES'
								p.target_species=uu{2};
							case 'DETECTOR'
								p.detector=uu{2};
							case 'MS_EE'
								v = __my_strtrim (__my_strsplit(uu{2},' '));
								p.MS_EE.val = str2num(v{1});
								p.MS_EE.unit = v{2};
							case 'BASIS'
								b = strrep (uu{2},' ',''); # remove all spaces
								b = strrep (b,'((',''); # remove opening brackets
								b = strrep (b,'))',''); # remove closing brackets
								b = strsplit( b , '),(' ); % cannot use __my_strsplit with length(sep) > 1
								species = {}; bas = mz = val = [];
								for i = 1:length(b)
									bb = __my_strsplit(b{i},',');
									species{i} = strrep(bb{1},"'","");
									nn = (length(bb)-1)/2;
									bas = [ bas, repmat(i,1,nn)  ];
									for j = 1:nn
										mz  = [ mz , str2num(bb{2*j})   ];
										val = [ val, str2num(bb{2*j+1}) ];
									end
								end

								BAS = unique (bas);
								MZ = unique (mz);
								x = repmat (0,length(MZ),length(BAS));
								for i = 1:length(BAS) % for each basis...
									for j = 1:length(MZ) % ...check if it has an entry for any of the mz values...
										kk = find( bas == BAS(i) );
										ll = find( mz(kk) == MZ(j) );
										if any(ll)
											x(j,i) = val(kk(ll));
										end
									end % for j = ...
								end % for i = ...

								p.basis.species   = species;
								p.basis.mz  = MZ';
								p.basis.val = x;
						end % switch
					end % for kk

					% append to DECONVOLUTION entries:
					if k == 1 % first iteration
						X.DECONVOLUTION = p;
					else
						X.DECONVOLUTION = [ X.DECONVOLUTION p ];
					end

					clear p

				end


			%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% OTHERWISE %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
			otherwise
				warning (sprintf('rP_read_datafile: type = %s unknown for SRSRGA object, skipping...',T{i}))

		end % switch
	end % for i = ...

end % function



function X = __parse_SELECTORVALVE (TYPE,DATA,t) % parse SELECTORVALVE object data
	X = [];
	T  = unique (TYPE);

	for i = 1:length(T)
		j = find (strcmp(TYPE,T{i})); % index to lines with type = T{i}
		tt = t(j); TT = TYPE(j); DD = DATA(j);
		
		% parse line by line
		switch toupper(T{i})
			
			%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% POSITION %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
			case 'POSITION'
				for k = 1:length(TT)
					
					% timestamp:
					p.epochtime = tt(k);
															
					% position value:
					
					u = __my_strtrim (DD{k}); % remove leading and trailing whitespace
					p.val = str2num (u);
					
					if ~( p.val >= 0 )
						warning ('rP_read_datafile: could not parse value in POSITION data field of SELECTORVALVE object data. Using position = NA...')
						p.val = NA;
					end
																				
					% append to POSITIONs:
					if k == 1 % first iteration
						X.POSITION = p;
					else
						X.POSITION = [ X.POSITION p ];
					end
													
				end % for k = ...

			%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% OTHERWISE %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
			otherwise
				warning (sprintf('rP_read_datafile: type = %s unknown for SELECTORVALVE object, skipping...',T{i}))

		end % switch
	end % for i = ...
end % function



function X = __parse_TEMPERATURESENSOR (TYPE,DATA,t) % parse TEMPERATURESENSOR object data
	X = [];
	T  = unique (TYPE);

	for i = 1:length(T)
		j = find (strcmp(TYPE,T{i})); % index to lines with type = T{i}
		tt = t(j); TT = TYPE(j); DD = DATA(j);
		
		% parse line by line
		switch toupper(T{i})
			
			%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% TEMPERATURE %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
			case 'TEMPERATURE'
				for k = 1:length(TT)
					
					% timestamp:
					p.epochtime = tt(k);
										
					% split data line entries:
					u = __my_strtrim (__my_strsplit(DD{k},';')); % remove leading and trailing whitespace from s
															
					% temperature value + unit:
					uu = __my_strsplit(__my_strtrim(DD{k}),' ');
					p.val  = str2num (uu{1});
					p.unit = __my_strtrim(uu{2});
		
					% append to TEMPERATUREs:
					if k == 1 % first iteration
						% X.TEMPERATURE = p;
						X = p;
					else
						% X.TEMPERATURE = [ X.TEMPERATURE p ];
						X = [ X p ];
					end
													
				end % for k = ...

			%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% OTHERWISE %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
			otherwise
				warning (sprintf('rP_read_datafile: type = %s unknown for TEMPERATURESENSOR object, skipping...',T{i}))

		end % switch
	end % for i = ...
end % function



function X = __parse_PRESSURESENSOR (TYPE,DATA,t) % parse PRESSURESENSOR object data
	X = [];
	T  = unique (TYPE);

	for i = 1:length(T)
		j = find (strcmp(TYPE,T{i})); % index to lines with type = T{i}
		tt = t(j); TT = TYPE(j); DD = DATA(j);
				
		% parse line by line
		switch toupper(T{i})
			
			%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% PRESSURE %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
			case 'PRESSURE'
				for k = 1:length(TT)
					
					% timestamp:
					p.epochtime = tt(k);
										
					% split data line entries:
					u = __my_strtrim (__my_strsplit(DD{k},';')); % remove leading and trailing whitespace from s
															
					% pressure value + unit:
					uu = __my_strsplit(__my_strtrim(DD{k}),' ');
					p.val  = str2num (uu{1});
					p.unit = __my_strtrim(uu{2});
		
					% append to PRESSUREs:
					if k == 1 % first iteration
						% X.PRESSURE = p;
						X = p;
					else
						% X.PRESSURE = [ X.PRESSURE p ];
						X = [ X p ];
					end
													
				end % for k = ...

			%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% OTHERWISE %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
			otherwise
				warning (sprintf('rP_read_datafile: type = %s unknown for PRESSURESENSOR object, skipping...',T{i}))

		end % switch		
	end % for i = ...
end % function


function ss = __my_strsplit (s,sep)
% split string s at sep (could use regular strsplit instead, but this is slow)
	k = find (s == sep);
	if isempty(k)
		ss = cellstr(s);
	else
		ss = {};
		if k(1) > 1
			ss{1} = s(1:k(1)-1);
		end
		for i = 2:length(k)
			if k(i) - k(i-1) > 1
				ss{end+1} = s(k(i-1)+1:k(i)-1);
			end
		end
		if k(end) < length(s)
			ss{end+1} = s(k(end)+1:end);
		end
	end
end


function s = __my_strtrim (s)
% remove leading and trailing spaces from string s (could use regular strtrim instead, but this is slow)
	if iscellstr (s)
		for i = 1:length(s)
			s{i} = __my_strtrim (s{i});
		end
	else
		try
			while s(1) == ' ', s= s(2:end); end
			while s(end) == ' ', s= s(1:end-1); end
		end
	end
end
