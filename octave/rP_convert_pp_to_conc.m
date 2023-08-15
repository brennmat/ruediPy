function C = rP_convert_pp_to_conc (P , major_pp_species , TDGP_sensor , TEMP_sensor, write_file)

% function C = rP_convert_pp_to_conc (P , major_pp_species , TDGP_sensor , TEMP_sensor, write_file)
% 
% Convert partial pressures data in P to dissolved gas concentrations. For each sample in P, do the following:
% (1*) calculate the sum of partial pressures (pp_sum) of the species in major_pp_species (not including the water vapour pressure)
% (2*) normalize all partial pressures by multiplying them wit the TDGP/pp_sum ratio, where TDGP is the total dry-gas gas pressure (sensor value minus the the water vapour pressure)
% (3) determine the Henry coefficient of each species at the water temperature measured in the GE-MIMS module)
% (4) apply Henry's Law to determine the the dissolved gas concentrations for each species using the normalized partial pressures and the Henry coefficients for all species
%
% (*) The normalisation steps (1) and (2) are omitted if either major_pp_species or TDGP_sensor are empty (i.e., major_pp_species = {} or TDGP_sensor = '').
% 
% INPUT:
% P: partial pressure data (see rP_read_pp_resultsfile.m)
% major_pp_species: name of species whose partial pressures are used to determine the sum of partial pressures. major_pp_species = {} can be used to skip the pressure normalisation.
% TDGP_sensor: name of the sensor with the total dissolved gas pressure data used for normalisation of the partial pressures. TDGP_sensor = '' can be used to skip the pressure normalisation.
% TEMP_sensor: name of the sensor with the water temperature data used for Henry coefficient in GE-MIMS module
% write_file (optional): flag to set if the results are written to a data file (default: write_file = true):
%	write_file = true: ask user for file name on terminal / command line, create the file, and save results in this file
%	write_file = 1: same as write_file = true
%	write_file = 2: same as write_file = true, but use Zenity/GUI dialog to determine new file name
% 
% OUPUT:
% C: struct object with dissolved gas concentrations and normalised partial pressures, using the same format as X; dissolved gas concentrations are in ccSTP/g (1 Mol = 22414 ccSTP)
%
% EXAMPLE:
% P = rP_read_pp_resultsfile ( 'my_partial_pressure_data.csv' ); % load data file with partial pressures
% fieldnames (P) % show names of gas items and sensors
% C = rP_convert_pp_to_conc ( P , { 'N2_28_F' , 'O2_32_F' , 'Ar_40_40_F' } , 'TOTALPRESSURE_MEMBRANE' , 'TEMP_MEMBRANE' ); % apply conversion from partial pressures to dissolved gas concentrations
% 
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
% Copyright 2017, 2018, Matthias Brennwald (brennmat@gmail.com)


% copy struct with partial pressures to new struct that will hold the concentrations:
C = P;

% determine gas items in the data set:
u = fieldnames (C); itms = {};
for i = 1:length (u)
	if ~isempty (k = strfind(u{i},'_PARTIALPRESSURE'))
		itms{end+1} = u{i}(1:k-1);
	end % if
end % for

Nsmpl = length (C.SAMPLES); % number of samples in P
Nitms = length (itms); % number of gas items

% add fields for CONCENTRATIONS:
u = repmat (NaN,Nsmpl,1);
conc_unit = 'ccSTP_per_gram';
for i = 1:Nitms
	eval(sprintf('C.%s_CONCENTRATION.VAL = u;',itms{i}))
	eval(sprintf('C.%s_CONCENTRATION.ERR = u;',itms{i}))
	eval(sprintf('C.%s_CONCENTRATION.UNIT = conc_unit;',itms{i}))
	eval(sprintf('C.%s_CONCENTRATION.EPOCH = C.%s_PARTIALPRESSURE.EPOCH;',itms{i},itms{i}))
end % for

% determine index to major gas items used to determine sum of partial pressures:
if length(major_pp_species) == 0 % no species given for sum of partial pressures
	kPP = [];
