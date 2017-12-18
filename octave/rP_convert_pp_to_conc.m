function C = rP_convert_pp_to_conc (P , major_pp_species , TDGP_sensor , TEMP_sensor)

% function C = rP_convert_pp_to_conc (P , major_pp_species , TDGP_sensor , TEMP_sensor)
% 
% Convert partial pressures data in P to dissolved gas concentrations. For each sample in P, do the following:
% - calculate the sum of partial pressures (pp_sum)
% - normalize all partial pressures multipling them by the ratio TDGP/pp_sum (where TDGP is the toal dissolved gas pressure as measured in the GE-MIMS module)
% - determine the Henry coefficient of each species at the water temperature measured in the GE-MIMS module)
% - apply Henry's Law to determine the the dissolved gas concentrations for each species using the normalized partial pressures and the Henry coefficients for all species
% 
% INPUT:
% P: partial pressure data (see rP_read_pp_resultsfile.m)
% major_pp_species: name of species whose partial pressures are used to determine the sum of partial pressures 
% TDGP_sensor: name of the sensor with the total dissolved gas pressure data used for normalisation of the partial pressures
% TEMP_sensor: name of the sensor with the water temperature data used for Henry coefficient in GE-MIMS module
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
% Copyright 2017, Matthias Brennwald (brennmat@gmail.com)


warning ('This function is under development -- ask a magician to fully implement it! The function is still highly experimental. Error propagation is not yet implemented at all.')

C = P;

% determine gas items in the data set:
u = fieldnames (C); itms = {};
for i = 1:length (u)
	if ~isempty (k = findstr(u{i},'_PARTIALPRESSURE'))
		itms{end+1} = u{i}(1:k-1);
	end % if
end % for

Nsmpl = length (C.SAMPLES); % number of samples in P
Nitms = length (itms); % number of gas items

% add fields for CONCENTRATIONS:
u = repmat (NaN,Nsmpl,1);
v = 'ccSTP_per_gram';
for i = 1:Nitms
	eval(sprintf('C.%s_CONCENTRATION.VAL = u;',itms{i}))
	eval(sprintf('C.%s_CONCENTRATION.ERR = u;',itms{i}))
	eval(sprintf('C.%s_CONCENTRATION.UNIT = v;',itms{i}))
	eval(sprintf('C.%s_CONCENTRATION.EPOCH = C.%s_PARTIALPRESSURE.EPOCH;',itms{i},itms{i}))
end % for

% determine index to major gas items used to determine sum of partial pressures:
kPP = repmat (NaN,size(major_pp_species));
for i = 1:length(major_pp_species)
	if ( any(k = find (strcmpi(major_pp_species{i},itms))) )
		kPP(i) = k;
	end
end % for
if any(u = find(isnan(kPP)))
	error (sprintf('rP_convert_pp_to_conc: could not find item %s in the data! Aborting...',major_pp_species{u(1)}))
end


% GE-MIMS temperature values (sensor):
TEMP = getfield (getfield(C,TEMP_sensor),'VAL');

% Total gas pressure values (sensor):
TDGP = getfield (getfield(C,TDGP_sensor),'VAL');
switch toupper(P.TOTALPRESSURE_MEMBRANE.UNIT) % convert TDGP to hPa
    case 'BAR'
    	TDGP = 1000 * TDGP;
    otherwise
    	error (sprintf('rP_convert_pp_to_conc: I do not know how to treat total gas pressures with unit %s! Aborting...',P.TOTALPRESSURE_MEMBRANE.UNIT))
end	

% Check units of partial pressures
for i = Nitms
	eval(sprintf('u = C.%s_PARTIALPRESSURE.UNIT;',itms{i}));
	if ~strcmp(u,'hPa')
    	error (sprintf('rP_convert_pp_to_conc: I do not know how to treat gas partial pressures with unit %s! Aborting...',u))
    end
end


% determine gas concenterations for each sample:
for i = 1:Nsmpl

	% determine sum of partial pressures:
	pp_sum = 0;
	for j = kPP
		eval(sprintf('pp_sum = pp_sum + C.%s_PARTIALPRESSURE.VAL(i);',itms{j}))
	end

	% normalize partial pressures to TDGP:
	for j = 1:Nitms
		eval(sprintf('C.%s_PARTIALPRESSURE.VAL(i) = TDGP(i) / pp_sum * C.%s_PARTIALPRESSURE.VAL(i);',itms{j},itms{j}))
	end





	
	% determine concentraions:
	for j = 1:Nitms
		
		% find Henry's Law coefficient:
		u = strsplit(itms{j},'_');
		
		switch toupper(u{1})
			
			case 'N2'
				[c,v,d,m,H] = nf_atmos_gas ('N2',TEMP(i),0,1013.25);
			
			case 'O2'
				[c,v,d,m,H] = nf_atmos_gas ('O2',TEMP(i),0,1013.25);

			case 'HE'
				[c,v,d,m,H] = nf_atmos_gas ('He',TEMP(i),0,1013.25);
			
			case 'NE'
				[c,v,d,m,H] = nf_atmos_gas ('Ne',TEMP(i),0,1013.25);
			
			case 'AR'
				[c,v,d,m,H] = nf_atmos_gas ('Ar',TEMP(i),0,1013.25);
			
			case 'Kr'
				[c,v,d,m,H] = nf_atmos_gas ('Kr',TEMP(i),0,1013.25);
			
			otherwise
				H = NA;
    			warning (sprintf('rP_convert_pp_to_conc: I do not know the Henry coefficient for %s. Setting to NA...',itms{j}))
    			
		end % switch
		
		eval(sprintf('C.%s_CONCENTRATION.VAL(i) = C.%s_PARTIALPRESSURE.VAL(i) / H;',itms{j},itms{j})); % Henry's Law
		
		warning ('rP_convert_pp_to_conc: NEED TO IMPLENENT ERROR PROPAGATION!!!')
		
	end
	
	
	
	
	
	
end % for i = ...

end % function
