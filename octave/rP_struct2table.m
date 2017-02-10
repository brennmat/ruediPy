function [val,epochtime,unit] = rP_struct2table (s)

% function [val,epochtime,unit] = rP_struct2table (s)
% 
% Convert object data in a ruediPy struct to vector data:
%		s(1:end).epochtime ---> epochtime
% 		s(1:end).val       ---> val
%		s(1:end).unit	   ---> unit
% 
% INPUT:
% s: ruediPy struct (fieldnames: epochtime, val, unit)
% 
% OUPUT:
% val: vector with data values
% epochtime: vector with epoch time stamps 
% unit: cell string with unit
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

N = length (s);

val = epochtime = repmat (NaN,N,1);
unit = cellstr (repmat('?',N,1));

for i = 1:N
	val(i)       = s(i).val;	
	epochtime(i) = s(i).epochtime;
	unit(i)      = s(i).unit;	
end