else
	kPP = repmat (NaN,size(major_pp_species));
	for i = 1:length(major_pp_species)
		if ( any(k = find (strcmpi(major_pp_species{i},itms))) )
			kPP(i) = k;
		end
	end % for
	if any(u = find(isnan(kPP)))
		error (sprintf('rP_convert_pp_to_conc: could not find item %s in the data! Aborting...',major_pp_species{u(1)}))
	end
end

% GE-MIMS temperature values (sensor):
TEMP = getfield (getfield(C,TEMP_sensor),'VAL');
TEMP_ERR = getfield (getfield(C,TEMP_sensor),'ERR');
u = getfield (getfield(C,TEMP_sensor),'UNIT');
switch toupper(u) % check unit
    case 'DEG.C'
    	% do nothing, be happy
    otherwise
    	error (sprintf('rP_convert_pp_to_conc: I do not know how to treat temperature with unit %s! Aborting...',u))
end

% Total gas pressure values (sensor, including vapour pressure):
if strcmp (TDGP_sensor,'') % no TDGP sensor given
	TDGP = [];
else
	TDGP     = getfield (getfield(C,TDGP_sensor),'VAL');
	TDGP_ERR = getfield (getfield(C,TDGP_sensor),'ERR');
	TDGP_UNIT = getfield (getfield(C,TDGP_sensor),'UNIT');
	switch toupper(TDGP_UNIT) % deal with unit, convert to hPa if necessary
	    case 'BAR'
	    	TDGP = 1000 * TDGP;
	    	TDGP_ERR = 1000 * TDGP_ERR;
	    otherwise
		if ~strcmp(toupper(TDGP_UNIT),'HPA')
		    	error (sprintf('rP_convert_pp_to_conc: I do not know how to treat total gas pressures with unit %s! Aborting...',TDGP_UNIT))
		end
	end
	for i = Nitms % Check units of partial pressures
		eval(sprintf('u = C.%s_PARTIALPRESSURE.UNIT;',itms{i}));
		if ~strcmp(u,'hPa')
	    		error (sprintf('rP_convert_pp_to_conc: I do not know how to treat gas partial pressures with unit %s! Aborting...',u))
	        end
	end
end

% determine gas concenterations for each sample:
unknown_henry_warn = true;
no_normalisation_warn = true;

