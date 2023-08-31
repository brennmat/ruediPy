function TEMP = rP_get_PRESS ( ... )

% function TEMP = rP_get_PRESS ( ... )
% 
% UNDER CONSTRUCTION!!!
%
% Extract pressure sensor data from processed data (output from rP_calibrate_batch output).
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


warning('rP_get_PRESS: NOT YET IMPLEMENTED')

% Pressure sensor values:


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
