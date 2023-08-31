function TEMP = rP_get_TEMP ( ... )

% function TEMP = rP_get_TEMP ( ... )
% 
% UNDER CONSTRUCTION!!!
%
% Extract temperature sensor data from processed data (output from rP_calibrate_batch output).
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


warning('rP_get_TEMP: NOT YET IMPLEMENTED')

% Temperature sensor values:
TEMP = getfield (getfield(C,TEMP_sensor),'VAL');
TEMP_ERR = getfield (getfield(C,TEMP_sensor),'ERR');
u = getfield (getfield(C,TEMP_sensor),'UNIT');
switch toupper(u) % check unit
    case 'DEG.C'
    	% do nothing, be happy
    otherwise
    	error (sprintf('rP_convert_pp_to_conc: I do not know how to treat temperature with unit %s! Aborting...',u))
end