for i = 1:Nsmpl

	if ~any(kPP) % don't normalize partial pressures
		if no_normalisation_warn
			disp ('rP_convert_pp_to_conc: no species given for sum of partial pressure -- not normalizing the partial pressures to total dissolved gas pressure!')
		end
		no_normalisation_warn = false;

	elseif ~any(TDGP) % don't normalize partial pressures
		if no_normalisation_warn
			disp ('rP_convert_pp_to_conc: no total dissolved gas pressure given -- not normalizing the partial pressures to total dissolved gas pressure!')
		end
		no_normalisation_warn = false;

	else % determine sum of partial pressures (using the 'major' items as given at input), then normalise partial pressures:
		pp_sum =     0;
		pp_sum_err = 0;

		for j = kPP
			eval(sprintf('pp_sum = pp_sum + C.%s_PARTIALPRESSURE.VAL(i);',itms{j}))
			eval(sprintf('pp_sum_err = pp_sum_err + C.%s_PARTIALPRESSURE.ERR(i)^2;',itms{j}))
		end
		pp_sum_err = sqrt (pp_sum_err);

		% subtract water vapour pressure from TDGP (need dry-gas TDGP for normalisation):
		pWater     = 1013.25 * exp(24.4543-67.4509*100/(TEMP(i)+273.15)-4.8489.*log((TEMP(i)+273.15)/100));  % water vapour pressure (in hPa)
		pWater_err = 1013.25 * exp(24.4543-67.4509*100/(TEMP(i)+TEMP_ERR(i)+273.15)-4.8489.*log((TEMP(i)+TEMP_ERR(i)+273.15)/100)); pWater_err = abs (pWater_err - pWater);		
		TDGP(i) = TDGP(i) - pWater;
		TDGP_ERR(i) = sqrt ( TDGP_ERR(i)^2 + pWater_err^2 );		

		% normalize partial pressures to TDGP (note: TDGP relates to dry gas now!):
		for j = 1:Nitms
			eval(sprintf('pnew     = TDGP(i) / pp_sum * C.%s_PARTIALPRESSURE.VAL(i);',itms{j}));
			eval(sprintf('pnew_err = sqrt ( (C.%s_PARTIALPRESSURE.ERR(i)/C.%s_PARTIALPRESSURE.VAL(i))^2 + (pp_sum_err/pp_sum)^2 + (TDGP_ERR(i)/TDGP(i))^2 );',itms{j},itms{j})); % relative error
			pnew_err = pnew * pnew_err; % convert relative error to absolute error
			eval(sprintf('C.%s_PARTIALPRESSURE.VAL(i) = pnew;',itms{j}))
			eval(sprintf('C.%s_PARTIALPRESSURE.ERR(i) = pnew_err;',itms{j}))
		end
	end


	% apply Henry's Law to determine concentraions:
	for j = 1:Nitms
		
		% find Henry's Law coefficient:
		u = strsplit(itms{j},'_');
		
		switch toupper(u{1})
			
			case 'N2'
				[c,v,d,m,H] = rP_atmos_gas ('N2',TEMP(i),0,1013.25);
				[c,v,d,m,dH] = rP_atmos_gas ('N2',TEMP(i)+TEMP_ERR(i),0,1013.25); dH = abs (dH-H);
							
			case 'O2'
				[c,v,d,m,H] = rP_atmos_gas ('O2',TEMP(i),0,1013.25);
				[c,v,d,m,dH] = rP_atmos_gas ('O2',TEMP(i)+TEMP_ERR(i),0,1013.25); dH = abs (dH-H);

			case 'HE'
				[c,v,d,m,H] = rP_atmos_gas ('He',TEMP(i),0,1013.25);
				[c,v,d,m,dH] = rP_atmos_gas ('He',TEMP(i)+TEMP_ERR(i),0,1013.25); dH = abs (dH-H);
			
			case 'NE'
				[c,v,d,m,H] = rP_atmos_gas ('Ne',TEMP(i),0,1013.25);
				[c,v,d,m,dH] = rP_atmos_gas ('Ne',TEMP(i)+TEMP_ERR(i),0,1013.25); dH = abs (dH-H);
			
			case 'AR'
				[c,v,d,m,H] = rP_atmos_gas ('Ar',TEMP(i),0,1013.25);
				[c,v,d,m,dH] = rP_atmos_gas ('Ar',TEMP(i)+TEMP_ERR(i),0,1013.25); dH = abs (dH-H);
			
			case 'KR'
				[c,v,d,m,H] = rP_atmos_gas ('Kr',TEMP(i),0,1013.25);
				[c,v,d,m,dH] = rP_atmos_gas ('Kr',TEMP(i)+TEMP_ERR(i),0,1013.25); dH = abs (dH-H);
			
			case 'XE'
				[c,v,d,m,H] = rP_atmos_gas ('Xe',TEMP(i),0,1013.25);
				[c,v,d,m,dH] = rP_atmos_gas ('Xe',TEMP(i)+TEMP_ERR(i),0,1013.25); dH = abs (dH-H);
			
			case 'CH4'
				[c,v,d,m,H] = rP_atmos_gas ('CH4',TEMP(i),0,1013.25);
				[c,v,d,m,dH] = rP_atmos_gas ('CH4',TEMP(i)+TEMP_ERR(i),0,1013.25); dH = abs (dH-H);

			case 'CO2'
				[c,v,d,m,H] = rP_atmos_gas ('CO2',TEMP(i),0,1013.25);
				[c,v,d,m,dH] = rP_atmos_gas ('CO2',TEMP(i)+TEMP_ERR(i),0,1013.25); dH = abs (dH-H);
				warning ('rP_convert_pp_to_conc: Henry coefficient for CO2 relates to DISSOLVED CO2 only!!! Chemical partitioning of CO2 with other species is not taken into account!!!')

			case 'C3H8' % propane
 				[c,v,d,m,H] = rP_atmos_gas ('C3H8',TEMP(i),0,1013.25);
 				[c,v,d,m,dH] = rP_atmos_gas ('C3H8',TEMP(i)+TEMP_ERR(i),0,1013.25); dH = abs (dH-H);

			otherwise
				H = NA;
				if unknown_henry_warn
	    			warning (sprintf('rP_convert_pp_to_conc: Henry coefficient for %s is unknown. Setting %s concentration to NA...',itms{j},itms{j}))
				end
				unknown_henry_warn = false;
    			
		end % switch
		
		eval (sprintf('pp     = C.%s_PARTIALPRESSURE.VAL(i);',itms{j}));
		eval (sprintf('pp_err = C.%s_PARTIALPRESSURE.ERR(i);',itms{j}));
		cc     = pp / H;
		cc_err = sqrt ( ( pp / (H+dH) - cc )^2 + ( pp_err / pp * cc )^2 );
		
		eval(sprintf('C.%s_CONCENTRATION.VAL(i) = cc;'     ,itms{j},itms{j}));
		eval(sprintf('C.%s_CONCENTRATION.ERR(i) = cc_err;' ,itms{j},itms{j}));
				
	end
	
