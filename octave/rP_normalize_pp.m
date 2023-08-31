function X,Y,Z = rP_normalize_pp ( ... )

% function X,Y,Z = rP_normalize_pp ( ... )
% 
% UNDER CONSTRUCTION!!!
%
% Normalize partial pressures such that their sum corresponds to the measured total gas pressure.
%
% 
% INPUT:
% ...
% 
% OUPUT:
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
% Copyright 2023, Matthias Brennwald (brennmat@gmail.com)


warning('rP_normalize_PP: NOT YET IMPLEMENTED')











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


if ~any(kPP) % don't normalize partial pressures
	if no_normalisation_warn
		disp ('rP_convert_pp_to_conc: no species given for sum of partial pressure -- not normalizing the partial pressures to total dissolved gas pressure!')
	end

else












	% Total gas pressure values (sensor, including vapour pressure):
	warning('rP_normalize_pp: DEBUG AND CHECK IF rP_get_PRESS DOES THE RIGHT THING!')
	TDGP = rP_get_PRESS(C);












	if ~any(TDGP) % don't normalize partial pressures
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
end









	
endfunction
