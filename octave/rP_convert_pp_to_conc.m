function C = rP_convert_pp_to_conc (...)

% function C = rP_convert_pp_to_conc (P , major_pp_species , TDGP_sensor )
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
% 
% OUPUT:
% C: struct object with dissolved gas concentrations, using the same format as X, but with partial pressures replaced by dissolved gas concentrations in ccSTP/g (1 Mol = 22414 ccSTP)
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


warning ('This function is under development -- ask a magician to fully implement it!')


end % function