end % for i = ...

warning ( 'on' , 'noblefit:atmos_gas_implementation' )


% write data to file:

if ~exist ('write_file','var')
	write_file = true;
end

if write_file	% write results to file:

	if write_file == true
		write_file = 1;
	end
	if ischar (write_file)
		write_file = str2num (write_file);
	end

	use_zenity = ( write_file == 2);
	name = rP_get_output_filename (use_zenity,'Data file for concentraion data','CSV');

	if isempty(name)
	    disp ('rP_convert_pp_to_conc: no file name given, not writing data to file.')
	
	else
	
		% prepare things:
		species = {};	
		for i = 1:Nitms
			u = strsplit (itms{i},'_');
			if length(u) > 3
				u{1} = sprintf('%s-%s',u{1},u{2});
				u{2} = u{3};
				u{3} = u{4};
			end
			species{i} = sprintf('%s (%s_%s)',u{1},u{2},u{3});
		end

		% open ASCII file for writing:
		name = strrep(name,"\n",""); % just in case: remove newlines
		[p,n,e] = fileparts (name);
		e = tolower(e);
		if ~strcmp(e,'.csv')
			warntext = 'rP_convert_pp_to_conc: saving CSV file without CSV file extension!';
			switch write_file
				case 2
					system (sprintf("zenity --warning --width=300 --height=150 --text \"%s\"",warntext));
				otherwise
					warning (warntext)
			end
		end

		[fid,msg] = fopen (name, 'wt');
		if fid == -1
			error (sprintf('rP_convert_pp_to_conc: could not open file for writing (%s).',msg))
		else    
	    	disp (sprintf('Writing data to %s...',name))
	    	
	    	% write header:
	    	fprintf (fid,'SAMPLE')    	
	    	for j = 1:length(species)
	    		fprintf (fid,';%s TIME (EPOCH);%s CONCENTRATION (%s);%s CONCENTRATION ERR (%s)',species{j},species{j},conc_unit,species{j},conc_unit)
	    	end	
			
			% write data values:
			for i = 1:Nsmpl
				fprintf (fid,'\n'); % start new line
				
				% sample name:
				fprintf (fid,'"%s"',C.SAMPLES{i});
				
				% gas concentrations pressures:
				for j = 1:Nitms				
					u = getfield(C,sprintf('%s_CONCENTRATION',itms{j}));
					fprintf (fid,';%.2f;%g;%g',u.EPOCH(i),u.VAL(i),u.ERR(i))
				end % for j = ...
			end % for i = ...
	
			% done writing the file, close file: 
	    	fclose (fid);
	    	
	    	disp ('...done.')
	
	    end % if fid == -1
	end % if isempty(name)
end % if ~no_file

end % function
